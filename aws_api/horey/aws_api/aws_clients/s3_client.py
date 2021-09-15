"""
AWS s3 client to handle s3 service API requests.
"""
import datetime
import os
import pdb

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.s3_bucket import S3Bucket
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount

logger = get_logger()


class AsyncUploadController:
    def __init__(self):
        self.dict_keys = None


class MultiPartUploadController:
    def __init__(self):
        self.file_size_multipart_limit = 100 * 1024 * 1024
        self._chunk_size = 5 * 1024 * 1024

    @property
    def chunk_size(self):
        return self._chunk_size

    @chunk_size.setter
    def chunk_size(self, value):
        if value < 5 * 1024 * 1024 :
            raise ValueError("Minimal chunk size is 5MB")
        self._chunk_size = value


class S3Client(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "s3"
        super().__init__(client_name)

    def yield_bucket_objects(self, obj):
        """
        Yield over specific bucket keys in order to handle OOM issue.
        :param obj:
        :return:
        """

        try:
            start_after = ""
            while start_after is not None:
                counter = 0
                for object_info in self.execute(self.client.list_objects_v2, "Contents",
                                                filters_req={"Bucket": obj.name, "StartAfter": start_after}):
                    counter += 1
                    bucket_object = S3Bucket.BucketObject(object_info)
                    yield bucket_object

                start_after = bucket_object.key if counter == 1000 else None

        except Exception as inst:
            if "AccessDenied" in repr(inst):
                print(f"Init bucket full information failed {obj.name}: {repr(inst)}")
            else:
                raise

    def get_all_buckets(self, full_information=True):
        """
        Get all S3 buckets - if full_information set fetches all bucket keys' information.
        :param full_information:
        :return:
        """
        final_result = list()
        all_buckets = list(self.execute(self.client.list_buckets, "Buckets"))
        len_all_buckets = len(all_buckets)

        for i in range(len_all_buckets):
            response = all_buckets[i]
            obj = S3Bucket(response)

            print(f"Init bucket {obj.name}:  {i}/{len_all_buckets}")

            final_result.append(obj)

            if full_information:
                try:
                    update_info = list(
                        self.execute(self.client.get_bucket_acl, "Grants", filters_req={"Bucket": obj.name}))
                    obj.update_acl(update_info)

                    location_info = list(self.execute(self.client.get_bucket_location, "LocationConstraint",
                                                      filters_req={"Bucket": obj.name}))
                    obj.update_location(location_info)

                    # Dangerous - must be at the end - throwable
                    update_info = list(
                        self.execute(self.client.get_bucket_website, "Grants", filters_req={"Bucket": obj.name},
                                     raw_data=True))
                    obj.update_website(update_info)
                except Exception as inst:
                    if "NoSuchWebsiteConfiguration" in repr(inst):
                        pass
                    elif "AccessDenied" in repr(inst):
                        logger.error(f"Init bucket full information failed {obj.name}: {repr(inst)}")
                    elif "IllegalLocationConstraintException" in repr(inst):
                        logger.error(f"Init bucket full information failed {obj.name}: {repr(inst)}")
                    else:
                        raise

                try:
                    for update_info in self.execute(self.client.get_bucket_policy, "Policy",
                                                    filters_req={"Bucket": obj.name}):
                        obj.update_policy(update_info)
                except Exception as inst:
                    if "NoSuchBucketPolicy" in repr(inst):
                        pass
                    elif "AccessDenied" in repr(inst):
                        print(f"Init bucket full information failed {obj.name}: {repr(inst)}")
                    else:
                        raise

        return final_result

    def upload(self, bucket_name, src_object_path, dst_root_key, keep_src_object_name=True):
        """

        @param bucket_name: S3 bucket name.
        @param src_object_path: File or directory path
        @param dst_root_key: Bucket key name - root of the copied tree.
        @param keep_src_object_name: If True: src_object base name preserved.
        @return: None
        """

        logger.info(f"Uploading '{src_object_path}' to S3 bucket '{bucket_name}'")

        key_name = dst_root_key if not keep_src_object_name else f"{dst_root_key}/{os.path.basename(src_object_path)}"
        key_name = key_name.strip("/")
        if os.path.isdir(src_object_path):
            return self.upload_directory(bucket_name, src_object_path, key_name)

        if key_name == "":
            raise ValueError("key_name is not set while keep_src_object_name is set to False")

        return self.upload_file(bucket_name, src_object_path, key_name)

    def upload_file(self, bucket_name, file_path, key_name, multipart_upload_controller=None):
        """
        Uploads a file to S3 bucket.
        File name is not preserved.
        File can be binary.
        If file larger then file_size_multipart_limit bytes the file is being split to multipart upload.
        According to AWS recommendation in https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html:
        In general, when your object size reaches 100 MB, you should consider using multipart uploads
        instead of uploading the object in a single operation.

        @param bucket_name: S3 bucket name.
        @param file_path: File
        @param key_name:
        @return:
        """

        if multipart_upload_controller is None:
            multipart_upload_controller = MultiPartUploadController()

        file_size = os.path.getsize(file_path)
        if file_size > multipart_upload_controller.file_size_multipart_limit:
            return self.multipart_upload_file(bucket_name, file_path, key_name, multipart_upload_controller)

        with open(file_path, "rb") as file_handler:
            file_data = file_handler.read()

        filters_req = {"Bucket": bucket_name, "Key": key_name, "Body": file_data}
        for response in self.execute(self.client.put_object, None, filters_req=filters_req, raw_data=True):
            return response

    def multipart_upload_file(self, bucket_name, file_path, key_name, multipart_upload_controller):
        """
        S3 limitation:
        Part number of part being uploaded. This is a positive integer between 1 and 10,000.

        @param bucket_name:
        @param file_path:
        @param key_name:
        @param multipart_upload_controller:
        @return:
        """

        if os.path.getsize(file_path) / multipart_upload_controller.chunk_size >= 100000:
            raise ValueError("Can not split file to more then 10000 parts")

        filters_req = {"Bucket": bucket_name,
                       "Key": key_name
                       }
        multipart_upload_ids = list(
            self.execute(self.client.create_multipart_upload, "UploadId", filters_req=filters_req))

        if len(multipart_upload_ids) != 1:
            raise ValueError(f"Was not able to create multipart upload with params {filters_req}. "
                             f"len(multipart_upload) = {len(multipart_upload_ids)} != 1")

        upload_id = multipart_upload_ids[0]

        part_number = 1
        parts = []
        with open(file_path, "rb") as file_handler:
            # todo:
            #file_handler.seek()
            while byte_chunk := file_handler.read(multipart_upload_controller.chunk_size):
                start_time = datetime.datetime.now()
                logger.info(f"Uploading {len(byte_chunk)} bytes part {part_number}")
                filters_req = {"Bucket": bucket_name,
                               "Body": byte_chunk,
                               "UploadId": upload_id,
                               "PartNumber": part_number,
                               "Key": key_name
                               }
                for part_response in self.execute(self.client.upload_part, None, raw_data=True,
                                                  filters_req=filters_req):
                    parts.append({
                        'ETag': part_response["ETag"],
                        'PartNumber': part_number
                    })

                end_time = datetime.datetime.now()
                logger.info(f"Uploaded {len(byte_chunk)} bytes part {part_number}: took {end_time-start_time}")

                part_number += 1
                print(f"part: {part_number}")

        filters_req = {"Bucket": bucket_name,
                       "Key": key_name,
                       "UploadId": upload_id,
                       "MultipartUpload": {
                           'Parts': parts
                       }}

        finished_uploads = list(
            self.execute(self.client.complete_multipart_upload, None, raw_data=True, filters_req=filters_req))

        if len(finished_uploads) != 1:
            raise ValueError(f"Was not able to finish multipart upload with params {filters_req}. "
                             f"len(finished_uploads) = {len(finished_uploads)} != 1")

    def upload_directory(self, bucket_name, src_data_path, dst_root_key):
        """
        Recursively uploads directory contents.
        Keeps its tree structure.
        Directory's name is not preserved.

        @param bucket_name: S3 bucket name
        @param src_data_path: Directory to upload from
        @param dst_root_key: This is the root key used for files and subdirectories path compilation.
        @return: None
        """

        for src_object_name in os.listdir(src_data_path):
            src_object_full_path = os.path.join(src_data_path, src_object_name)
            new_dst_root_key = f"{dst_root_key}/{src_object_name}"
            new_dst_root_key = new_dst_root_key.strip("/")
            self.upload(bucket_name, src_object_full_path, new_dst_root_key, keep_src_object_name=False)

    def provision_bucket(self, bucket):
        filters_req = {"Bucket": bucket.name}
        AWSAccount.set_aws_region(bucket.region)
        try:
            for bucket_region_mark in self.execute(self.client.get_bucket_location, "LocationConstraint",
                                                   filters_req=filters_req):
                if bucket.region.region_mark != bucket_region_mark:
                    raise RuntimeError(f"Provisioning bucket {bucket.name} in '{bucket.region.region_mark}' fails. "
                                       f"Exists in region '{bucket_region_mark}'")
        except Exception as exception_instance:
            repr_exception_instance = repr(exception_instance)
            logger.info(repr_exception_instance)
            if "NoSuchBucket" not in repr_exception_instance:
                raise

            response = self.provision_bucket_raw(bucket.generate_create_request())
            bucket.location = response

        if bucket.policy is not None:
            self.put_bucket_policy_raw(bucket.generate_put_bucket_policy_request())

    def provision_bucket_raw(self, request_dict):
        for response in self.execute(self.client.create_bucket, "Location", filters_req=request_dict):
            return response

    def put_bucket_policy_raw(self, request_dict):
        for response in self.execute(self.client.put_bucket_policy, "ResponseMetadata", filters_req=request_dict):
            return response

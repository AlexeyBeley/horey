"""
AWS s3 client to handle s3 service API requests.
"""
import pdb

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.s3_bucket import S3Bucket
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
logger = get_logger()


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
                for object_info in self.execute(self.client.list_objects_v2, "Contents", filters_req={"Bucket": obj.name, "StartAfter": start_after}):
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
                    update_info = list(self.execute(self.client.get_bucket_acl, "Grants", filters_req={"Bucket": obj.name}))
                    obj.update_acl(update_info)

                    location_info = list(self.execute(self.client.get_bucket_location, "LocationConstraint", filters_req={"Bucket": obj.name}))
                    obj.update_location(location_info)

                    # Dangerous - must be at the end - throwable
                    update_info = list(self.execute(self.client.get_bucket_website, "Grants", filters_req={"Bucket": obj.name}, raw_data=True))
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
                    for update_info in self.execute(self.client.get_bucket_policy, "Policy", filters_req={"Bucket": obj.name}):
                        obj.update_policy(update_info)
                except Exception as inst:
                    if "NoSuchBucketPolicy" in repr(inst):
                        pass
                    elif "AccessDenied" in repr(inst):
                        print(f"Init bucket full information failed {obj.name}: {repr(inst)}")
                    else:
                        raise

        return final_result

    def upload_to_s3(self, dir_to_upload, bucket_name):
        """
        Uploads directory or file to s3 bucket name- saves the same folders tree.

        for root, dirs, files in os.walk(dir_to_upload):
            print(root)
            for file in files:
                aws_api.s3_client.client.upload_file(os.path.join(root, file), bucket_name, os.path.join(root, file))
        return
        :param dir_to_upload:
        :param bucket_name:
        :return:
        """
        raise NotImplementedError()

    def provision_bucket(self, bucket):
        filters_req = {"Bucket": bucket.name}
        AWSAccount.set_aws_region(bucket.region)
        try:
            for bucket_region_mark in self.execute(self.client.get_bucket_location, "LocationConstraint", filters_req=filters_req):
                if bucket.region.region_mark != bucket_region_mark:
                    raise RuntimeError(f"Provisioning bucket {bucket.name} in '{bucket.region.region_mark}' fails. "
                                       f"Exists in region '{bucket_region_mark}'")
                return
        except Exception as exception_instance:
            repr_exception_instance = repr(exception_instance)
            logger.info(repr_exception_instance)
            if "NoSuchBucket" not in repr_exception_instance:
                raise

        response = self.provision_bucket_raw(bucket.generate_create_request())
        bucket.location = response

    def provision_bucket_raw(self, request_dict):
        for response in self.execute(self.client.create_bucket, "Location", filters_req=request_dict):
            return response

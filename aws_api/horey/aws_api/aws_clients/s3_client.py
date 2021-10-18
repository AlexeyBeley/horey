"""
AWS s3 client to handle s3 service API requests.
"""
import datetime
import os
import pdb
import base64
import hashlib

import time

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.s3_bucket import S3Bucket
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from concurrent.futures import ThreadPoolExecutor
import threading
from enum import Enum
import traceback

logger = get_logger()


class UploadTask:
    def __init__(self, task_id, task_type, file_path, bucket_name, key_name, extra_args=None):
        self.id = task_id
        self.task_type = task_type
        self.file_path = file_path
        self.offset_index = None
        self.offset_length = None
        self.key_name = key_name
        self.bucket_name = bucket_name
        self.start_time = None
        self.started = False
        self.finished = False
        self.upload_id = None
        self.extra_args = extra_args
        self.attempts = []
        self.thread_pool_executor_future = None

    class Type(Enum):
        FILE = 0
        PART = 1


class TasksQueue:
    TASKS_DICT = dict()

    def __init__(self, max_queue_size):
        self._max_queue_size = max_queue_size

    @property
    def max_queue_size(self):
        return self._max_queue_size

    @max_queue_size.setter
    def max_queue_size(self, value):
        self._max_queue_size = value

    def put(self, task):
        if len(TasksQueue.TASKS_DICT) >= self.max_queue_size:
            raise self.FullQueueError()
        TasksQueue.TASKS_DICT[task.id] = task

    def empty(self):
        return len(TasksQueue.TASKS_DICT) == 0

    def remove(self, task):
        del TasksQueue.TASKS_DICT[task.id]

    def prune_finished(self):
        finished_tasks = []
        keys = list(self.TASKS_DICT)[:]
        for key in keys:
            task = self.TASKS_DICT.get(key)
            if task is None:
                continue

            if task.finished:
                if task.succeed:
                    finished_tasks.append(task)
                    continue

                task.finished = False
                task.started = False
            elif task.thread_pool_executor_future is not None:
                ret = task.thread_pool_executor_future.exception()
                if ret is not None:
                    raise self.TaskThreadError(f"Thread failed with error: {repr(ret)}").with_traceback(ret.__traceback__)

        for task in finished_tasks:
            del self.TASKS_DICT[task.id]

        return finished_tasks

    def get_next_ready(self):
        keys = list(self.TASKS_DICT)[:]
        for key in keys:
            task = self.TASKS_DICT.get(key)
            if task is None:
                continue
            if not task.started:
                return task

    class FullQueueError(RuntimeError):
        pass

    class TaskThreadError(RuntimeError):
        pass


class S3Client(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """
    TASKS_QUEUE = None
    THREAD_POOL_EXECUTOR = None

    def __init__(self):
        client_name = "s3"
        super().__init__(client_name)
        self._multipart_chunk_size = 8 * 1024 * 1024
        self._max_queue_size = 1000
        self._multipart_threshold = 50 * 1024 * 1024
        self._max_concurrent_requests = 70
        self.finished_uploading_flow = False
        self.multipart_uploads = dict()
        self._tasks_manager_thread_keepalive = None
        self._tasks_manager_thread_progress_time_limit = datetime.timedelta(minutes=20)
        self._md5_validate = False

    @property
    def md5_validate(self):
        return self._md5_validate

    @md5_validate.setter
    def md5_validate(self, value):
        self._md5_validate = value

    @property
    def multipart_chunk_size(self):
        return self._multipart_chunk_size

    @multipart_chunk_size.setter
    def multipart_chunk_size(self, value):
        self.validate_int(value, min_value=5 * 1024 * 1024)
        self._multipart_chunk_size = value

    @property
    def max_queue_size(self):
        return self._max_queue_size

    @max_queue_size.setter
    def max_queue_size(self, value):
        self.validate_int(value)
        self._max_queue_size = value

        if S3Client.TASKS_QUEUE.max_queue_size == value:
            return

        S3Client.TASKS_QUEUE.max_queue_size = value

    @property
    def tasks_queue(self):
        if S3Client.TASKS_QUEUE is None:
            S3Client.TASKS_QUEUE = TasksQueue(self.max_queue_size)

        return S3Client.TASKS_QUEUE

    @property
    def thread_pool_executor(self):
        if S3Client.THREAD_POOL_EXECUTOR is None:
            S3Client.THREAD_POOL_EXECUTOR = ThreadPoolExecutor(max_workers=self.max_concurrent_requests)
        return S3Client.THREAD_POOL_EXECUTOR

    @property
    def multipart_threshold(self):
        return self._multipart_threshold

    @multipart_threshold.setter
    def multipart_threshold(self, value):
        self.validate_int(value)
        self._multipart_threshold = value

    @property
    def max_concurrent_requests(self):
        return self._max_concurrent_requests

    @max_concurrent_requests.setter
    def max_concurrent_requests(self, value):
        self.validate_int(value)
        self._max_concurrent_requests = value

        if S3Client.THREAD_POOL_EXECUTOR is not None:
            raise RuntimeError("Can not change max_concurrent_requests for running executor")

    @staticmethod
    def validate_int(value, min_value=1, max_value=None):
        if not isinstance(value, int):
            raise ValueError(f"{value} is not int")

        if value < min_value:
            raise ValueError(f"{value} < {min_value}")

        if max_value is not None:
            if value > max_value:
                raise ValueError(f"{value} > {max_value}")

    def yield_bucket_objects(self, bucket):
        """
        Yield over specific bucket keys in order to handle OOM issue.
        :param bucket:
        :return:
        """
        max_keys = 1000
        try:
            start_after = ""
            while start_after is not None:
                counter = 0
                for object_info in self.execute(self.client.list_objects_v2, "Contents",
                                                filters_req={"Bucket": bucket.name, "StartAfter": start_after, "MaxKeys": max_keys}):
                    counter += 1
                    bucket_object = S3Bucket.BucketObject(object_info)
                    yield bucket_object

                start_after = bucket_object.key if counter == max_keys else None

        except Exception as inst:
            if "AccessDenied" in repr(inst):
                print(f"Init bucket full information failed {bucket.name}: {repr(inst)}")
            else:
                raise

    def get_all_buckets(self, full_information=True):
        """
        Get all S3 buckets - if full_information set fetches all bucket keys' information.

        :param full_information: Extended bucket information
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

    def upload(self, bucket_name, src_object_path, dst_root_key, keep_src_object_name=True, extra_args=None):
        """
        Upload file or directory tree to s3 bucket.
        extra_args values
        https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html#the-extraargs-parameter
        https://boto3.amazonaws.com/v1/documentation/api/1.9.42/guide/s3.html
        ALLOWED_UPLOAD_ARGS = ['ACL', 'CacheControl', 'ContentDisposition', 'ContentEncoding', 'ContentLanguage',
         'ContentType', 'Expires', 'GrantFullControl', 'GrantRead', 'GrantReadACP', 'GrantWriteACP', 'Metadata',
          'RequestPayer', 'ServerSideEncryption', 'StorageClass', 'SSECustomerAlgorithm', 'SSECustomerKey',
           'SSECustomerKeyMD5', 'SSEKMSKeyId', 'WebsiteRedirectLocation']

        @param bucket_name: S3 bucket name.
        @param src_object_path: File or directory path
        @param dst_root_key: Bucket key name - root of the copied tree.
        @param keep_src_object_name: If True: src_object base name preserved.
        @return: None
        """
        start_time = datetime.datetime.now()

        self.finished_uploading_flow = False
        self._tasks_manager_thread_keepalive = datetime.datetime.now()

        thread = threading.Thread(target=self.start_tasks_manager_thread)
        thread.start()

        self.start_uploading_object(bucket_name, src_object_path, dst_root_key,
                                    keep_src_object_name=keep_src_object_name, extra_args=extra_args)
        self.finished_uploading_flow = True

        sleep_time = 0.5

        while not self.tasks_queue.empty():
            if self._tasks_manager_thread_keepalive is None:
                raise RuntimeError("Tasks manager thread is dead")

            if self._tasks_manager_thread_keepalive + self._tasks_manager_thread_progress_time_limit < datetime.datetime.now():
                raise TimeoutError(f"Tasks manager thread was not updated for {self._tasks_manager_thread_progress_time_limit}")

            logger.info(f"Main thread waiting for all tasks to finish. Going to sleep for {sleep_time}")
            time.sleep(sleep_time)

        end_time = datetime.datetime.now()
        logger.info(f"Upload with args {bucket_name, src_object_path, dst_root_key, keep_src_object_name} "
                    f"finished in {end_time - start_time}")

    def start_uploading_object(self, bucket_name, src_object_path, dst_root_key, keep_src_object_name=True, extra_args=None):
        """
        Start the flow of uploading local object - file or folder.

        @param bucket_name: S3 dst bucket name
        @param src_object_path: Local object path
        @param dst_root_key: Root of the s3 keys tree.
        @param keep_src_object_name: Keep the object name /overwrite with the dst_root_key
        @return:
        """
        logger.info(f"Uploading '{src_object_path}' to S3 bucket '{bucket_name}'")

        key_name = dst_root_key if not keep_src_object_name else f"{dst_root_key}/{os.path.basename(src_object_path)}"
        key_name = key_name.strip("/")
        if os.path.isdir(src_object_path):
            return self.upload_directory(bucket_name, src_object_path, key_name, extra_args=extra_args)

        if not os.path.exists(src_object_path):
            raise ValueError(f"Local object does not exist {src_object_path}")

        if key_name == "":
            raise ValueError("key_name is not set while keep_src_object_name is set to False")

        self.start_uploading_file_task(bucket_name, src_object_path, key_name, extra_args=extra_args)

    def start_tasks_manager_thread(self):
        """
        Start the thread manages tasks:
        * Runs new tasks
        * Reruns failed tasks
        * Removes successful tasks

        @return:
        """
        progress_time_limit = datetime.datetime.now() + self._tasks_manager_thread_progress_time_limit

        for counter in range(60):
            if not self.tasks_queue.empty():
                break
            logger.info(f"Tasks manager thread waiting for first tasks in tasks queue to start running")
            time.sleep(0.5)
        else:
            raise TimeoutError()
        while not self.tasks_queue.empty() or not self.finished_uploading_flow:
            self._tasks_manager_thread_keepalive = datetime.datetime.now()

            try:
                finished_tasks = self.tasks_queue.prune_finished()
            except self.tasks_queue.TaskThreadError:
                self._tasks_manager_thread_keepalive = None
                self.finished_uploading_flow = True
                raise

            logger.info(f"Finished {len(finished_tasks)} tasks")
            self.finish_multipart_uploads(finished_tasks)

            task = self.tasks_queue.get_next_ready()

            if task is None:
                if datetime.datetime.now() > progress_time_limit:
                    self._tasks_manager_thread_keepalive = None
                    raise TimeoutError(f"tasks_manager_thread can not fetch ready task for"
                                       f" {self._tasks_manager_thread_progress_time_limit}")
                logger.info(f"Tasks manager thread waiting for tasks in tasks queue")

            progress_time_limit = datetime.datetime.now() + self._tasks_manager_thread_progress_time_limit

            if task.attempts and "Access Denied" in task.attempts[-1]:
                self._tasks_manager_thread_keepalive = None
                raise RuntimeError(f"Uploading file {task.file_path} failed with {task.attempts[-1]}")

            self.execute_s3_upload_task(task)

    def finish_multipart_uploads(self, finished_tasks):
        """
        Goes over finished tasks- if there are finished multipart tasks sends complete request to AWS.

        @param finished_tasks: List of successfully completed tasks.
        @return:
        """
        finished_parts = []
        for task in finished_tasks:
            if task.task_type != task.Type.PART:
                continue
            if task.upload_id in finished_parts:
                continue

            finished_parts.append(task.upload_id)
            for upload_part in self.multipart_uploads[task.upload_id]:
                if not upload_part.finished or not upload_part.succeed:
                    break
            else:
                logger.info(f"Completing multipart upload of file {task.key_name}")

                task = self.multipart_uploads[task.upload_id][0]
                filters_req = {"Bucket": task.bucket_name,
                               "Key": task.key_name,
                               "UploadId": task.upload_id,
                               "MultipartUpload": {
                                   'Parts': [
                                       {"ETag": part.raw_response["ETag"].strip('"'), "PartNumber": part.part_number}
                                       for part in self.multipart_uploads[task.upload_id]]
                               }}

                finished_uploads = list(
                    self.execute(self.client.complete_multipart_upload, None, raw_data=True, filters_req=filters_req))

                if len(finished_uploads) != 1:
                    raise ValueError(f"Was not able to finish multipart upload with params {filters_req}. "
                                     f"len(finished_uploads) = {len(finished_uploads)} != 1")

    def execute_s3_upload_task(self, task):
        """
        Starts uploading task thread.

        @param task: UpdateTask
        @return:
        """
        task.started = True
        if task.task_type == task.Type.FILE:
            thread_pool_executor_future = self.thread_pool_executor.submit(self.upload_file_thread, (task))
        elif task.task_type == task.Type.PART:
            thread_pool_executor_future = self.thread_pool_executor.submit(self.upload_file_part_thread, (task))
        else:
            raise ValueError(task.type)
        task.thread_pool_executor_future = thread_pool_executor_future

    def upload_file_thread(self, task):
        """
        Uploads a complete file.

        @param task: UpdateTask with all needed info
        @return:
        """
        logger.info(f"Starting upload_file_thread for file {task.file_path}")
        with open(task.file_path, "rb") as file_handler:
            file_data = file_handler.read()

        start_time = datetime.datetime.now()
        filters_req = {"Bucket": task.bucket_name, "Key": task.key_name, "Body": file_data}

        if task.extra_args is not None:
            filters_req.update(task.extra_args)

        if self.md5_validate:
            self.add_md5_to_request(filters_req, file_data)

        try:
            for response in self.execute(self.client.put_object, None, filters_req=filters_req, raw_data=True):
                task.raw_response = response
            task.succeed = True
        except Exception as exception_inst:
            exception_repr = repr(exception_inst)
            logger.warning(f"Failed to upload to s3 {filters_req} with exception {exception_repr}")
            task.attempts.append(exception_repr)
            task.succeed = False

        task.finished = True
        end_time = datetime.datetime.now()
        logger.info(f"Uploaded {task.key_name}, {len(file_data)} bytes took {end_time - start_time}")

    @staticmethod
    def add_md5_to_request(filters_req, file_data):
        md = hashlib.md5(file_data).digest()
        content_md5_string = base64.b64encode(md).decode('utf-8')
        filters_req["ContentMD5"] = content_md5_string

    def upload_file_part_thread(self, task):
        """
        Uploads part of a large file.

        @param task: UpdateTask has all the relevant information for the upload - offset, length etc.
        @return:
        """
        logger.info(f"Reading file {task.file_path} offset {task.offset_index}, offset_length {task.offset_length}")

        with open(task.file_path, "rb") as file_handler:
            file_handler.seek(task.offset_index)
            byte_chunk = file_handler.read(task.offset_length)

        logger.info(f"Uploading {len(byte_chunk)} bytes part {task.part_number}")
        filters_req = {"Bucket": task.bucket_name,
                       "Body": byte_chunk,
                       "UploadId": task.upload_id,
                       "PartNumber": task.part_number,
                       "Key": task.key_name
                       }

        if task.extra_args is not None:
            filters_req.update(task.extra_args)

        if self.md5_validate:
            self.add_md5_to_request(filters_req, byte_chunk)

        start_time = datetime.datetime.now()
        try:
            for response in self.execute(self.client.upload_part, None, raw_data=True,
                                         filters_req=filters_req):
                task.raw_response = response
            task.succeed = True
        except Exception as exception_inst:
            logger.warning(exception_inst)
            task.succeed = False

        task.finished = True

        end_time = datetime.datetime.now()
        logger.info(f"Uploaded {len(byte_chunk)} bytes part {task.part_number}: took {end_time - start_time}")

    def start_uploading_file_task(self, bucket_name, file_path, key_name, extra_args=None):
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

        file_size = os.path.getsize(file_path)
        if file_size >= self.multipart_threshold:
            return self.start_multipart_uploading_file_task(bucket_name, file_path, key_name, extra_args=extra_args)

        task_id = key_name
        task_type = UploadTask.Type.FILE

        task = UploadTask(task_id, task_type, file_path, bucket_name, key_name, extra_args=extra_args)
        task.start_time = datetime.datetime.now()
        self.insert_task_into_tasks_queue(task)

    def start_multipart_uploading_file_task(self, bucket_name, file_path, key_name, extra_args=None):
        """
        S3 limitation:
        Part number of part being uploaded. This is a positive integer between 1 and 10,000.

        @param bucket_name:
        @param file_path:
        @param key_name:
        @return:
        """

        if os.path.getsize(file_path) / self.multipart_chunk_size >= 100000:
            raise ValueError("Can not split file to more then 10000 parts")

        filters_req = {"Bucket": bucket_name,
                       "Key": key_name
                       }
        if extra_args is not None:
            filters_req.update(extra_args)

        multipart_upload_ids = list(
            self.execute(self.client.create_multipart_upload, "UploadId", filters_req=filters_req))

        if len(multipart_upload_ids) != 1:
            raise ValueError(f"Was not able to create multipart upload with params {filters_req}. "
                             f"len(multipart_upload) = {len(multipart_upload_ids)} != 1")

        upload_id = multipart_upload_ids[0]
        fh = open(file_path, "ab")
        last_position = fh.tell()
        full_chunks = last_position // self.multipart_chunk_size
        part_chunk = last_position % self.multipart_chunk_size

        self.multipart_uploads[upload_id] = list()
        part_number = 0
        file_lock = threading.Lock()
        for part_number in range(1, full_chunks + 1):
            task_id = f"{key_name}%{part_number}"
            task = UploadTask(task_id, UploadTask.Type.PART, file_path, bucket_name, key_name)
            task.part_number = part_number
            task.offset_index = self.multipart_chunk_size * (part_number - 1)
            task.offset_length = self.multipart_chunk_size
            task.upload_id = upload_id
            task.file_lock = file_lock
            self.multipart_uploads[upload_id].append(task)
            self.insert_task_into_tasks_queue(task)

        if part_chunk > 0:
            part_number += 1
            task_id = f"{key_name}%{part_number}"
            task = UploadTask(task_id, UploadTask.Type.PART, file_path, bucket_name, key_name)
            task.part_number = part_number
            task.offset_index = self.multipart_chunk_size * (part_number - 1)
            task.offset_length = self.multipart_chunk_size
            task.upload_id = upload_id
            task.file_lock = file_lock
            self.multipart_uploads[upload_id].append(task)
            self.insert_task_into_tasks_queue(task)

    def insert_task_into_tasks_queue(self, task):
        counter = 20 * 60 * 2
        while counter > 0:
            if self._tasks_manager_thread_keepalive is None:
                raise RuntimeError("tasks_manager_thread is dead")

            try:
                return self.tasks_queue.put(task)
            except TasksQueue.FullQueueError:
                counter -= 1
                time.sleep(0.5)
        else:
            raise TimeoutError(f"Timeout reached waiting to put a task into tasks queue")

    def upload_directory(self, bucket_name, src_data_path, dst_root_key, extra_args=None):
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
            self.start_uploading_object(bucket_name, src_object_full_path, new_dst_root_key, keep_src_object_name=False, extra_args=extra_args)

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

    def delete_objects(self, bucket):
        keys_to_delete = list(self.yield_bucket_objects(bucket))
        while len(keys_to_delete) != 0:
            deletion_list = [{"Key": obj.key} for obj in keys_to_delete[:1000]]
            request_dict = {"Bucket": bucket.name, "Delete": {"Objects": deletion_list}}
            for response in self.execute(self.client.delete_objects, None, raw_data=True, filters_req=request_dict):
                logger.info(f"Deleted {len(deletion_list)} keys from bucket '{bucket.name}'")
                if "Errors" in response:
                    raise RuntimeError(response)
                pass
            keys_to_delete = keys_to_delete[1000:]


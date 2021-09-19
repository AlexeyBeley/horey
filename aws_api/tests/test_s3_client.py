import os
import sys

from horey.aws_api.aws_clients.s3_client import S3Client
from horey.aws_api.aws_services_entities.s3_bucket import S3Bucket
import pdb
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.common_utils.common_utils import CommonUtils

from unittest.mock import Mock
configuration_values_file_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py")
logger = get_logger(configuration_values_file_full_path=configuration_values_file_full_path)

accounts_file_full_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "aws_api_managed_accounts.py"))

accounts = CommonUtils.load_object_from_module(accounts_file_full_path, "main")
AWSAccount.set_aws_account(accounts["1111"])
AWSAccount.set_aws_region(accounts["1111"].regions['us-west-2'])


def test_init_s3_client():
    assert isinstance(S3Client(), S3Client)


def test_provision_s3_bucket():
    region = Region.get_region("us-west-2")
    s3_client = S3Client()

    s3_bucket = S3Bucket({})
    s3_bucket.region = region
    s3_bucket.name = "horey-alexey-ytest-test"
    s3_bucket.acl = "private"

    s3_client.provision_bucket(s3_bucket)


def test_provision_s3_bucket():
    region = Region.get_region("us-west-2")
    s3_client = S3Client()

    s3_bucket = S3Bucket({})
    s3_bucket.region = region
    s3_bucket.name = "horey-alexey-ytest-test"
    s3_bucket.acl = "private"

    s3_bucket.policy = S3Bucket.Policy({})
    s3_bucket.policy.version = "2012-10-17"
    s3_bucket.policy.statement = [
          {
            "Sid": "AllowReadAny",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{s3_bucket.name}/*"
          }
        ]

    s3_client.provision_bucket(s3_bucket)


def create_test_file(path, size):
    with open(path, "w+") as file_handler:
        file_handler.write("a" * size)


def test_upload_small_file_to_s3():
    path = "./test_file"
    # 10 MB
    #size = 10 * 1024 * 1024
    # 10 Byte
    size = 10

    create_test_file(path, size)

    s3_client = S3Client()
    bucket_name = "horey-alexey-ytest-test"
    src_data_path = path
    dst_root_key = "root"
    s3_client.upload(bucket_name, src_data_path, dst_root_key, keep_src_object_name=False)


def test_upload_small_dir_to_s3():
    dir_path = "./test_files_dir"
    file_name = "test_file"
    path = os.path.join(dir_path, file_name)
    os.makedirs(dir_path, exist_ok=True)
    size = 10

    create_test_file(path, size)

    s3_client = S3Client()
    bucket_name = "horey-alexey-ytest-test"
    src_data_path = dir_path
    dst_root_key = "root"
    s3_client.upload(bucket_name, src_data_path, dst_root_key, keep_src_object_name=True)


def test_upload_large_file_to_s3():
    dir_path = "./test_files_dir"
    file_name = "test_file"
    path = os.path.join(dir_path, file_name)
    os.makedirs(dir_path, exist_ok=True)
    size = 500 * 1024 * 1024

    create_test_file(path, size)

    s3_client = S3Client()
    bucket_name = "horey-alexey-ytest-test"
    src_data_path = path
    dst_root_key = "root"
    s3_client.upload(bucket_name, src_data_path, dst_root_key, keep_src_object_name=True)


def test_upload_large_files_directory_to_s3():
    dir_path = "./test_files_dir"
    os.makedirs(dir_path, exist_ok=True)
    for counter in range(10):
        file_name = f"test_file_{counter}"
        path = os.path.join(dir_path, file_name)
        size = 500 * 1024 * 1024

        create_test_file(path, size)

    s3_client = S3Client()
    bucket_name = "horey-alexey-ytest-test"
    src_data_path = dir_path
    dst_root_key = "root"
    s3_client.upload(bucket_name, src_data_path, dst_root_key, keep_src_object_name=True)


def test_upload_small_files_directory_to_s3():
    dir_path = "./test_files_dir"
    os.makedirs(dir_path, exist_ok=True)
    for counter in range(100000):
        file_name = f"test_file_{counter}"
        path = os.path.join(dir_path, file_name)
        size = 100 * 1024

        create_test_file(path, size)

    s3_client = S3Client()
    bucket_name = "horey-alexey-ytest-test"
    src_data_path = dir_path
    dst_root_key = "root"
    s3_client.upload(bucket_name, src_data_path, dst_root_key, keep_src_object_name=True)

if __name__ == "__main__":
    #test_init_s3_client()
    #test_provision_s3_bucket()
    #test_upload_small_file_to_s3()
    test_upload_large_file_to_s3()
    #test_upload_large_files_directory_to_s3()
    #test_multipart_upload_file()

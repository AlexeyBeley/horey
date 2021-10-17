import os

from unittest.mock import Mock
from horey.aws_api.aws_clients.s3_client import S3Client
from horey.aws_api.aws_services_entities.s3_bucket import S3Bucket
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region

AWSAccount.set_aws_region(Region.get_region('us-west-2'))

TEST_BUCKET_NAME = "horey-alexey-ytest-test"  # "horey-test-bucket"


def test_init_s3_client():
    assert isinstance(S3Client(), S3Client)


def test_provision_s3_bucket():
    region = Region.get_region("us-west-2")
    s3_client = S3Client()

    s3_bucket = S3Bucket({})
    s3_bucket.region = region
    s3_bucket.name = TEST_BUCKET_NAME
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
    print(f"Creating test file {path}")
    with open(path, "w+") as file_handler:
        file_handler.write("a" * size)


def create_test_html_file(path, size):
    print(f"Creating test html file {path}")
    prefix_data = "<head>Hello world!</head><body>Body content:\n"
    postfix_data = "</body>"
    size = size - (len(prefix_data) + len(postfix_data))
    with open(path, "w+") as file_handler:
        file_handler.write(prefix_data + "a" * size + postfix_data)


def test_upload_small_file_to_s3():
    path = "./test_file"
    # 10 Byte
    size = 10

    create_test_file(path, size)

    s3_client = S3Client()
    src_data_path = path
    dst_root_key = "root"
    s3_client.upload(TEST_BUCKET_NAME, src_data_path, dst_root_key, keep_src_object_name=False)


def test_upload_small_file_with_extra_args_to_s3():
    path = "./index.html"
    # 200 Byte
    size = 200

    create_test_html_file(path, size)

    s3_client = S3Client()
    src_data_path = path
    dst_root_key = "root"
    #extra_args = {"Metadata": {"Content-Type": "text/html"}, "CacheControl": "max-age=2592000", "ContentType": "text/html"}
    extra_args = {"Metadata": {"Content-Type": "text/html"}, "CacheControl": "no-cache", "ContentType": "text/html"}
    s3_client.upload(TEST_BUCKET_NAME, src_data_path, dst_root_key, keep_src_object_name=True, extra_args=extra_args)


def test_upload_large_file_with_extra_args_to_s3():
    path = "./index.html"
    # 200 Byte
    size = 200 * 1024 * 1024

    create_test_html_file(path, size)

    s3_client = S3Client()
    src_data_path = path
    dst_root_key = "root"
    #extra_args = {"Metadata": {"Content-Type": "text/html"}, "CacheControl": "max-age=2592000", "ContentType": "text/html"}
    extra_args = {"Metadata": {"Content-Type": "text/html"}, "CacheControl": "no-cache", "ContentType": "text/html"}
    s3_client.upload(TEST_BUCKET_NAME, src_data_path, dst_root_key, keep_src_object_name=True, extra_args=extra_args)


def test_upload_small_dir_to_s3():
    dir_path = "./test_files_dir"
    file_name = "test_file"
    path = os.path.join(dir_path, file_name)
    os.makedirs(dir_path, exist_ok=True)
    size = 10

    create_test_file(path, size)

    s3_client = S3Client()
    src_data_path = dir_path
    dst_root_key = "root"
    s3_client.upload(TEST_BUCKET_NAME, src_data_path, dst_root_key, keep_src_object_name=True)


def test_upload_large_file_to_s3():
    dir_path = "./test_files_dir"
    file_name = "test_file"
    path = os.path.join(dir_path, file_name)
    os.makedirs(dir_path, exist_ok=True)
    size = 500 * 1024 * 1024

    create_test_file(path, size)

    s3_client = S3Client()
    src_data_path = path
    dst_root_key = "root"
    s3_client.upload(TEST_BUCKET_NAME, src_data_path, dst_root_key, keep_src_object_name=True)


def test_upload_large_files_directory_to_s3():
    dir_path = "./test_files_dir"
    os.makedirs(dir_path, exist_ok=True)
    for counter in range(10):
        file_name = f"test_file_{counter}"
        path = os.path.join(dir_path, file_name)
        size = 500 * 1024 * 1024

        create_test_file(path, size)

    s3_client = S3Client()
    src_data_path = dir_path
    dst_root_key = "root"
    s3_client.upload(TEST_BUCKET_NAME, src_data_path, dst_root_key, keep_src_object_name=True)


def test_upload_small_files_directory_to_s3():
    dir_path = "./test_files_dir"
    os.makedirs(dir_path, exist_ok=True)
    for counter in range(100000):
        file_name = f"test_file_{counter}"
        path = os.path.join(dir_path, file_name)
        # 100KB
        size = 100 * 1024

        create_test_file(path, size)

    s3_client = S3Client()
    src_data_path = dir_path
    dst_root_key = "root"
    s3_client.upload(TEST_BUCKET_NAME, src_data_path, dst_root_key, keep_src_object_name=True)

def test_upload_file_thread_without_validation():

    path = "./test_file"
    # 10 Byte
    size = 10

    create_test_file(path, size)

    s3_client = S3Client()
    task = Mock()
    task.file_path = path
    task.bucket_name = TEST_BUCKET_NAME
    task.key_name = "root/test_file"
    task.extra_args = {}
    task.raw_response = None
    task.succeed = None
    task.attempts = list()
    task.finished = None
    s3_client.upload_file_thread(task, md5_validate=False)


def test_upload_file_thread_with_validation():

    path = "./test_file"
    # 10 Byte
    size = 10

    create_test_file(path, size)

    s3_client = S3Client()
    s3_client.md5_validate = True
    task = Mock()
    task.file_path = path
    task.bucket_name = TEST_BUCKET_NAME
    task.key_name = "root/test_file"
    task.extra_args = {}
    task.raw_response = None
    task.succeed = None
    task.attempts = list()
    task.finished = None
    s3_client.upload_file_thread(task)

if __name__ == "__main__":
    #test_init_s3_client()
    #test_provision_s3_bucket()
    #test_upload_small_file_to_s3()
    #test_upload_small_file_with_extra_args_to_s3()
    #test_upload_large_file_with_extra_args_to_s3()
    #test_upload_large_file_to_s3()
    #test_upload_large_files_directory_to_s3()
    #test_upload_small_files_directory_to_s3()
    #test_multipart_upload_file()
    #test_upload_file_thread_without_validation()
    test_upload_file_thread_with_validation()

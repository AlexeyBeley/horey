"""
Serverless packer tests

"""

import os
import datetime

from ignore.mock_values import main
from horey.serverless.packer.packer import Packer
from horey.aws_api.base_entities.region import Region
from horey.aws_api.aws_services_entities.aws_lambda import AWSLambda
from horey.aws_api.aws_api import AWSAPI
from horey.docker_api.docker_api import DockerAPI
from horey.aws_api.aws_services_entities.ecr_repository import ECRRepository

mock_values = main()

DEPLOYMENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build")
HOREY_SOURCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
VENV_DIR = os.path.join(DEPLOYMENT_DIR, "_venv")
PACKAGE_SETUP_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "build", "package_test"
)
ZIP_FILE_NAME = "lambda_test"

SRC_PACKAGE_DIR_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "test_lambda_src_package_dir"
)

# pylint: disable= missing-function-docstring


def test_create_venv():
    packer = Packer()
    packer.create_venv(VENV_DIR)


def test_create_venv_python_39():
    packer = Packer(python_version="3.9")
    packer.create_venv(VENV_DIR)


def test_execute():
    packer = Packer()
    ret = packer.execute("ls")
    print(ret)


def test_execute_in_venv():
    packer = Packer()
    ret = packer.execute_in_venv("ls", VENV_DIR)
    print(ret)


def test_install_horey_requirements():
    packer = Packer()
    packer.install_horey_requirements(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "horey_test_requirements.txt"
        ),
        VENV_DIR,
        HOREY_SOURCE_DIR,
    )


def test_install_requirements():
    packer = Packer()
    ret = packer.install_requirements(PACKAGE_SETUP_DIR, VENV_DIR)
    print(ret.stdout)


def test_create_lambda_package():
    packer = Packer()
    packer.create_lambda_package("lambda_name", DEPLOYMENT_DIR, PACKAGE_SETUP_DIR)


def test_create_lambda_package_python_39():
    packer = Packer(python_version="3.9")
    packer.create_lambda_package("lambda_name", DEPLOYMENT_DIR, PACKAGE_SETUP_DIR)


def test_zip_venv_site_packages():
    packer = Packer()
    packer.zip_venv_site_packages(ZIP_FILE_NAME, VENV_DIR)


def test_add_files_to_zip():
    packer = Packer()
    files_paths = [
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "build",
            "files_list_test",
            file_name,
        )
        for file_name in ["dependency_1.py", "entrypoint.py"]
    ]
    packer.add_files_to_zip(f"{ZIP_FILE_NAME}.zip", files_paths)


def test_provision_lambda():
    packer = Packer()
    aws_api = AWSAPI()

    files_paths = [
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "build",
            "files_list_test",
            file_name,
        )
        for file_name in ["dependency_1.py", "entrypoint.py"]
    ]
    packer.add_files_to_zip(f"{ZIP_FILE_NAME}.zip", files_paths)
    aws_lambda = AWSLambda({})
    aws_lambda.region = Region.get_region("us-west-2")
    aws_lambda.name = "horey-test-lambda"
    aws_lambda.role = mock_values["lambda:execution_role"]
    aws_lambda.handler = "entrypoint.main"
    aws_lambda.runtime = "python3.8"
    aws_lambda.tags = {"lvl": "tst", "name": "horey-test"}
    aws_lambda.policy = {
        "Version": "2012-10-17",
        "Id": "default",
        "Statement": [
            {
                "Sid": aws_lambda.name + "_" + "sid",
                "Effect": "Allow",
                "Principal": {"Service": "events.amazonaws.com"},
                "Action": "lambda:InvokeFunction",
                "Resource": None,
                "Condition": {
                    "ArnLike": {
                        "AWS:SourceArn": mock_values["lambda:policy_events_rule_arn"]
                    }
                },
            }
        ],
    }

    aws_api.provision_aws_lambda(aws_lambda, update_code=True)

    assert aws_lambda.state == "Active"


def test_provision_lambda_python_39():
    packer = Packer()
    aws_api = AWSAPI()

    files_paths = [
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "build",
            "files_list_test",
            file_name,
        )
        for file_name in ["dependency_1.py", "entrypoint.py"]
    ]
    packer.add_files_to_zip(f"{ZIP_FILE_NAME}.zip", files_paths)
    aws_lambda = AWSLambda({})
    aws_lambda.region = Region.get_region("us-west-2")
    aws_lambda.name = "horey-test-lambda"
    aws_lambda.role = mock_values["lambda:execution_role"]
    aws_lambda.handler = "lambda_test.lambda_handler"
    aws_lambda.runtime = "python3.9"
    aws_lambda.tags = {"lvl": "tst", "name": "horey-test"}
    aws_lambda.policy = {
        "Version": "2012-10-17",
        "Id": "default",
        "Statement": [
            {
                "Sid": aws_lambda.name + "_" + "sid",
                "Effect": "Allow",
                "Principal": {"Service": "events.amazonaws.com"},
                "Action": "lambda:InvokeFunction",
                "Resource": None,
                "Condition": {
                    "ArnLike": {
                        "AWS:SourceArn": mock_values["lambda:policy_events_rule_arn"]
                    }
                },
            }
        ],
    }

    aws_api.provision_aws_lambda(aws_lambda, update_code=True)

    assert aws_lambda.state == "Active"


def test_copy_venv_site_packages_to_dir():
    packer = Packer()
    os.makedirs(SRC_PACKAGE_DIR_PATH, exist_ok=True)
    packer.copy_venv_site_packages_to_dir(SRC_PACKAGE_DIR_PATH, VENV_DIR)


def test_provision_lambda_s3():
    packer = Packer()
    aws_api = AWSAPI()

    files_paths = [
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "build",
            "files_list_test",
            file_name,
        )
        for file_name in ["dependency_1.py", "entrypoint.py"]
    ]
    packer.add_files_to_zip(f"{ZIP_FILE_NAME}.zip", files_paths)
    bucketname = mock_values["test_provision_lambda_s3_bucket_name"]
    key_path = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f%z')}"
    aws_api.s3_client.upload(bucketname, f"{ZIP_FILE_NAME}.zip", key_path)

    aws_lambda = AWSLambda({})
    aws_lambda.code = {"S3Bucket": bucketname, "S3Key": f"{key_path}/{ZIP_FILE_NAME}.zip"}
    aws_lambda.region = Region.get_region("us-west-2")
    aws_lambda.name = "horey-test-lambda-1"
    aws_lambda.role = mock_values["lambda:execution_role"]
    aws_lambda.handler = "lambda_test.lambda_handler"
    aws_lambda.runtime = "python3.9"
    aws_lambda.tags = {"lvl": "tst", "name": "horey-test"}
    aws_lambda.policy = {
        "Version": "2012-10-17",
        "Id": "default",
        "Statement": [
            {
                "Sid": aws_lambda.name + "_" + "sid",
                "Effect": "Allow",
                "Principal": {"Service": "events.amazonaws.com"},
                "Action": "lambda:InvokeFunction",
                "Resource": None,
                "Condition": {
                    "ArnLike": {
                        "AWS:SourceArn": mock_values["lambda:policy_events_rule_arn"]
                    }
                },
            }
        ],
    }
    aws_api.provision_aws_lambda(aws_lambda, update_code=True)

    assert aws_lambda.state == "Active"


def test_get_local_python_version():
    assert Packer.PYTHON_VERSION is not None


def prepare_and_upload_image(region, aws_api, docker_api):
    # repo
    repo = ECRRepository({})
    repo.region = region
    repo.name = "lambda-test-repo"
    repo.tags = [{
            "Key": "Name",
            "Value": repo.name
        }]
    aws_api.provision_ecr_repository(repo)

    #login
    credentials = aws_api.get_ecr_authorization_info(region=region)
    credentials = credentials[0]
    registry, username, password = credentials["proxy_host"], credentials["user_name"], credentials["decoded_token"]
    docker_api.login(registry, username, password)

    #build
    tags = [f"{aws_api.ec2_client.account_id}.dkr.ecr.{region.region_mark}.amazonaws.com/{repo.name}:latest"]
    image = docker_api.build(os.path.join(os.path.dirname(os.path.abspath(__file__)), "docker_image"), tags)

    docker_api.upload_images(tags)
    return image


def test_provision_lambda_docker_image():
    region = Region.get_region("us-west-2")
    aws_api = AWSAPI()
    docker_api = DockerAPI()
    prepare_and_upload_image(region, aws_api, docker_api)

    aws_lambda = AWSLambda({})
    tag = f"{aws_api.ec2_client.account_id}.dkr.ecr.{region.region_mark}.amazonaws.com/lambda-test-repo:latest"
    aws_lambda.code = {"ImageUri": tag}
    # aws_lambda.code = {"ImageUri": image.tags[0]}
    aws_lambda.region = region
    aws_lambda.name = "test-lambda-docker"
    aws_lambda.role = mock_values["lambda:execution_role"]
    aws_lambda.handler = "lambda_test.lambda_handler"
    aws_lambda.runtime = "python3.9"
    aws_lambda.tags = {"lvl": "tst", "name": "horey-test"}
    aws_lambda.policy = {
        "Version": "2012-10-17",
        "Id": "default",
        "Statement": [
            {
                "Sid": aws_lambda.name + "_" + "sid",
                "Effect": "Allow",
                "Principal": {"Service": "events.amazonaws.com"},
                "Action": "lambda:InvokeFunction",
                "Resource": None,
                "Condition": {
                    "ArnLike": {
                        "AWS:SourceArn": mock_values["lambda:policy_events_rule_arn"]
                    }
                },
            }
        ],
    }
    aws_api.provision_aws_lambda(aws_lambda, update_code=True)

    assert aws_lambda.state == "Active"


if __name__ == "__main__":
    # test_create_venv()
    # test_execute()
    # test_execute_in_venv()
    # test_install_requirements()
    # test_install_horey_requirements()
    # test_create_lambda_package()
    # test_zip_venv_site_packages()
    # test_add_files_to_zip()
    # test_provision_lambda()
    # test_copy_venv_site_packages_to_dir()
    # test_create_venv_python_39()
    # test_provision_lambda_python_39()
    # test_create_lambda_package_python_39()
    # test_provision_lambda_s3()
    # test_get_local_python_version()
    test_provision_lambda_docker_image()

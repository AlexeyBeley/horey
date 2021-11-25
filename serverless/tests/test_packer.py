import pdb
import os

from horey.serverless.packer.packer import Packer
from horey.aws_api.base_entities.region import Region
from horey.aws_api.aws_services_entities.aws_lambda import AWSLambda
from horey.aws_api.aws_api import AWSAPI

from ignore.mock_values import main
mock_values = main()

DEPLOYMENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build")
VENV_DIR = os.path.join(DEPLOYMENT_DIR, "_venv")
PACKAGE_SETUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "package_test")
ZIP_FILE_NAME = "lambda_test"


def test_create_venv():
    packer = Packer()
    packer.create_venv(VENV_DIR)


def test_execute_in_venv():
    packer = Packer()
    ret = packer.execute_in_venv("ls", VENV_DIR)
    print(ret.stdout)


def test_install_requirements():
    packer = Packer()
    ret = packer.install_requirements(PACKAGE_SETUP_DIR, VENV_DIR)
    print(ret.stdout)


def test_create_lambda_package():
    packer = Packer()
    packer.create_lambda_package("lambda_name", DEPLOYMENT_DIR, PACKAGE_SETUP_DIR)


def test_zip_venv_site_packages():
    packer = Packer()
    packer.zip_venv_site_packages(ZIP_FILE_NAME, VENV_DIR, "python3.8")


def test_add_files_to_zip():
    packer = Packer()
    files_paths = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "files_list_test", file_name) for file_name
                   in ["dependency_1.py", "entrypoint.py"]]
    packer.add_files_to_zip(f"{ZIP_FILE_NAME}.zip", files_paths)


def test_provision_lambda():
    packer = Packer()
    aws_api = AWSAPI()

    files_paths = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "files_list_test", file_name) for file_name
                   in ["dependency_1.py", "entrypoint.py"]]
    packer.add_files_to_zip(f"{ZIP_FILE_NAME}.zip", files_paths)
    aws_lambda = AWSLambda({})
    aws_lambda.region = Region.get_region("us-west-2")
    aws_lambda.name = "horey-test-lambda"
    aws_lambda.role = mock_values["lambda:execution_role"]
    aws_lambda.handler = "lambda_test.lambda_handler"
    aws_lambda.runtime = "python3.8"
    aws_lambda.tags = {
        "lvl": "tst",
        "name": "horey-test"
    }

    files_paths = [os.path.join(os.path.dirname(os.path.abspath(__file__)), filename) for filename in
                   ["lambda_test.py", "lambda_test_2.py"]]

    aws_api.provision_aws_lambda(aws_lambda, force=True)

    assert aws_lambda.state == "Active"


if __name__ == "__main__":
    # test_create_venv()
    # test_execute_in_venv()
    # test_install_requirements()
    # test_create_lambda_package()
    #test_zip_venv_site_packages()
    #test_add_files_to_zip()
    test_provision_lambda()

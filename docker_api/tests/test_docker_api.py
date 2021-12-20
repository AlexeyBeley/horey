import pdb

from horey.docker_api.docker_api import DockerAPI
import os
from horey.common_utils.common_utils import CommonUtils
from horey.aws_api.aws_api import AWSAPI

mock_values_file_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"))
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

src_aws_region = "us-west-2"
dst_aws_region = "us-west-2"


def test_init_docker_api():
    assert isinstance(DockerAPI(), DockerAPI)


def login(docker_api):
    aws_api = AWSAPI()
    credentials = aws_api.get_ecr_authorization_info(region=src_aws_region)
    credentials = credentials[0]
    registry, username, password = credentials["proxy_host"], credentials["user_name"], credentials["decoded_token"]
    docker_api.login(registry, username, password)


def test_login():
    docker_api = DockerAPI()
    aws_api = AWSAPI()
    credentials = aws_api.get_ecr_authorization_info(region=src_aws_region)

    if len(credentials) != 1:
        raise ValueError(f"len(credentials) != 1")
    credentials = credentials[0]

    registry, username, password = credentials["proxy_host"], credentials["user_name"], credentials["decoded_token"]
    docker_api.login(registry, username, password)


def test_build():
    docker_api = DockerAPI()
    image = docker_api.build(os.path.dirname(os.path.abspath(__file__)), ["horey-test:latest"])
    assert image is not None


def test_get_image():
    docker_api = DockerAPI()
    image = docker_api.get_image("horey-test:latest")
    assert image is not None


def test_upload_image():
    docker_api = DockerAPI()
    login(docker_api)
    image = docker_api.get_image("horey-test:latest")
    tags = mock_values["src_image_tags"]
    docker_api.tag_image(image, tags)
    docker_api.upload_image(tags)


def test_pull_image():
    docker_api = DockerAPI()
    login(docker_api)
    image = docker_api.pull_image(mock_values["src_image_tags"][0])
    assert image is not None


def test_copy_image():
    docker_api = DockerAPI()
    login(docker_api)
    docker_api.copy_image(mock_values["src_image_tags"][0], mock_values["dst_repo"], copy_all_tags=True)


if __name__ == "__main__":
    #test_init_docker_api()
    #test_build()
    #test_get_image()
    #test_login()
    #test_upload_image()
    #test_pull_image()
    test_copy_image()

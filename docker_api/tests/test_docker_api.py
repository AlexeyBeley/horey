"""
Testing docker_api module.

"""

import os
from horey.docker_api.docker_api import DockerAPI
from horey.common_utils.common_utils import CommonUtils
from horey.aws_api.aws_api import AWSAPI

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

src_aws_region = "us-west-2"
dst_aws_region = "us-west-2"

# pylint: disable= missing-function-docstring

def test_init_docker_api():
    """
    Test basic init.

    @return:
    """

    assert isinstance(DockerAPI(), DockerAPI)


def login(docker_api):
    """
    Login to aws region using aws_api

    @param docker_api:
    @return:
    """

    aws_api = AWSAPI()
    credentials = aws_api.get_ecr_authorization_info(region=src_aws_region)
    credentials = credentials[0]
    registry, username, password = (
        credentials["proxy_host"],
        credentials["user_name"],
        credentials["decoded_token"],
    )
    docker_api.login(registry, username, password)


def test_login():
    """
    Test login to aws region using aws_api

    @return:
    """
    docker_api = DockerAPI()
    aws_api = AWSAPI()
    credentials = aws_api.get_ecr_authorization_info(region=src_aws_region)

    if len(credentials) != 1:
        raise ValueError("len(credentials) != 1")
    credentials = credentials[0]

    registry, username, password = (
        credentials["proxy_host"],
        credentials["user_name"],
        credentials["decoded_token"],
    )
    docker_api.login(registry, username, password)


def test_build():
    """
    Test building image.

    @return:
    """

    docker_api = DockerAPI()
    image = docker_api.build(
        os.path.dirname(os.path.abspath(__file__)), ["horey-test:latest"]
    )
    assert image is not None


def test_get_image():
    """
    Self explanatory.

    @return:
    """

    docker_api = DockerAPI()
    image = docker_api.get_image("horey-test:latest")
    assert image is not None


def test_upload_image():
    """
    Self explanatory.

    @return:
    """

    docker_api = DockerAPI()
    login(docker_api)
    image = docker_api.get_image("horey-test:latest")
    tags = mock_values["src_image_tags"]
    docker_api.tag_image(image, tags)
    docker_api.upload_images(tags)


def test_pull_image():
    """
    Self explanatory.

    @return:
    """

    docker_api = DockerAPI()
    login(docker_api)
    images = docker_api.pull_images(mock_values["src_image_tags"][0])
    assert images is not None


def test_copy_image():
    """
    Test copying image from source repo to dst

    @return:
    """

    docker_api = DockerAPI()
    login(docker_api)
    docker_api.copy_image(
        mock_values["src_image_tags"][0], mock_values["dst_repo"], copy_all_tags=True
    )


def test_remove_image():
    """
    Test removing image.

    @return:
    """

    docker_api = DockerAPI()
    docker_api.remove_image("755fa0e2e444", force=True)


def test_get_all_images():
    """
    Test getting all images.

    @return:
    """

    docker_api = DockerAPI()
    login(docker_api)
    images = docker_api.get_all_images(repo_name=mock_values["repo_name"])
    assert images is not None


def test_get_child_image_ids():
    docker_api = DockerAPI()
    image_id = ""
    image_ids = docker_api.get_child_image_ids(image_id)
    assert isinstance(image_ids, list)


if __name__ == "__main__":
    # test_init_docker_api()
    # test_build()
    # test_get_image()
    # test_login()
    # test_upload_image()
    # test_pull_image()
    # test_copy_image()
    # test_remove_image()
    #test_get_all_images()
    test_get_child_image_ids()

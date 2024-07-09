"""
Testing docker_api module.

"""

import os

import pytest
from horey.docker_api.docker_api import DockerAPI
from horey.common_utils.common_utils import CommonUtils
from horey.aws_api.aws_api import AWSAPI

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "docker_api_mock_values.py"
    )
)
print(f"{mock_values_file_path=}")
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

src_aws_region = "us-west-2"
dst_aws_region = "us-west-2"

# pylint: disable= missing-function-docstring


@pytest.mark.done
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
    return registry


@pytest.mark.done
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


@pytest.mark.done
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


@pytest.mark.done
def test_get_image():
    """
    Self explanatory.

    @return:
    """

    docker_api = DockerAPI()
    image = docker_api.get_image("horey-test:latest")
    assert image is not None


@pytest.mark.skip
def test_upload_image():
    docker_api = DockerAPI()
    registry = login(docker_api)
    image_tag = "horey-test:latest"
    image = docker_api.get_image(image_tag)
    tags = [f"{registry}/{image_tag}"]
    docker_api.tag_image(image, tags)
    docker_api.upload_images(tags)


@pytest.mark.skip
def test_pull_image():
    """
    Self explanatory.

    @return:
    """

    docker_api = DockerAPI()
    registry = login(docker_api)
    image_tag = "horey-test:latest"
    tags = f"{registry}/{image_tag}"
    images = docker_api.pull_images(tags)
    assert images is not None


@pytest.mark.skip
def test_copy_image():
    """
    Test copying image from source repo to dst

    @return:
    """

    docker_api = DockerAPI()
    registry = login(docker_api)
    image_tag = "horey-test:latest"
    image_registry_path = f"{registry}/{image_tag}"
    image_dst_tag = "horey-test:dst"
    image_registry_path_dst = f"{registry}/{image_dst_tag}"
    docker_api.copy_image(
        image_registry_path, image_registry_path_dst, copy_all_tags=True
    )


@pytest.mark.skip
def test_remove_image():
    """
    Test removing image.

    @return:
    """

    docker_api = DockerAPI()
    docker_api.remove_image(mock_values["image_with_children_id"], force=True)


@pytest.mark.done
def test_get_all_images():
    """
    Test getting all images.

    @return:
    """

    docker_api = DockerAPI()
    registry = login(docker_api)
    images = docker_api.get_all_images(repo_name=f"{registry}/horey-test")
    assert images is not None


@pytest.mark.skip
def test_get_child_image_ids():
    docker_api = DockerAPI()
    image_id = mock_values["image_with_children_id"]
    image_ids = docker_api.get_child_image_ids(image_id)
    assert isinstance(image_ids, list)


@pytest.mark.done
def test_save():
    docker_api = DockerAPI()
    image_tag = "horey-test:latest"
    image = docker_api.get_image(image_tag)
    assert docker_api.save(image, "tmp.tar")


@pytest.mark.done
def test_load():
    docker_api = DockerAPI()
    image = docker_api.load("tmp.tar")
    tags = ["horey-test:latest", "horey:file_loaded"]
    assert docker_api.tag_image(image, tags)


@pytest.mark.wip
def test_get_all_ancestors():
    docker_api = DockerAPI()
    image_id = "sha256:7455e988e7a35e82819636c8afd59516147c199309ed47aa720283d571a0880e"
    ret = docker_api.get_all_ancestors(image_id)
    assert ret

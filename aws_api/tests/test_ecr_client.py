"""
Test aws ecr client.

"""
import os
import pytest

from horey.aws_api.aws_clients.ecr_client import ECRClient
from horey.aws_api.aws_services_entities.ecr_repository import ECRRepository
from horey.aws_api.aws_services_entities.ecr_image import ECRImage
from horey.aws_api.base_entities.region import Region
from horey.common_utils.common_utils import CommonUtils


mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

ECRClient().main_cache_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore",
            "cache"
        )
    )

# pylint: disable= missing-function-docstring§

@pytest.mark.done
def test_init_ecr_client():
    """
    Base init check.

    @return:
    """

    assert isinstance(ECRClient(), ECRClient)

@pytest.mark.done
def test_get_authorization_info():
    """
    Test getting authorization info used by docker service.

    @return:
    """

    client = ECRClient()
    assert len(client.get_authorization_info()) == 1

@pytest.mark.done
def test_tag_image():
    """
    Tag image with new tags.

    @return:
    """

    client = ECRClient()
    repos = client.get_region_repositories(Region.get_region("us-east-1"))
    images = client.get_all_images(repos[5])
    client.tag_image(images[3], ["test_version"])

@pytest.mark.done
def test_provision_repository():
    client = ECRClient()
    repo = ECRRepository({})
    repo.region = Region.get_region("us-west-2")
    repo.name = "test_tags"
    repo.tags = [{
        "Key": "Name",
        "Value": "some_other_name"
    }]
    client.provision_repository(repo)

@pytest.mark.done
def test_provision_repository_change_tags():
    client = ECRClient()
    repo = ECRRepository({})
    repo.region = Region.get_region("us-west-2")
    repo.name = "test_tags"
    repo.tags = [{
        "Key": "Name",
        "Value": "some_other_name"
    }]
    client.provision_repository(repo)

    region_repos = client.get_region_repositories(
        repo.region, repository_names=[repo.name], get_tags=True)

    if len(region_repos) != 1:
        raise RuntimeError("len(region_repos) != 1")

    assert region_repos[0].tags == repo.tags

    repo.tags = [{
        "Key": "Name",
        "Value": repo.name
    }]

    client.provision_repository(repo)

    region_repos = client.get_region_repositories(
        repo.region, repository_names=[repo.name], get_tags=True)

    if len(region_repos) != 1:
        raise RuntimeError("len(region_repos) != 1")

    assert region_repos[0].tags == repo.tags

@pytest.mark.wip
def test_yield_repositories():
    client = ECRClient()
    obj = None
    for obj in client.yield_repositories():
        break
    assert obj.arn is not None

@pytest.mark.wip
def test_get_all_repositories():
    client = ECRClient()
    assert len(client.get_all_repositories()) > 0


@pytest.mark.wip
def test_get_region_repositories_tags_true():
    client = ECRClient()
    assert len(client.get_region_repositories(Region.get_region("us-west-2"), get_tags=True)) > 0


@pytest.mark.wip
def test_get_region_repositories_tags_false():
    """
    Tag image with new tags.

    @return:
    """

    client = ECRClient()
    ret = client.get_region_repositories(Region.get_region("us-west-2"), get_tags=False)
    assert len(ret) > 0


@pytest.mark.wip
def test_yield_images_raw_filter_true():
    client = ECRClient()
    filters_req= {"repositoryName": "dst_tst"}
    obj = None
    for obj in client.yield_images_raw(filters_req=filters_req):
        break
    assert isinstance(obj, dict)
    assert obj["imageSizeInBytes"] is not None


@pytest.mark.wip
def test_yield_images_raw_filter_false():
    client = ECRClient()
    obj = None
    for obj in client.yield_images_raw():
        break
    assert isinstance(obj, dict)
    assert obj["imageSizeInBytes"] is not None


@pytest.mark.wip
def test_yield_images_region_none_update_info_false_filters_req_none():
    client = ECRClient()
    obj = None
    for obj in client.yield_images():
        break
    assert obj.image_size_in_bytes is not None


@pytest.mark.wip
def test_yield_images_region_us_west_2_update_info_false_filters_req_none():
    client = ECRClient()
    obj = None
    for obj in client.yield_images(region=Region.get_region("us-west-2")):
        break
    assert obj.image_size_in_bytes is not None


@pytest.mark.wip
def test_yield_images_region_none_update_info_false_filters_req_repo():
    client = ECRClient()
    obj = None
    filters_req = {"repositoryName": "dst_tst"}
    for obj in client.yield_images(filters_req=filters_req):
        break
    assert obj.image_size_in_bytes is not None

@pytest.mark.wip
def test_yield_images_region_us_west_2_update_info_true_filters_req_none():
    client = ECRClient()
    obj = None
    for obj in client.yield_images(region=Region.get_region("us-west-2"), update_info=True):
        break
    assert obj.image_size_in_bytes is not None

@pytest.mark.done
def test_clear_cache():
    client = ECRClient()
    client.clear_cache(ECRImage)


@pytest.mark.wip
def test_get_all_images_region_none():
    client = ECRClient()
    ret = client.get_all_images()
    assert len(ret) > 0


@pytest.mark.wip
def test_get_all_images_region_us_west_2():
    client = ECRClient()
    ret = client.get_all_images(region=Region.get_region("us-west-2"))
    assert len(ret) > 0

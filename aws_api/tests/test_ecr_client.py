"""
Test aws ecr client.

"""
import json
import os
import pytest

from horey.aws_api.aws_clients.ecr_client import ECRClient
from horey.aws_api.aws_services_entities.ecr_repository import ECRRepository
from horey.aws_api.aws_services_entities.ecr_image import ECRImage
from horey.aws_api.base_entities.region import Region
from horey.common_utils.common_utils import CommonUtils


ECRClient().main_cache_dir_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "..",
        "ignore",
        "cache"
    )
)

REPO_NAME = "test_tags"


# pylint: disable= missing-function-docstring§

@pytest.mark.todo
def test_init_ecr_client():
    """
    Base init check.

    @return:
    """

    assert isinstance(ECRClient(), ECRClient)


@pytest.mark.todo
def test_get_authorization_info(repo_base):
    """
    Test getting authorization info used by docker service.

    @return:
    """

    client = ECRClient()
    assert len(client.get_authorization_info(repo_base.region)) == 1


@pytest.mark.skip
def test_tag_image():
    """
    Tag image with new tags.

    @return:
    """

    client = ECRClient()
    images = client.get_all_images()
    client.tag_image(images[3], ["test_version"])


@pytest.fixture(name="repo_base")
def fixture_repo_base():
    repo = ECRRepository({})
    repo.region = Region.get_region("us-west-2")
    repo.name = REPO_NAME
    repo.tags = [{
        "Key": "Name",
        "Value": "some_other_name"
    }]
    return repo


@pytest.mark.todo
def test_provision_repository(repo_base):
    client = ECRClient()
    client.provision_repository(repo_base)


@pytest.mark.todo
def test_get_repository_full_information(repo_base):
    client = ECRClient()
    client.get_repository_full_information(repo_base)


@pytest.mark.todo
def test_update_repository_information(repo_base):
    client = ECRClient()
    assert client.update_repository_information(repo_base)


@pytest.mark.todo
def test_provision_repository_change_tags(repo_base):
    client = ECRClient()
    client.provision_repository(repo_base)

    region_repos = client.get_region_repositories(
        repo_base.region, repository_names=[repo_base.name], get_tags=True)

    if len(region_repos) != 1:
        raise RuntimeError("len(region_repos) != 1")

    assert region_repos[0].tags == repo_base.tags

    repo_base.tags = [{
        "Key": "Name",
        "Value": repo_base.name
    }]

    client.provision_repository(repo_base)

    region_repos = client.get_region_repositories(
        repo_base.region, repository_names=[repo_base.name], get_tags=True)

    if len(region_repos) != 1:
        raise RuntimeError("len(region_repos) != 1")

    assert region_repos[0].tags == repo_base.tags


@pytest.mark.todo
def test_provision_repository_add_policy(repo_base):
    client = ECRClient()
    client.provision_repository(repo_base)
    assert repo_base.policy_text is None
    policy = {"Version": "2008-10-17",
              "Statement": [
        {"Sid": "LambdaECRImageRetrievalPolicy", "Effect": "Allow",
         "Principal": {"Service": "lambda.amazonaws.com"},
         "Action": ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer", "ecr:SetRepositoryPolicy",
                    "ecr:DeleteRepositoryPolicy", "ecr:GetRepositoryPolicy"],
         "Condition": {"StringLike": {
             "aws:sourceArn": f"arn:aws:lambda:{repo_base.region.region_mark}:{client.account_id}:function:*"}}}]}
    repo_base.policy_text = json.dumps(policy)
    client.provision_repository(repo_base)
    assert repo_base.policy_text is not None


@pytest.mark.todo
def test_provision_repository_delete_policy(repo_base):
    client = ECRClient()
    client.provision_repository(repo_base)
    repo_base.policy_text = None
    client.provision_repository(repo_base)
    assert repo_base.policy_text is None


@pytest.mark.todo
def test_yield_repositories():
    client = ECRClient()
    obj = None
    for obj in client.yield_repositories():
        break
    assert obj.arn is not None


@pytest.mark.todo
def test_get_all_repositories(repo_base):
    client = ECRClient()
    assert len(client.get_all_repositories(region=repo_base.region)) > 0


@pytest.mark.todo
def test_get_region_repositories_tags_true():
    client = ECRClient()
    assert len(client.get_region_repositories(Region.get_region("us-west-2"), get_tags=True)) > 0


@pytest.mark.todo
def test_get_region_repositories_tags_false():
    """
    Tag image with new tags.

    @return:
    """

    client = ECRClient()
    ret = client.get_region_repositories(Region.get_region("us-west-2"), get_tags=False)
    assert len(ret) > 0


@pytest.mark.todo
def test_yield_images_raw_filter_true(repo_base):
    client = ECRClient()
    filters_req = {"repositoryName": "dst_tst"}
    obj = None
    for obj in client.yield_images_raw(repo_base.region, filters_req=filters_req):
        break
    assert isinstance(obj, dict)
    assert obj["imageSizeInBytes"] is not None


@pytest.mark.todo
def test_yield_images_raw_filter_false(repo_base):
    client = ECRClient()
    obj = None
    for obj in client.yield_images_raw(repo_base.region):
        break
    assert isinstance(obj, dict)
    assert obj["imageSizeInBytes"] is not None


@pytest.mark.todo
def test_yield_images_region_none_update_info_false_filters_req_none():
    client = ECRClient()
    obj = None
    for obj in client.yield_images():
        break
    assert obj.image_size_in_bytes is not None


@pytest.mark.todo
def test_yield_images_region_us_west_2_update_info_false_filters_req_none():
    client = ECRClient()
    obj = None
    for obj in client.yield_images(region=Region.get_region("us-west-2")):
        break
    assert obj.image_size_in_bytes is not None


@pytest.mark.todo
def test_yield_images_region_none_update_info_false_filters_req_repo():
    client = ECRClient()
    obj = None
    filters_req = {"repositoryName": "dst_tst"}
    for obj in client.yield_images(filters_req=filters_req):
        break
    assert obj.image_size_in_bytes is not None


@pytest.mark.todo
def test_yield_images_region_us_west_2_update_info_true_filters_req_none():
    client = ECRClient()
    obj = None
    for obj in client.yield_images(region=Region.get_region("us-west-2"), update_info=True):
        break
    assert obj.image_size_in_bytes is not None


@pytest.mark.todo
def test_clear_cache():
    client = ECRClient()
    client.clear_cache(ECRImage)


@pytest.mark.todo
def test_get_all_images_region_none():
    client = ECRClient()
    ret = client.get_all_images()
    assert len(ret) > 0


@pytest.mark.todo
def test_get_all_images_region_us_west_2():
    client = ECRClient()
    ret = client.get_all_images(region=Region.get_region("us-west-2"))
    assert len(ret) > 0

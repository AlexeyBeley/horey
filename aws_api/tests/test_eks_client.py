"""
Test aws eks client

"""

import os

import pytest
from horey.aws_api.aws_clients.eks_client import EKSClient
from horey.h_logger import get_logger
from horey.aws_api.base_entities.region import Region
from horey.aws_api.aws_services_entities.eks_cluster import EKSCluster
from horey.aws_api.aws_services_entities.eks_fargate_profile import EKSFargateProfile
from horey.common_utils.common_utils import CommonUtils

logger = get_logger()


# pylint: disable= missing-function-docstring

@pytest.mark.done
def test_init_client():
    """
    Base init check.

    @return:
    """

    assert isinstance(EKSClient(), EKSClient)


@pytest.mark.unit
def test_get_all_clusters():
    client = EKSClient()
    for str_region in ["us-east-1", "us-east-2", "us-west-1", "us-west-2", "af-south-1", "ap-east-1", "ap-southeast-3",
                       "ap-south-1",
                       "ap-northeast-3", "ap-northeast-2", "ap-southeast-1", "ap-southeast-2", "ap-northeast-1",
                       "ca-central-1", "eu-central-1",
                       "eu-west-1", "eu-west-2", "eu-south-1", "sa-east-1"]:
        region = Region.get_region(str_region)
        try:
            objs = client.get_all_clusters(region=region)
            if objs:
                assert objs is not None
        except Exception:
            logger.warning(f"Failed in region: {str_region}")


@pytest.mark.todo
def test_get_all_addons():
    client = EKSClient()
    objs = client.get_all_addons()
    assert objs is not None


@pytest.mark.todo
def test_get_region_clusters():
    client = EKSClient()
    objs = client.get_region_clusters(Region.get_region("us-west-2"))
    assert objs is not None


@pytest.mark.todo
def test_provision_eks_cluster():
    client = EKSClient()
    eks_cluster = EKSCluster({})
    eks_cluster.region = Region.get_region("us-west-2")
    eks_cluster.name = "test_name_1"
    client.provision_cluster(eks_cluster)
    assert eks_cluster.arn is not None


@pytest.mark.todo
def test_get_all_fargate_profiles():
    client = EKSClient()
    objs = client.get_all_fargate_profiles()
    assert objs is not None


@pytest.mark.todo
def test_get_region_fargate_profiles():
    client = EKSClient()
    objs = client.get_region_fargate_profiles(Region.get_region("us-west-2"))
    assert objs is not None


@pytest.mark.todo
def test_provision_fargate_profiles():
    client = EKSClient()
    eks_fargate_profile = EKSFargateProfile({})
    eks_fargate_profile.region = Region.get_region("us-west-2")
    eks_fargate_profile.name = "alb-sample-app"
    eks_fargate_profile.cluster_name = "test-aws-example"
    eks_fargate_profile.pod_execution_role_arn = ""
    client.provision_fargate_profile(eks_fargate_profile)
    assert eks_fargate_profile.arn is not None

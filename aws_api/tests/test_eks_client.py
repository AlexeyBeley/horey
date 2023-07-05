"""
Test aws eks client

"""

import os

from horey.aws_api.aws_clients.eks_client import EKSClient
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.aws_api.aws_services_entities.eks_cluster import EKSCluster
from horey.aws_api.aws_services_entities.eks_fargate_profile import EKSFargateProfile
from horey.common_utils.common_utils import CommonUtils

logger = get_logger()

accounts_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "ignore",
        "aws_api_managed_accounts.py",
    )
)

accounts = CommonUtils.load_object_from_module(accounts_file_full_path, "main")
AWSAccount.set_aws_account(accounts["1111"])
AWSAccount.set_aws_region(accounts["1111"].regions["us-west-2"])

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)

mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

# pylint: disable= missing-function-docstring


def test_init_client():
    """
    Base init check.

    @return:
    """

    assert isinstance(EKSClient(), EKSClient)


def test_get_all_clusters():
    client = EKSClient()
    objs = client.get_all_clusters()
    assert objs is not None


def test_get_all_addons():
    client = EKSClient()
    objs = client.get_all_addons()
    assert objs is not None


def test_get_region_clusters():
    client = EKSClient()
    objs = client.get_region_clusters(Region.get_region("us-west-2"))
    assert objs is not None


def test_provision_eks_cluster():
    client = EKSClient()
    eks_cluster = EKSCluster({})
    eks_cluster.region = Region.get_region("us-west-2")
    eks_cluster.name = "test_name_1"
    client.provision_cluster(eks_cluster)
    assert eks_cluster.arn is not None


def test_get_all_fargate_profiles():
    client = EKSClient()
    objs = client.get_all_fargate_profiles()
    assert objs is not None


def test_get_region_fargate_profiles():
    client = EKSClient()
    objs = client.get_region_fargate_profiles(Region.get_region("us-west-2"))
    assert objs is not None


def test_provision_fargate_profiles():
    client = EKSClient()
    eks_fargate_profile = EKSFargateProfile({})
    eks_fargate_profile.region = Region.get_region("us-west-2")
    eks_fargate_profile.name = "alb-sample-app"
    eks_fargate_profile.cluster_name = "test-aws-example"
    eks_fargate_profile.pod_execution_role_arn = ""
    client.provision_fargate_profile(eks_fargate_profile)
    assert eks_fargate_profile.arn is not None


if __name__ == "__main__":
    # test_init_client()
    # test_get_all_clusters()
    # test_get_region_clusters()
    # test_provision_eks_cluster()
    # test_get_region_clusters()
    # test_get_all_clusters()
    # test_get_all_addons()
    # test_get_all_fargate_profiles()
    # test_get_region_fargate_profiles()
    test_provision_fargate_profiles()

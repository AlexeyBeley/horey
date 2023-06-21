"""
Test aws stepfunctions client.

"""
import json
import os

from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.common_utils.common_utils import CommonUtils
from horey.aws_api.k8s import K8S

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
definition_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "step_definition.json"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

# pylint: disable= missing-function-docstring


def test_get_cluster_login_credentials():
    """
    Base init check.

    @return:
    """
    k8s = K8S()
    cluster_name = "test-aws-example"
    region = Region.get_region("us-west-2")
    k8s.get_cluster_login_credentials(cluster_name, region)


def test_create_fargate_profile():
    """
    https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html
    --cluster test-aws-example \
    --region us-west-2 \
    --name alb-sample-app \
    --namespace game-2048
    :return:
    """



if __name__ == "__main__":
    test_get_cluster_login_credentials()
    test_create_fargate_profile()

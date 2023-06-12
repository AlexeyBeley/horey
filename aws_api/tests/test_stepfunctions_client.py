"""
Test aws stepfunctions client.

"""

import os

from horey.aws_api.aws_clients.stepfunctions_client import StepfunctionsClient
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
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

# pylint: disable= missing-function-docstring


def test_init_client():
    """
    Base init check.

    @return:
    """

    assert isinstance(StepfunctionsClient(), StepfunctionsClient)


def test_get_all_state_machines():
    client = StepfunctionsClient()
    objs = client.get_all_state_machines()
    assert objs is not None


def test_get_region_state_machines():
    client = StepfunctionsClient()
    objs = client.get_region_state_machines("eu-west-2")
    assert objs is not None


if __name__ == "__main__":
    test_init_client()
    test_get_all_state_machines()
    test_get_region_state_machines()

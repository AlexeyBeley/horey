import os
import sys

from horey.aws_api.aws_clients.athena_client import AthenaClient
import pdb
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.common_utils.common_utils import CommonUtils

configuration_values_file_full_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py"
)
logger = get_logger(
    configuration_values_file_full_path=configuration_values_file_full_path
)

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
AWSAccount.set_aws_region(Region.get_region("eu-central-1"))

accounts["1111"].regions["us-east-1"] = Region.get_region("us-east-1")
accounts["1111"].regions["eu-central-1"] = Region.get_region("eu-central-1")

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


def test_init_athena_client():
    assert isinstance(AthenaClient(), AthenaClient)


def test_get():
    AthenaClient().get_all_template_entities()
    assert isinstance(AthenaClient(), AthenaClient)


if __name__ == "__main__":
    test_init_athena_client()

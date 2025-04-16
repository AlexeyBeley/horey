"""
Test aws ssm client.

"""

import os

from horey.aws_api.aws_clients.ssm_client import SSMClient
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.common_utils.common_utils import CommonUtils

configuration_values_file_full_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py"
)
logger = get_logger(
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
#AWSAccount.set_aws_account(accounts["1111"])
#AWSAccount.set_aws_region(accounts["1111"].regions["us-west-2"])


def test_init_client():
    """
    Base init check.

    @return:
    """

    assert isinstance(SSMClient(), SSMClient)


def test_get_region_recommended_ecs_linux_2():
    """
    Get single parameter from region.

    :return:
    """

    client = SSMClient()
    param = client.get_region_parameter("us-west-2", "/aws/service/ecs/optimized-ami/amazon-linux-2/recommended")
    param.print()
    assert param is not None



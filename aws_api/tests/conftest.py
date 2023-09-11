"""
Common configuration for pytest.

"""

import os
import pytest
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.common_utils.common_utils import CommonUtils


@pytest.fixture(scope="session", autouse=True)
def activate_account():
    """
    Connect to AWS API account.

    :return:
    """
    print("Autouse triggered")
    accounts_file_full_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore",
            "accounts",
            "aws_managed_accounts.py",
        )
    )
    accounts = CommonUtils.load_object_from_module(accounts_file_full_path, "main")
    #AWSAccount.set_aws_account(accounts["full_ro_access"])
    #AWSAccount.set_aws_region(accounts["full_ro_access"].regions["us-west-2"])

    AWSAccount.set_aws_account(accounts["development"])
    AWSAccount.set_aws_region(accounts["development"].regions["us-west-2"])

"""
Testing AWS Cleaner

"""
import os
import pytest

from horey.aws_access_manager.aws_access_manager import AWSAccessManager
from horey.common_utils.common_utils import CommonUtils
from horey.aws_access_manager.aws_access_manager_configuration_policy import (
    AWSAccessManagerConfigurationPolicy,
)

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "access_manager", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

# pylint: disable= missing-function-docstring

@pytest.fixture(name="configuration")
def fixture_configuration():
    """
    Fixture used as a base config.

    :return:
    """

    _configuration = AWSAccessManagerConfigurationPolicy()
    _configuration.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
    _configuration.aws_api_account_name = "iam_manager"
    _configuration.managed_accounts_file_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore",
            "accounts",
            "aws_managed_accounts.py",
        )
    )

    return _configuration


@pytest.mark.wip
def test_get_aws_api_accounts(configuration: AWSAccessManagerConfigurationPolicy):
    ret = AWSAccessManager(configuration).get_user_assume_roles(mock_values["get_user_faces_user_name"])
    assert len(ret) > 0

"""
Testing AWS Cleaner

"""

import os
import pytest

from horey.aws_cleaner.aws_cleaner import AWSCleaner
from horey.aws_cleaner.aws_cleaner_configuration_policy import (
    AWSCleanerConfigurationPolicy,
)


configuration = AWSCleanerConfigurationPolicy()
configuration.aws_api_account_name = "cleaner"
configuration.managed_accounts_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "aws_managed_accounts.py",
    )
)

# pylint: disable=missing-function-docstring

@pytest.mark.done
def test_init_aws_cleaner():
    """
    Test initiation.

    @return:
    """

    assert isinstance(AWSCleaner(configuration), AWSCleaner)


@pytest.mark.wip
def test_init_ec2_volumes():
    """
    Test initiation.

    @return:
    """

    cleaner = AWSCleaner(configuration)
    cleaner.init_ec2_volumes()
    assert len(cleaner.aws_api.ec2_volumes) > 0

@pytest.mark.todo
def test_cleanup_report_ebs_volumes():
    pass

@pytest.mark.todo
def test_cleanup_report_ebs_volumes_in_use():
    pass

@pytest.mark.todo
def test_cleanup_report_ebs_volumes_sizes():
    pass

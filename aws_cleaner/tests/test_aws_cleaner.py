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
configuration.reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
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


@pytest.mark.done
def test_init_ec2_volumes():
    """
    Test initiation.

    @return:
    """

    cleaner = AWSCleaner(configuration)
    cleaner.init_ec2_volumes()
    assert len(cleaner.aws_api.ec2_volumes) > 0


@pytest.mark.done
def test_cleanup_report_ebs_volumes_in_use():
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_ebs_volumes_in_use()
    assert len(cleaner.aws_api.ec2_volumes) > 0
    assert ret is not None


@pytest.mark.done
def test_cleanup_report_ebs_volumes_sizes():
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_ebs_volumes_sizes()
    assert len(cleaner.aws_api.ec2_volumes) > 0
    assert ret is not None


@pytest.mark.done
def test_cleanup_report_ebs_volumes_types():
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_ebs_volumes_types()
    assert len(cleaner.aws_api.ec2_volumes) > 0
    assert ret is not None


@pytest.mark.wip
def test_cleanup_report_ebs_volumes():
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_ebs_volumes()
    assert len(cleaner.aws_api.ec2_volumes) > 0
    assert ret is not None
    assert os.path.exists(configuration.ec2_ebs_report_file_path)

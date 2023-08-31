"""
Testing AWS Cleaner

"""

import os
import pytest

from horey.aws_cleaner.aws_cleaner import AWSCleaner
from horey.aws_cleaner.aws_cleaner_configuration_policy import (
    AWSCleanerConfigurationPolicy,
)


@pytest.fixture(name="configuration")
def fixture_configuration():
    """
    Fixture used as a base config.

    :return:
    """

    _configuration = AWSCleanerConfigurationPolicy()
    _configuration.reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    _configuration.aws_api_account_name = "cleaner"
    _configuration.managed_accounts_file_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "aws_managed_accounts.py",
        )
    )
    return _configuration


@pytest.fixture(name="configuration_generate_permissions")
def fixture_configuration_generate_permissions(configuration):
    """
    Set all cleanup_report values to False

    :return:
    """
    for attr in configuration.__dict__:
        if attr.startswith("_cleanup_report_"):
            setattr(configuration, attr, False)
    return configuration


# pylint: disable=missing-function-docstring

@pytest.mark.done
def test_init_aws_cleaner(configuration):
    """
    Test initiation.

    @return:
    """

    assert isinstance(AWSCleaner(configuration), AWSCleaner)


@pytest.mark.done
def test_init_ec2_volumes(configuration):
    """
    Test initiation.

    @return:
    """

    cleaner = AWSCleaner(configuration)
    cleaner.init_ec2_volumes()
    assert len(cleaner.aws_api.ec2_volumes) > 0


@pytest.mark.done
def test_cleanup_report_ebs_volumes_in_use(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_ebs_volumes_in_use()
    assert len(cleaner.aws_api.ec2_volumes) > 0
    assert ret is not None


@pytest.mark.done
def test_cleanup_report_ebs_volumes_sizes(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_ebs_volumes_sizes()
    assert len(cleaner.aws_api.ec2_volumes) > 0
    assert ret is not None


@pytest.mark.done
def test_cleanup_report_ebs_volumes_types(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_ebs_volumes_types()
    assert len(cleaner.aws_api.ec2_volumes) > 0
    assert ret is not None


@pytest.mark.done
def test_cleanup_report_ebs_volumes(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_ebs_volumes()
    assert len(cleaner.aws_api.ec2_volumes) > 0
    assert ret is not None
    assert os.path.exists(configuration.ec2_ebs_report_file_path)


@pytest.mark.wip
def test_generate_permissions_cleanup_report_ebs_volumes(
        configuration_generate_permissions: AWSCleanerConfigurationPolicy):
    configuration_generate_permissions.cleanup_report_ebs_volumes = True

    cleaner = AWSCleaner(configuration_generate_permissions)
    ret = cleaner.generate_permissions()
    assert ret == {"Version": "2012-10-17", "Statement": [
        {"Sid": "DescribeVolumes", "Effect": "Allow", "Action": "ec2:DescribeVolumes", "Resource": "*"}]}


@pytest.mark.done
def test_init_acm_certificates(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_acm_certificates()
    assert len(cleaner.aws_api.acm_certificates) > 0


@pytest.mark.done
def test_init_hosted_zones(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_hosted_zones()
    assert len(cleaner.aws_api.hosted_zones) > 0


@pytest.mark.wip
def test_generate_permissions_cleanup_report_route53_certificates(
        configuration_generate_permissions: AWSCleanerConfigurationPolicy):
    configuration_generate_permissions.cleanup_report_route53_certificates = True

    cleaner = AWSCleaner(configuration_generate_permissions)
    ret = cleaner.generate_permissions()
    assert ret["Statement"][:2] == [
        {"Sid": "Route53", "Effect": "Allow", "Action": ["route53:ListHostedZones", "route53:ListResourceRecordSets"],
         "Resource": "*"},
        {"Sid": "ListCertificates", "Effect": "Allow", "Action": "acm:ListCertificates", "Resource": "*"}]
    del ret["Statement"][2]["Resource"]
    assert ret["Statement"][2] == {'Sid': 'DescribeCertificate', 'Effect': 'Allow', 'Action': 'acm:DescribeCertificate'}

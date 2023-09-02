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
    _configuration.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
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
def test_init_ec2_network_interfaces(configuration):
    """
    Test initiation.

    @return:
    """

    cleaner = AWSCleaner(configuration)
    cleaner.init_ec2_network_interfaces()
    assert len(cleaner.aws_api.network_interfaces) > 0


@pytest.mark.done
def test_sub_cleanup_report_ebs_volumes_in_use(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_report_ebs_volumes_in_use()
    assert len(cleaner.aws_api.ec2_volumes) > 0
    assert ret is not None


@pytest.mark.done
def test_sub_cleanup_report_ebs_volumes_sizes(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_report_ebs_volumes_sizes()
    assert len(cleaner.aws_api.ec2_volumes) > 0
    assert ret is not None


@pytest.mark.done
def test_sub_cleanup_report_ebs_volumes_types(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_report_ebs_volumes_types()
    assert len(cleaner.aws_api.ec2_volumes) > 0
    assert ret is not None


@pytest.mark.done
def test_cleanup_report_ebs_volumes(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_ebs_volumes()
    assert len(cleaner.aws_api.ec2_volumes) > 0
    assert ret is not None
    assert os.path.exists(configuration.ec2_ebs_report_file_path)


@pytest.mark.done
def test_cleanup_report_acm_certificate(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_acm_certificate()
    assert len(cleaner.aws_api.acm_certificates) > 0
    assert ret is not None
    assert os.path.exists(configuration.acm_certificate_report_file_path)

@pytest.mark.wip
def test_cleanup_report_lambdas(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_lambdas()
    assert len(cleaner.aws_api.lambdas) > 0
    assert ret is not None
    assert os.path.exists(configuration.lambda_report_file_path)

@pytest.mark.done
def test_cleanup_report_network_interfaces(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_network_interfaces()
    assert len(cleaner.aws_api.network_interfaces) > 0
    assert ret is not None
    assert os.path.exists(configuration.ec2_interfaces_report_file_path)

@pytest.mark.done
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


@pytest.mark.done
def test_init_load_balancers(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_load_balancers()
    assert len(cleaner.aws_api.load_balancers) > 1


@pytest.mark.done
def test_init_security_groups(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_security_groups()
    assert len(cleaner.aws_api.security_groups) > 1


@pytest.mark.done
def test_init_lambdas(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_lambdas()
    assert len(cleaner.aws_api.lambdas) > 1


@pytest.mark.done
def test_init_cloud_watch_log_groups(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_cloud_watch_log_groups()
    assert len(cleaner.aws_api.cloud_watch_log_groups) > 1


@pytest.mark.done
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
    assert ret["Statement"][2] == {"Sid": "DescribeCertificate", "Effect": "Allow", "Action": "acm:DescribeCertificate"}


@pytest.mark.done
def test_generate_permissions_cleanup_report_route53_loadbalancers(
        configuration_generate_permissions: AWSCleanerConfigurationPolicy):
    configuration_generate_permissions.cleanup_report_route53_loadbalancers = True

    cleaner = AWSCleaner(configuration_generate_permissions)
    ret = cleaner.generate_permissions()
    assert ret["Statement"] == [
        {"Sid": "Route53", "Effect": "Allow", "Action": ["route53:ListHostedZones", "route53:ListResourceRecordSets"],
         "Resource": "*"},
        {"Sid": "LoadBalancers", "Effect": "Allow",
         "Action": ["elasticloadbalancing:DescribeLoadBalancers",
                    "elasticloadbalancing:DescribeListeners", "elasticloadbalancing:DescribeRules",
                    "elasticloadbalancing:DescribeTags"], "Resource": "*"}]


@pytest.mark.done
def test_generate_permissions_cleanup_report_lambdas(
        configuration_generate_permissions: AWSCleanerConfigurationPolicy):
    configuration_generate_permissions.cleanup_report_lambdas = True

    cleaner = AWSCleaner(configuration_generate_permissions)
    ret = cleaner.generate_permissions()
    del ret["Statement"][1]["Resource"]
    del ret["Statement"][4]["Resource"]
    assert ret["Statement"] == [{"Sid": "GetFunctions", "Effect": "Allow",
                                 "Action": ["lambda:ListFunctions", "lambda:GetFunctionConcurrency"], "Resource": "*"},
                                {"Sid": "LambdaGetPolicy", "Effect": "Allow", "Action": "lambda:GetPolicy"},
                                {"Sid": "DescribeSecurityGroups", "Effect": "Allow", "Action": "ec2:DescribeSecurityGroup", "Resource": "*"},
                                {"Sid": "CloudwatchLogs", "Effect": "Allow", "Action": ["logs:DescribeLogGroups"], "Resource": "*"},
                                {"Sid": "CloudwatchLogTags", "Effect": "Allow", "Action": "logs:ListTagsForResource"}]

@pytest.mark.done
def test_sub_cleanup_report_lambdas_large_size(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_report_lambdas_large_size()
    assert len(cleaner.aws_api.lambdas) > 0
    assert ret is not None

@pytest.mark.done
def test_sub_cleanup_report_lambdas_deprecate(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_report_lambdas_deprecate()
    assert len(cleaner.aws_api.lambdas) > 0
    assert ret is not None

@pytest.mark.done
def test_sub_cleanup_report_lambdas_security_group(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_report_lambdas_security_group()
    assert len(cleaner.aws_api.lambdas) > 0
    assert ret is not None


@pytest.mark.done
def test_sub_cleanup_report_lambdas_old_code(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_report_lambdas_old_code()
    assert len(cleaner.aws_api.lambdas) > 0
    assert ret is not None


@pytest.mark.wip
def test_cleanup_reports_in_aws_cleaner_match_configuration_policy_cleanup_reports():
    """

    :return:
    """
    config_cleanup_report_attrs = [attr_name for attr_name in AWSCleanerConfigurationPolicy.__dict__ if
                                   attr_name.startswith("cleanup_report_")]
    cleaner_cleanup_report_attrs = [attr_name for attr_name in AWSCleaner.__dict__ if
                                    attr_name.startswith("cleanup_report_")]

    # assert set(config_cleanup_report_attrs) == set(cleaner_cleanup_report_attrs)
    for x in cleaner_cleanup_report_attrs:
        if x not in config_cleanup_report_attrs:
            print(f"""\n        self._{x} = None
    @property
    def {x}(self):
    if self._{x} is None:
        self._{x} = True
    return self._{x}

    @{x}.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def {x}(self, value):
    self._{x} = value
    """)

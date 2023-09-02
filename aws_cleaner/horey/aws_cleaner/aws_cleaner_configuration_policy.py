"""
Alert system configuration policy.

"""
import os
from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable=missing-function-docstring


class AWSCleanerConfigurationPolicy(ConfigurationPolicy):
    """
    Main class.

    """

    def __init__(self):
        super().__init__()
        self._reports_dir = None
        self._cache_dir = None
        self._aws_api_account_name = None
        self._managed_accounts_file_path = None
        self._cleanup_report_route53_loadbalancers = None
        self._cleanup_report_route53_certificates = None
        self._cleanup_report_ebs_volumes = None
        self._cleanup_report_ec2_ami_version = None
        self._cleanup_report_acm_certificate = None
        self._cleanup_report_lambdas = None

    @property
    def cleanup_report_lambdas(self):
        if self._cleanup_report_lambdas is None:
            self._cleanup_report_lambdas = True

        return self._cleanup_report_lambdas

    @cleanup_report_lambdas.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def cleanup_report_lambdas(self, value):
        self._cleanup_report_lambdas = value

    @property
    def cleanup_report_acm_certificate(self):
        if self._cleanup_report_acm_certificate is None:
            self._cleanup_report_acm_certificate = True

        return self._cleanup_report_acm_certificate

    @cleanup_report_acm_certificate.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def cleanup_report_acm_certificate(self, value):
        self._cleanup_report_acm_certificate = value

    @property
    def cleanup_report_ec2_ami_version(self):
        if self._cleanup_report_ec2_ami_version is None:
            self._cleanup_report_ec2_ami_version = True
        return self._cleanup_report_ec2_ami_version

    @cleanup_report_ec2_ami_version.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def cleanup_report_ec2_ami_version(self, value):
        self._cleanup_report_ec2_ami_version = value

    @property
    def cleanup_report_ebs_volumes(self):
        if self._cleanup_report_ebs_volumes is None:
            self._cleanup_report_ebs_volumes = True
        return self._cleanup_report_ebs_volumes

    @cleanup_report_ebs_volumes.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def cleanup_report_ebs_volumes(self, value):
        self._cleanup_report_ebs_volumes = value

    @property
    def managed_accounts_file_path(self):
        return self._managed_accounts_file_path

    @managed_accounts_file_path.setter
    def managed_accounts_file_path(self, value):
        self._managed_accounts_file_path = value

    @property
    def aws_api_account_name(self):
        return self._aws_api_account_name

    @aws_api_account_name.setter
    def aws_api_account_name(self, value):
        self._aws_api_account_name = value

    @property
    def cleanup_report_route53_certificates(self):
        if self._cleanup_report_route53_certificates is None:
            self._cleanup_report_route53_certificates = True
        return self._cleanup_report_route53_certificates

    @cleanup_report_route53_certificates.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def cleanup_report_route53_certificates(self, value):
        self._cleanup_report_route53_certificates = value

    @property
    def cleanup_report_route53_loadbalancers(self):
        if self._cleanup_report_route53_loadbalancers is None:
            self._cleanup_report_route53_loadbalancers = True
        return self._cleanup_report_route53_loadbalancers

    @cleanup_report_route53_loadbalancers.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def cleanup_report_route53_loadbalancers(self, value):
        self._cleanup_report_route53_loadbalancers = value

    @property
    def reports_dir(self):
        return self._reports_dir

    @reports_dir.setter
    def reports_dir(self, value):
        if not isinstance(value, str):
            raise ValueError()
        self._reports_dir = value
        if not os.path.exists(value):
            os.makedirs(value, exist_ok=True)

    @property
    def ec2_reports_dir(self):
        ret = os.path.join(self.reports_dir, "ec2")
        if not os.path.exists(ret):
            os.makedirs(ret, exist_ok=True)
        return ret

    @property
    def ec2_ebs_report_file_path(self):
        return os.path.join(self.ec2_reports_dir, "ebs.txt")

    @property
    def ec2_interfaces_report_file_path(self):
        return os.path.join(self.ec2_reports_dir, "enis.txt")

    @property
    def route53_reports_dir(self):
        ret = os.path.join(self.reports_dir, "route53")
        if not os.path.exists(ret):
            os.makedirs(ret, exist_ok=True)
        return ret

    @property
    def route53_report_file_path(self):
        return os.path.join(self.route53_reports_dir, "route53.txt")

    @property
    def acm_reports_dir(self):
        ret = os.path.join(self.reports_dir, "acm")
        if not os.path.exists(ret):
            os.makedirs(ret, exist_ok=True)
        return ret

    @property
    def acm_certificate_report_file_path(self):
        return os.path.join(self.acm_reports_dir, "acm_certificate.txt")

    @property
    def lambda_reports_dir(self):
        ret = os.path.join(self.reports_dir, "lambda")
        if not os.path.exists(ret):
            os.makedirs(ret, exist_ok=True)
        return ret

    @property
    def lambda_report_file_path(self):
        return os.path.join(self.lambda_reports_dir, "lambdas.txt")

    @property
    def cache_dir(self):
        return self._cache_dir

    @cache_dir.setter
    def cache_dir(self, value):
        if not isinstance(value, str):
            raise ValueError()
        self._cache_dir = value
        if not os.path.exists(value):
            os.makedirs(value, exist_ok=True)

    @property
    def cloudwatch_log_groups_streams_cache_dir(self):
        return os.path.join(self.cache_dir, "cloudwatch", "streams")

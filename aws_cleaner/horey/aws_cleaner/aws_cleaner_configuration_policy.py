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
        self._aws_api_account_name = None
        self._managed_accounts_file_path = None
        self._cleanup_report_ebs_volumes = None
        self._cleanup_report_route53_loadbalancers = None
        self._cleanup_report_route53_certificates = None

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
    def route53_reports_dir(self):
        ret = os.path.join(self.reports_dir, "route53")
        if not os.path.exists(ret):
            os.makedirs(ret, exist_ok=True)
        return ret

    @property
    def route53_report_file_path(self):
        return os.path.join(self.route53_reports_dir, "route53.txt")

"""
Alert system configuration policy.

"""
import os
from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable=missing-function-docstring, too-many-instance-attributes

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
        self._cleanup_report_ec2_instances = None
        self._cleanup_report_acm_certificate = None
        self._cleanup_report_lambdas = None
        self._cleanup_report_network_interfaces = None
        self._cleanup_report_ecr_images = None
        self._cleanup_report_security_groups = None
        self._cleanup_report_load_balancers = None
        self._cleanup_report_sqs = None
        self._cleanup_report_cloudwatch_logs = None
        self._cleanup_report_elasticache = None
        self._cleanup_report_rds = None
        self._cleanup_report_dynamodb = None

    @property
    def cleanup_report_dynamodb(self):
        if self._cleanup_report_dynamodb is None:
            self._cleanup_report_dynamodb = True
        return self._cleanup_report_dynamodb

    @cleanup_report_dynamodb.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def cleanup_report_dynamodb(self, value):
        self._cleanup_report_dynamodb = value

    @property
    def cleanup_report_rds(self):
        if self._cleanup_report_rds is None:
            self._cleanup_report_rds = True
        return self._cleanup_report_rds

    @cleanup_report_rds.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def cleanup_report_rds(self, value):
        self._cleanup_report_rds = value

    @property
    def cleanup_report_elasticache(self):
        if self._cleanup_report_elasticache is None:
            self._cleanup_report_elasticache = True
        return self._cleanup_report_elasticache

    @cleanup_report_elasticache.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def cleanup_report_elasticache(self, value):
        self._cleanup_report_elasticache = value

    @property
    def cleanup_report_cloudwatch_logs(self):
        if self._cleanup_report_cloudwatch_logs is None:
            self._cleanup_report_cloudwatch_logs = True
        return self._cleanup_report_cloudwatch_logs

    @cleanup_report_cloudwatch_logs.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def cleanup_report_cloudwatch_logs(self, value):
        self._cleanup_report_cloudwatch_logs = value


    @property
    def cleanup_report_sqs(self):
        if self._cleanup_report_sqs is None:
            self._cleanup_report_sqs = True
        return self._cleanup_report_sqs

    @cleanup_report_sqs.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def cleanup_report_sqs(self, value):
        self._cleanup_report_sqs = value

    @property
    def cleanup_report_load_balancers(self):
        if self._cleanup_report_load_balancers is None:
            self._cleanup_report_load_balancers = True
        return self._cleanup_report_load_balancers

    @cleanup_report_load_balancers.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def cleanup_report_load_balancers(self, value):
        self._cleanup_report_load_balancers = value

    @property
    def cleanup_report_security_groups(self):
        if self._cleanup_report_security_groups is None:
            self._cleanup_report_security_groups = True
        return self._cleanup_report_security_groups

    @cleanup_report_security_groups.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def cleanup_report_security_groups(self, value):
        self._cleanup_report_security_groups = value

    @property
    def cleanup_report_ecr_images(self):
        if self._cleanup_report_ecr_images is None:
            self._cleanup_report_ecr_images = True
        return self._cleanup_report_ecr_images

    @cleanup_report_ecr_images.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def cleanup_report_ecr_images(self, value):
        self._cleanup_report_ecr_images = value

    @property
    def cleanup_report_network_interfaces(self):
        if self._cleanup_report_network_interfaces is None:
            self._cleanup_report_network_interfaces = True
        return self._cleanup_report_network_interfaces

    @cleanup_report_network_interfaces.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def cleanup_report_network_interfaces(self, value):
        self._cleanup_report_network_interfaces = value

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
    def cleanup_report_ec2_instances(self):
        if self._cleanup_report_ec2_instances is None:
            self._cleanup_report_ec2_instances = True
        return self._cleanup_report_ec2_instances

    @cleanup_report_ec2_instances.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def cleanup_report_ec2_instances(self, value):
        self._cleanup_report_ec2_instances = value

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
    def permissions_file_path(self):
        return os.path.join(self.reports_dir, "permissions_policy.json")

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
    def ec2_instances_report_file_path(self):
        return os.path.join(self.ec2_reports_dir, "instances.txt")

    @property
    def ec2_interfaces_report_file_path(self):
        return os.path.join(self.ec2_reports_dir, "enis.txt")

    @property
    def ec2_security_groups_report_file_path(self):
        return os.path.join(self.ec2_reports_dir, "security_groups.txt")

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
    def load_balancer_reports_dir(self):
        ret = os.path.join(self.reports_dir, "load_balancer")
        if not os.path.exists(ret):
            os.makedirs(ret, exist_ok=True)
        return ret

    @property
    def load_balancer_report_file_path(self):
        return os.path.join(self.load_balancer_reports_dir, "load_balancers.txt")

    @property
    def ecr_reports_dir(self):
        ret = os.path.join(self.reports_dir, "ecr")
        if not os.path.exists(ret):
            os.makedirs(ret, exist_ok=True)
        return ret

    @property
    def ecr_report_file_path(self):
        return os.path.join(self.ecr_reports_dir, "ecr_images.txt")

    @property
    def dynamodb_reports_dir(self):
        ret = os.path.join(self.reports_dir, "dynamodb")
        if not os.path.exists(ret):
            os.makedirs(ret, exist_ok=True)
        return ret

    @property
    def dynamodb_report_file_path(self):
        return os.path.join(self.dynamodb_reports_dir, "dynamodb.txt")

    @property
    def rds_reports_dir(self):
        ret = os.path.join(self.reports_dir, "rds")
        if not os.path.exists(ret):
            os.makedirs(ret, exist_ok=True)
        return ret

    @property
    def rds_report_file_path(self):
        return os.path.join(self.rds_reports_dir, "rds.txt")

    @property
    def elasticsearch_domains_reports_dir(self):
        ret = os.path.join(self.reports_dir, "elasticsearch_domains")
        if not os.path.exists(ret):
            os.makedirs(ret, exist_ok=True)
        return ret

    @property
    def elasticsearch_domains_report_file_path(self):
        return os.path.join(self.elasticsearch_domains_reports_dir, "elasticsearch_domains.txt")

    @property
    def elasticache_clusters_reports_dir(self):
        ret = os.path.join(self.reports_dir, "elasticache_clusters")
        if not os.path.exists(ret):
            os.makedirs(ret, exist_ok=True)
        return ret

    @property
    def elasticache_report_file_path(self):
        return os.path.join(self.elasticache_clusters_reports_dir, "elasticache.txt")

    @property
    def cloudwatch_logs_reports_dir(self):
        ret = os.path.join(self.reports_dir, "cloudwatch_logs")
        if not os.path.exists(ret):
            os.makedirs(ret, exist_ok=True)
        return ret

    @property
    def cloud_watch_report_file_path(self):
        return os.path.join(self.cloudwatch_logs_reports_dir, "cloudwatch.txt")

    @property
    def sqs_reports_dir(self):
        ret = os.path.join(self.reports_dir, "sqs")
        if not os.path.exists(ret):
            os.makedirs(ret, exist_ok=True)
        return ret

    @property
    def sqs_report_file_path(self):
        return os.path.join(self.sqs_reports_dir, "sqs.txt")

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

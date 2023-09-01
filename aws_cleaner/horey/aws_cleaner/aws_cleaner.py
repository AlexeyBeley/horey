"""
AWS Cleaner. Money, money, money...

"""
import datetime
# pylint: disable=no-name-in-module
from collections import defaultdict
from horey.h_logger import get_logger
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.aws_cleaner.aws_cleaner_configuration_policy import AWSCleanerConfigurationPolicy
from horey.common_utils.text_block import TextBlock
from horey.aws_api.base_entities.aws_account import AWSAccount

logger = get_logger()


class AWSCleaner:
    """
    Alert system management class.

    """

    def __init__(self, configuration: AWSCleanerConfigurationPolicy):
        self.configuration = configuration

        aws_api_configuration = AWSAPIConfigurationPolicy()
        aws_api_configuration.accounts_file = self.configuration.managed_accounts_file_path
        aws_api_configuration.aws_api_account= self.configuration.aws_api_account_name
        self.aws_api = AWSAPI(aws_api_configuration)

    def init_ec2_volumes(self):
        """
        Init EC2 EBS volumes.

        :return:
        """

        if not self.aws_api.ec2_volumes:
            self.aws_api.init_ec2_volumes()

    def init_ec2_instances(self):
        """
        Init EC2 instances.

        :return:
        """

        if not self.aws_api.ec2_instances:
            self.aws_api.init_ec2_instances()

    def init_hosted_zones(self):
        """
        Init Route 53 hosted zones.

        :return:
        """

        if not self.aws_api.hosted_zones:
            self.aws_api.init_hosted_zones()

    def init_acm_certificates(self):
        """
        Init ACM certificates.

        :return:
        """

        if not self.aws_api.acm_certificates:
            self.aws_api.init_acm_certificates()

    def init_load_balancers(self):
        """
        Init ACM certificates.

        :return:
        """

        if not self.aws_api.load_balancers and not self.aws_api.classic_load_balancers:
            self.aws_api.init_load_balancers()
            self.aws_api.init_classic_load_balancers()

    def generate_permissions(self):
        """
        Generate iam permissions.
        https://iam.cloudonaut.io/

        :return:
        """

        statements = []
        if self.configuration.cleanup_report_ebs_volumes:
            statement_generator = self.statement_describe_volumes
            if statement_generator not in statements:
                statements.append(statement_generator)
        if self.configuration.cleanup_report_route53_certificates:
            for statement_generator in [self.statement_route53_list, self.statement_acm_describe]:
                if statement_generator not in statements:
                    statements.append(statement_generator)
        if self.configuration.cleanup_report_route53_loadbalancers:
            for statement_generator in [self.statement_route53_list, self.statement_loadbalancers]:
                if statement_generator not in statements:
                    statements.append(statement_generator)

        return {"Version": "2012-10-17",
                  "Statement": [statement for statement_generator in statements for statement in statement_generator()]}

    @staticmethod
    def statement_route53_list():
        """
        Route 53 permissions.

        :return:
        """

        return [{
            "Sid": "Route53",
            "Effect": "Allow",
            "Action": [
                "route53:ListHostedZones",
                "route53:ListResourceRecordSets"
            ],
            "Resource": "*"
        }]

    def statement_acm_describe(self):
        """
        ACM Permissions.

        :return:
        """

        return [{
            "Sid": "ListCertificates",
            "Effect": "Allow",
            "Action": "acm:ListCertificates",
            "Resource": "*"
        },
        *[{
            "Sid": "DescribeCertificate",
            "Effect": "Allow",
            "Action": "acm:DescribeCertificate",
            "Resource": f"arn:aws:acm:{self.aws_api.acm_client.account_id}:{region.region_mark}:certificate/*"
        } for region in AWSAccount.get_aws_account().regions.values()]]

    @staticmethod
    def statement_loadbalancers():
        """
        Load balancers Permissions.

        :return:
        """
        return [{
            "Sid": "LoadBalancers",
            "Effect": "Allow",
            "Action": [
                "elasticloadbalancing:DescribeLoadBalancers",
                "elasticloadbalancing:DescribeListeners",
                "elasticloadbalancing:DescribeRules",
                "elasticloadbalancing:DescribeTags"
            ],
            "Resource": "*"
        }]

    @staticmethod
    def statement_describe_volumes():
        """
        Volumes.

        :return:
        """

        return [{
            "Sid": "DescribeVolumes",
            "Effect": "Allow",
            "Action": "ec2:DescribeVolumes",
            "Resource": "*"
        }]

    def cleanup_report_ebs_volumes(self):
        """
        Generate cleanup report for Volumes

        :return:
        """

        tb_ret = TextBlock("EBS Volumes Report")
        tb_ret_tmp = self.sub_cleanup_report_ebs_volumes_in_use()
        if tb_ret_tmp.blocks or tb_ret_tmp.lines:
            tb_ret.blocks.append(tb_ret_tmp)
        tb_ret_tmp = self.sub_cleanup_report_ebs_volumes_types()
        tb_ret.blocks.append(tb_ret_tmp)
        tb_ret_tmp = self.sub_cleanup_report_ebs_volumes_sizes()
        tb_ret.blocks.append(tb_ret_tmp)
        with open(self.configuration.ec2_ebs_report_file_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        logger.info(f"Output in: {self.configuration.ec2_ebs_report_file_path}")
        return tb_ret

    def sub_cleanup_report_ebs_volumes_in_use(self):
        """
        Check volumes not in use

        :return:
        """

        self.init_ec2_volumes()

        tb_ret = TextBlock("EBS Volumes not in use")
        for volume in self.aws_api.ec2_volumes:
            if volume.state == "in-use":
                continue
            try:
                name = volume.get_tagname()
            except RuntimeError as exception_instance:
                if "No tag" not in repr(exception_instance):
                    raise
                name = volume.id
            tb_ret.lines.append(f"{name}: {volume}")
        return tb_ret

    def sub_cleanup_report_ebs_volumes_sizes(self):
        """
        Generate EBS Volume sizes

        :return:
        """

        self.init_ec2_volumes()

        tb_ret = TextBlock("EBS Volumes' sizes")
        for volume in sorted(self.aws_api.ec2_volumes, key=lambda vol: vol.size, reverse=True):
            try:
                name = volume.get_tagname()
            except RuntimeError as exception_instance:
                if "No tag" not in repr(exception_instance):
                    raise
                name = volume.id

            try:
                attachment_string = volume.attachments[0]['InstanceId']
            except IndexError:
                attachment_string = "Not-attached"

            tb_ret.lines.append(
                f"{volume.availability_zone}, {name}, {volume.volume_type}, {volume.size}GB, {volume.iops}IOPS, Attached:{attachment_string}")
        return tb_ret

    def sub_cleanup_report_ebs_volumes_types(self):
        """
        Generate EBS Volume sizes by type.

        :return:
        """

        self.init_ec2_volumes()

        tb_ret = TextBlock("Storage used by type")
        dict_total_size_to_volume_type = defaultdict(int)
        dict_sizes_counter = defaultdict(int)

        for volume in self.aws_api.ec2_volumes:
            dict_total_size_to_volume_type[volume.volume_type] += volume.size
            dict_sizes_counter[volume.size] += 1

        for size, counter in sorted(dict_sizes_counter.items(),
                                    key=lambda size_counter: size_counter[0]*size_counter[1],
                                    reverse=True):
            tb_ret.lines.append(
                f"Volume size: {size} GB, Volumes count: {counter} [= {size*counter} GB]")

        add_gp3_recommendation = False
        for volume_type, size in sorted(dict_total_size_to_volume_type.items(), key=lambda x: x[1]):
            if volume_type == "gp2":
                add_gp3_recommendation = True
            tb_ret.lines.append(
                f"Volume type: {volume_type}, Volumes summary size: {size} GB")

        if add_gp3_recommendation:
            tb_ret.lines.append("Optimization: consider useinf gp3 type instead of gp2.")

        return tb_ret

    def cleanup_route_53(self):
        """
        Clean the Route 53 service.

        :return:
        """

        tb_ret = TextBlock("Route53 Report")
        tb_ret_tmp = self.cleanup_report_route53_certificates()
        if tb_ret_tmp.blocks or tb_ret_tmp.lines:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.cleanup_report_route53_loadbalancers()
        if tb_ret_tmp.blocks or tb_ret_tmp.lines:
            tb_ret.blocks.append(tb_ret_tmp)

        with open(self.configuration.route53_report_file_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        logger.info(f"Output in: {self.configuration.route53_report_file_path}")
        return tb_ret

    def cleanup_report_route53_certificates(self):
        """
        * Expired certificate validation
        * Certificate renew failed.
        * Not existing.
        * Wrong CNAME Value.

        :return:
        """
        self.init_hosted_zones()
        self.init_acm_certificates()
        tb_ret = TextBlock("Route53 Certificate")
        return tb_ret

    def cleanup_report_route53_loadbalancers(self):
        """
        DNS records pointing to missing load balancers.

        :return:
        """
        self.init_load_balancers()
        tb_ret = TextBlock("Route53 Load Balancers")
        return tb_ret

    def cleanup_report_ec2_ami_version(self):
        """
        Check AMI last version of the server.

        :return:
        """
        self.init_ec2_instances()
        tb_ret = TextBlock("AMI")
        return tb_ret

    def cleanup_report_acm_certificate(self):
        """
        ACM Certificates

        :return:
        """
        tb_ret = TextBlock("ACM Report")

        tb_ret_tmp = self.sub_cleanup_report_acm_unused()
        tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_cleanup_report_acm_ineligible()
        tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_cleanup_report_acm_expiration()
        tb_ret.blocks.append(tb_ret_tmp)

        with open(self.configuration.acm_certificate_report_file_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())
        logger.info(f"Output in: {self.configuration.acm_certificate_report_file_path}")
        return tb_ret

    def sub_cleanup_report_acm_unused(self):
        """
        ACM Certificates

        :return:
        """
        self.init_acm_certificates()
        tb_ret = TextBlock("Unused certificates")

        unused = [certificate for certificate in self.aws_api.acm_certificates if not certificate.in_use_by]
        for certificate in unused:
            tb_ret.lines.append(f"[{certificate.domain_name}] {certificate.arn}")
        return tb_ret

    def sub_cleanup_report_acm_ineligible(self):
        """
        ACM ineligible renewal Certificates

        :return:
        """
        self.init_acm_certificates()
        tb_ret = TextBlock("Ineligible certificates")

        for certificate in self.aws_api.acm_certificates:
            if certificate.renewal_eligibility == "INELIGIBLE":
                tb_ret.lines.append(f"[{certificate.domain_name}] {certificate.arn}")
            elif certificate.renewal_eligibility != "ELIGIBLE":
                tb_ret.lines.append(f"Unknown status: '{certificate.renewal_eligibility}' [{certificate.domain_name}] {certificate.arn}")
        return tb_ret

    def sub_cleanup_report_acm_expiration(self):
        """
        ACM expired/expiring Certificates

        :return:
        """
        self.init_acm_certificates()
        tb_ret = TextBlock("Expired/Expiring Certificates")
        for certificate in self.aws_api.acm_certificates:
            now = datetime.datetime.now(tz=certificate.not_after.tzinfo)
            if certificate.not_after < now:
                tb_ret.lines.append(f"Expired: [{certificate.domain_name}] {certificate.arn}")
            elif certificate.not_after < now + datetime.timedelta(days=30):
                days_left = (certificate.not_after - now).days
                tb_ret.lines.append(f"Days left {days_left}: '{certificate.renewal_eligibility}' [{certificate.domain_name}] {certificate.arn}")
        return tb_ret

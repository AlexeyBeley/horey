"""
AWS Cleaner. Money, money, money...

"""
import os
import json
import datetime
# pylint: disable=no-name-in-module
from collections import defaultdict
import requests

from horey.h_logger import get_logger
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.aws_cleaner.aws_cleaner_configuration_policy import AWSCleanerConfigurationPolicy
from horey.common_utils.text_block import TextBlock
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.common_utils.common_utils import CommonUtils

logger = get_logger()


class AWSCleaner:
    """
    Alert system management class.

    """

    def __init__(self, configuration: AWSCleanerConfigurationPolicy):
        self.configuration = configuration

        aws_api_configuration = AWSAPIConfigurationPolicy()
        aws_api_configuration.accounts_file = self.configuration.managed_accounts_file_path
        aws_api_configuration.aws_api_account = self.configuration.aws_api_account_name
        self.aws_api = AWSAPI(aws_api_configuration)

    def init_cloud_watch_log_groups(self, permissions_only=False):
        """
        Init Cloudwatch logs groups

        :return:
        """

        if not permissions_only and not self.aws_api.cloud_watch_log_groups:
            self.aws_api.init_cloud_watch_log_groups()

        return [{
            "Sid": "CloudwatchLogs",
            "Effect": "Allow",
            "Action": [
                "logs:DescribeLogGroups"
            ],
            "Resource": "*"
        },
            *[{
                "Sid": "CloudwatchLogTags",
                "Effect": "Allow",
                "Action": "logs:ListTagsForResource",
                "Resource": f"arn:aws:acm:{region.region_mark}:{self.aws_api.acm_client.account_id}:log-group/*"
            } for region in AWSAccount.get_aws_account().regions.values()]
        ]

    def init_lambdas(self, permissions_only=False):
        """
        Init AWS Lambdas

        :return:
        """

        if not permissions_only and not self.aws_api.lambdas:
            #cache_file = os.path.join(self.configuration.cache_dir, "lambdas.json")
            #self.aws_api.cache_objects(self.aws_api.lambdas, cache_file, indent=4)
            #self.aws_api.init_lambdas(from_cache=True, cache_file=cache_file)
            self.aws_api.init_lambdas()

        return [{
            "Sid": "GetFunctions",
            "Effect": "Allow",
            "Action": ["lambda:ListFunctions", "lambda:GetFunctionConcurrency"],
            "Resource": "*"
        },
            *[{
                "Sid": "LambdaGetPolicy",
                "Effect": "Allow",
                "Action": "lambda:GetPolicy",
                "Resource": f"arn:aws:lambda:{region.region_mark}:{self.aws_api.acm_client.account_id}:function:*"
            } for region in AWSAccount.get_aws_account().regions.values()]]

    def init_security_groups(self, permissions_only=False):
        """
        Init AWS security groups

        :return:
        """

        if not permissions_only and not self.aws_api.security_groups:
            self.aws_api.init_security_groups()

        return [{
            "Sid": "DescribeSecurityGroups",
            "Effect": "Allow",
            "Action": "ec2:DescribeSecurityGroup",
            "Resource": "*"
        }]

    def init_ec2_volumes(self, permissions_only=False):
        """
        Init EC2 EBS volumes.

        :return:
        """

        if not permissions_only and not self.aws_api.ec2_volumes:
            self.aws_api.init_ec2_volumes()

        return [{
            "Sid": "DescribeVolumes",
            "Effect": "Allow",
            "Action": "ec2:DescribeVolumes",
            "Resource": "*"
        }]

    def init_ec2_instances(self, permissions_only=False):
        """
        Init EC2 instances.

        :return:
        """

        if not permissions_only and not self.aws_api.ec2_instances:
            self.aws_api.init_ec2_instances()

        return [{
            "Sid": "DescribeInstances",
            "Effect": "Allow",
            "Action": "ec2:DescribeInstances",
            "Resource": "*"
        }]

    def init_ec2_amis(self, permissions_only=False):
        """
        Init EC2 amis.

        :return:
        """

        if not permissions_only and not self.aws_api.amis:
            self.aws_api.init_amis()

        return [{
            "Sid": "DescribeImages",
            "Effect": "Allow",
            "Action": "ec2:DescribeImages",
            "Resource": "*"
        }]

    def init_hosted_zones(self, permissions_only=False):
        """
        Init Route 53 hosted zones.

        :return:
        """

        if not permissions_only and not self.aws_api.hosted_zones:
            self.aws_api.init_hosted_zones()

        return [{
            "Sid": "Route53",
            "Effect": "Allow",
            "Action": [
                "route53:ListHostedZones",
                "route53:ListResourceRecordSets"
            ],
            "Resource": "*"
        }]

    def init_ec2_network_interfaces(self, permissions_only=False):
        """
        Init AWS ENIs

        :return:
        """

        if not permissions_only and not self.aws_api.network_interfaces:
            self.aws_api.init_network_interfaces()

        return [{
            "Sid": "DescribeNetworkInterfaces",
            "Effect": "Allow",
            "Action": "ec2:DescribeNetworkInterfaces",
            "Resource": "*"
        }]

    def init_acm_certificates(self, permissions_only=False):
        """
        Init ACM certificates.

        :return:
        """

        if not permissions_only and not self.aws_api.acm_certificates:
            self.aws_api.init_acm_certificates()

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
                "Resource": f"arn:aws:acm:{region.region_mark}:{self.aws_api.acm_client.account_id}:certificate/*"
            } for region in AWSAccount.get_aws_account().regions.values()]]

    def init_load_balancers(self, permissions_only=False):
        """
        Init ACM certificates.

        :return:
        """

        if not permissions_only and not self.aws_api.load_balancers and not self.aws_api.classic_load_balancers:
            self.aws_api.init_load_balancers()
            self.aws_api.init_classic_load_balancers()

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

    def get_active_cleanups(self):
        """
        Return All active clean up functions.

        :return:
        """

        lst_ret = []
        for cleanup_report_name in dir(self.configuration):
            if not cleanup_report_name.startswith("cleanup_report"):
                continue

            if getattr(self.configuration, cleanup_report_name):
                lst_ret.append(getattr(self, cleanup_report_name))
        return lst_ret

    def clean(self):
        """
        Run all active cleanup reports.

        :return:
        """

        tb_ret = TextBlock("AWS Cleanup report")
        for report_generator in self.get_active_cleanups():
            report = report_generator()
            if report:
                tb_ret.blocks.append(report)
        return tb_ret

    # pylint: disable= too-many-branches
    def generate_permissions(self):
        """
        Generate iam permissions.
        https://iam.cloudonaut.io/

        :return:
        """
        statements = []
        for report_generator in self.get_active_cleanups():
            statements += report_generator(permissions_only=True)
        unique_statements = []
        for statement in statements:
            if statement not in unique_statements:
                unique_statements.append(statement)
        return {"Version": "2012-10-17",
                "Statement": unique_statements}

    def cleanup_report_ebs_volumes(self, permissions_only=False):
        """
        Generate cleanup report for Volumes

        :return:
        """
        if permissions_only:
            permissions = self.sub_cleanup_report_ebs_volumes_in_use(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_ebs_volumes_types(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_ebs_volumes_sizes(permissions_only=permissions_only)
            return permissions

        tb_ret = TextBlock("EBS Volumes Report")
        tb_ret_tmp = self.sub_cleanup_report_ebs_volumes_in_use()
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)
        tb_ret_tmp = self.sub_cleanup_report_ebs_volumes_types()
        tb_ret.blocks.append(tb_ret_tmp)
        tb_ret_tmp = self.sub_cleanup_report_ebs_volumes_sizes()
        tb_ret.blocks.append(tb_ret_tmp)
        with open(self.configuration.ec2_ebs_report_file_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        logger.info(f"Output in: {self.configuration.ec2_ebs_report_file_path}")
        return tb_ret

    def sub_cleanup_report_ebs_volumes_in_use(self, permissions_only=False):
        """
        Check volumes not in use

        :return:
        """

        permissions = self.init_ec2_volumes(permissions_only=permissions_only)
        if permissions_only:
            return permissions

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

    def sub_cleanup_report_ebs_volumes_sizes(self, permissions_only=False):
        """
        Generate EBS Volume sizes

        :return:
        """

        response = self.init_ec2_volumes(permissions_only=permissions_only)
        if permissions_only:
            return response

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

    def sub_cleanup_report_ebs_volumes_types(self, permissions_only=False):
        """
        Generate EBS Volume sizes by type.

        :return:
        """

        response = self.init_ec2_volumes(permissions_only=permissions_only)
        if permissions_only:
            return response

        tb_ret = TextBlock("Storage used by type")
        dict_total_size_to_volume_type = defaultdict(int)
        dict_sizes_counter = defaultdict(int)

        for volume in self.aws_api.ec2_volumes:
            dict_total_size_to_volume_type[volume.volume_type] += volume.size
            dict_sizes_counter[volume.size] += 1

        for size, counter in sorted(dict_sizes_counter.items(),
                                    key=lambda size_counter: size_counter[0] * size_counter[1],
                                    reverse=True):
            tb_ret.lines.append(
                f"Volume size: {size} GB, Volumes count: {counter} [= {size * counter} GB]")

        add_gp3_recommendation = False
        for volume_type, size in sorted(dict_total_size_to_volume_type.items(), key=lambda x: x[1]):
            if volume_type == "gp2":
                add_gp3_recommendation = True
            tb_ret.lines.append(
                f"Volume type: {volume_type}, Volumes summary size: {size} GB")

        if add_gp3_recommendation:
            tb_ret.lines.append("Optimization: consider useinf gp3 type instead of gp2.")

        return tb_ret

    def cleanup_route_53(self, permissions_only=False):
        """
        Clean the Route 53 service.

        :return:
        """
        if permissions_only:
            permissions = self.cleanup_report_route53_certificates(permissions_only=permissions_only)
            permissions += self.cleanup_report_route53_loadbalancers(permissions_only=permissions_only)
            return permissions

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

    def cleanup_report_route53_certificates(self, permissions_only=False):
        """
        * Expired certificate validation
        * Certificate renew failed.
        * Not existing.
        * Wrong CNAME Value.

        :return:
        """

        permissions = self.init_hosted_zones(permissions_only=permissions_only)
        permissions += self.init_acm_certificates(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("Route53 Certificate")
        return tb_ret

    def cleanup_report_route53_loadbalancers(self, permissions_only=False):
        """
        DNS records pointing to missing load balancers.

        :return:
        """

        permissions = self.init_hosted_zones(permissions_only=permissions_only)
        permissions += self.init_load_balancers(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("Route53 Load Balancers")
        return tb_ret

    def cleanup_report_acm_certificate(self, permissions_only=False):
        """
        ACM Certificates

        :return:
        """

        if permissions_only:
            permissions = self.sub_cleanup_report_acm_unused(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_acm_ineligible(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_acm_expiration(permissions_only=permissions_only)
            return permissions

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

    def sub_cleanup_report_acm_unused(self, permissions_only=False):
        """
        ACM Certificates

        :return:
        """

        permissions = self.init_acm_certificates(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("Unused certificates")

        unused = [certificate for certificate in self.aws_api.acm_certificates if not certificate.in_use_by]
        for certificate in unused:
            tb_ret.lines.append(f"[{certificate.domain_name}] {certificate.arn}")
        return tb_ret

    def sub_cleanup_report_acm_ineligible(self, permissions_only=False):
        """
        ACM ineligible renewal Certificates

        :return:
        """

        permissions = self.init_acm_certificates(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("Renewal ineligible certificates")

        for certificate in self.aws_api.acm_certificates:
            if certificate.renewal_eligibility == "INELIGIBLE":
                tb_ret.lines.append(f"[{certificate.domain_name}] {certificate.arn}")
            elif certificate.renewal_eligibility != "ELIGIBLE":
                tb_ret.lines.append(
                    f"Unknown status: '{certificate.renewal_eligibility}' [{certificate.domain_name}] {certificate.arn}")
        return tb_ret

    def sub_cleanup_report_acm_expiration(self, permissions_only=False):
        """
        ACM expired/expiring Certificates

        :return:
        """

        permissions = self.init_acm_certificates(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("Expired/Expiring Certificates")
        for certificate in self.aws_api.acm_certificates:
            now = datetime.datetime.now(tz=certificate.not_after.tzinfo)
            if certificate.not_after < now:
                tb_ret.lines.append(f"Expired: [{certificate.domain_name}] {certificate.arn}")
            elif certificate.not_after < now + datetime.timedelta(days=30):
                days_left = (certificate.not_after - now).days
                tb_ret.lines.append(
                    f"Days left {days_left}: '{certificate.renewal_eligibility}' [{certificate.domain_name}] {certificate.arn}")
        return tb_ret

    def cleanup_report_network_interfaces(self, permissions_only=False):
        """
        Cleanup report for ec2 interfaces

        :return:
        """

        permissions = self.init_ec2_network_interfaces()
        if permissions_only:
            return permissions

        tb_ret = TextBlock("Unused network interfaces")
        for interface in self.aws_api.network_interfaces:
            if interface.attachment is None:
                tb_ret.lines.append(
                    f"Name: {interface.name}, Private dns name: {interface.private_dns_name}, "
                    f"availability_zone: {interface.availability_zone}, subnet: {interface.subnet_id}"
                )

            if interface.status not in ["available", "in-use"]:
                raise NotImplementedError(interface.status)

        tb_ret.header += f": ({len(tb_ret.lines)})"
        with open(self.configuration.ec2_interfaces_report_file_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())
        logger.info(f"Output in: {self.configuration.ec2_interfaces_report_file_path}")
        return tb_ret

    def cleanup_report_lambdas(self, permissions_only=False):
        """
        Generated various lambdas' cleanup reports.

        @return:
        """
        if permissions_only:
            permissions = self.sub_cleanup_report_lambdas_not_running(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_lambdas_deprecate(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_lambdas_large_size(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_lambdas_security_group(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_lambdas_old_code(permissions_only=permissions_only)
            return permissions

        tb_ret = TextBlock("AWS Lambdas cleanup")
        tb_ret_tmp = self.sub_cleanup_report_lambdas_not_running()
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_cleanup_report_lambdas_deprecate()
        tb_ret.blocks.append(tb_ret_tmp)
        tb_ret_tmp = self.sub_cleanup_report_lambdas_large_size()
        tb_ret.blocks.append(tb_ret_tmp)
        tb_ret_tmp = self.sub_cleanup_report_lambdas_security_group()
        tb_ret.blocks.append(tb_ret_tmp)
        tb_ret_tmp = self.sub_cleanup_report_lambdas_old_code()
        tb_ret.blocks.append(tb_ret_tmp)

        with open(self.configuration.lambda_report_file_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())
        logger.info(f"Output in: {self.configuration.lambda_report_file_path}")

        return tb_ret

    def sub_cleanup_report_lambdas_security_group(self, permissions_only=False):
        """
        Lambda uses external resources, while can not be accessed from the outside itself.
        No need to keep an open port for that. If there is - misconfiguration might have occurred.

        :return:
        """

        permissions = self.init_lambdas(permissions_only=permissions_only)
        permissions += self.init_security_groups(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("Lambdas' security groups report")
        tb_ret_open_ingress = TextBlock(
            "Lambdas with open ingress security groups - no need to open a port into lambda"
        )
        tb_ret_nonexistent_security_groups = TextBlock(
            "Security groups being assigned to lambdas, but were deleted."
        )

        for aws_lambda in self.aws_api.lambdas:
            lst_str_sgs = aws_lambda.get_assinged_security_group_ids()
            for security_group_id in lst_str_sgs:
                lst_security_group = CommonUtils.find_objects_by_values(
                    self.aws_api.security_groups, {"id": security_group_id}, max_count=1
                )
                if len(lst_security_group) == 0:
                    line = f"{aws_lambda.name}: {security_group_id}"
                    tb_ret_nonexistent_security_groups.lines.append(line)
                    continue

                security_group = lst_security_group[0]
                if len(security_group.ip_permissions) > 0:
                    line = f"{aws_lambda.name}: {security_group.name}"
                    tb_ret_open_ingress.lines.append(line)

        if len(tb_ret_open_ingress.lines) > 0:
            tb_ret.blocks.append(tb_ret_open_ingress)
        if len(tb_ret_nonexistent_security_groups.lines) > 0:
            tb_ret.blocks.append(tb_ret_nonexistent_security_groups)
        return tb_ret

    def sub_cleanup_report_lambdas_large_size(self, permissions_only=False):
        """
        Large lambdas - over 100MiB size code.
        :return:
        """

        permissions = self.init_lambdas(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("Large lambdas: Maximum size is 250 MiB")
        limit = 100 * 1024 * 1024
        lst_names_sizes = []
        for aws_lambda in self.aws_api.lambdas:
            if aws_lambda.code_size >= limit:
                lst_names_sizes.append([aws_lambda.name, aws_lambda.code_size])

        if len(lst_names_sizes) > 0:
            lst_names_sizes = sorted(lst_names_sizes, key=lambda x: x[1], reverse=True)
            tb_ret.lines = [
                f"Lambda '{name}' size:{CommonUtils.bytes_to_str(code_size)}"
                for name, code_size in lst_names_sizes
            ]
        else:
            tb_ret.lines = [
                f"No lambdas found with size over {CommonUtils.bytes_to_str(limit)}"
            ]
        return tb_ret

    def sub_cleanup_report_lambdas_deprecate(self, permissions_only=False):
        """
        Lambdas with deprecating runtimes.

        :return:
        """

        permissions = self.init_lambdas(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        try:
            response = requests.get("https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html", timeout=32)
            response_text = response.text
            runtime_to_deprecation_date = self.get_supported_runtimes(response_text)
        except Exception as error_instance:
            logger.exception(repr(error_instance))
            runtime_to_deprecation_date = {"nodejs18.x": None,
                                           "nodejs16.x": datetime.datetime(2024, 3, 11, 0, 0),
                                           "nodejs14.x": datetime.datetime(2023, 11, 27, 0, 0),
                                           "python3.11": None,
                                           "python3.10": None,
                                           "python3.9": None,
                                           "python3.8": None,
                                           "python3.7": datetime.datetime(2023, 11, 27, 0, 0),
                                           "java17": None,
                                           "java11": None,
                                           "java8.al2": None,
                                           "java8": datetime.datetime(2023, 12, 31, 0, 0),
                                           "dotnet7": datetime.datetime(2024, 5, 14, 0, 0),
                                           "dotnet6": None,
                                           "go1.x": datetime.datetime(2023, 12, 31, 0, 0),
                                           "ruby3.2": None,
                                           "ruby2.7": datetime.datetime(2023, 12, 7, 0, 0),
                                           "provided.al2": None,
                                           "provided": datetime.datetime(2023, 12, 31, 0, 0)}

        tb_ret = TextBlock("Lambda runtime versions report")
        python_versions = sorted([int(runtime.replace("python3.", "")) for runtime in runtime_to_deprecation_date if runtime.startswith("python3.")])
        python_last_version = f"python3.{max(python_versions)}"
        provided_last_version = max(runtime for runtime in runtime_to_deprecation_date if runtime.startswith("provided"))
        nodejs_last_version = max(int(runtime.replace("nodejs","").replace(".x", "")) for runtime in runtime_to_deprecation_date if runtime.startswith("nodejs"))
        nodejs_last_version = f"nodejs{nodejs_last_version}.x"
        for function in self.aws_api.lambdas:
            if not function.runtime:
                continue
            if "python" in function.runtime:
                if function.runtime != python_last_version:
                    tb_ret.lines.append(f"Upgradable '{function.name}' [{function.runtime} -> {python_last_version}]")
            elif "provided" in function.runtime:
                if function.runtime != provided_last_version:
                    tb_ret.lines.append(f"Upgradable '{function.name}' [{function.runtime} -> {provided_last_version}]")
            elif "nodejs" in function.runtime:
                if function.runtime != nodejs_last_version:
                    tb_ret.lines.append(f"Upgradable '{function.name}' [{function.runtime} -> {nodejs_last_version}]")
            else:
                logger.error(f"Not implemented: Lambda runtime last version calculation: {function.runtime}")

        return tb_ret

    def get_supported_runtimes(self, response_text):
        """
        Supported runtimes with their deprecation date

        :param response_text:
        :return:
        """

        dict_ret = {}
        tables = self.extract_text_chunks(response_text, "<table", "</table")
        for table in tables:
            if "Supported Runtimes" in table:
                break
        else:
            raise RuntimeError("Can not find Supported Runtimes table")
        rows = self.extract_text_chunks(table, "<tr", "</tr")
        for row in rows[2:]:
            colls = self.extract_text_chunks(row, "<td", "</td")
            runtime_id_coll = \
                self.extract_text_chunks(self.extract_text_chunks(colls[1], "<p", "</p")[0], "<code", "</code")[
                    0].replace(
                    '<code class="code">', "")
            runtime_eol_coll = self.extract_text_chunks(colls[5], "<p", "</p")[0].replace("<p>", "")
            runtime_eol_coll = datetime.datetime.strptime(runtime_eol_coll, "%b %d, %Y") if runtime_eol_coll else None
            dict_ret[runtime_id_coll] = runtime_eol_coll
        return dict_ret

    @staticmethod
    def extract_text_chunks(src_text, start_string, end_string):
        """
        Text chunk by start/end string.

        :param src_text:
        :param start_string:
        :param end_string:
        :return:
        """

        lst_ret = []
        search_start_index = 0
        search_end_index = len(src_text)
        while True:
            chunk_start_index = src_text.find(start_string, search_start_index, search_end_index)
            if chunk_start_index == -1:
                break

            chunk_end_index = src_text.find(end_string, chunk_start_index, search_end_index)
            lst_ret.append(src_text[chunk_start_index:chunk_end_index])
            search_start_index = chunk_end_index
        return lst_ret

    def sub_cleanup_report_lambdas_not_running(self, permissions_only=False):
        """
        Lambda report checking if lambdas write logs:
        * No log group
        * Log group is empty
        * To old streams

        @return:
        """
        permissions = self.init_lambdas(permissions_only=permissions_only)
        permissions += self.init_cloud_watch_log_groups(permissions_only=permissions_only)

        if permissions_only:
            return permissions

        if not os.path.exists(self.configuration.cloudwatch_log_groups_streams_cache_dir):
            return None

        tb_ret = TextBlock(
            "Not functioning lambdas- either the last run was to much time ago or it never run"
        )
        for aws_lambda in self.aws_api.lambdas:
            log_groups = CommonUtils.find_objects_by_values(
                self.aws_api.cloud_watch_log_groups,
                {"name": f"/aws/lambda/{aws_lambda.name}"},
                max_count=1,
            )
            if len(log_groups) == 0:
                tb_ret.lines.append(
                    f"{aws_lambda.name}- never run [Log group does not exist]"
                )
                continue

            log_group = log_groups[0]
            if log_group.stored_bytes == 0:
                tb_ret.lines.append(
                    f"{aws_lambda.name}- never run [No logs in log group]"
                )
                continue

            if CommonUtils.timestamp_to_datetime(
                    log_group.creation_time / 1000
            ) > datetime.datetime.now() - datetime.timedelta(days=31):
                continue

            lines = self.sub_cleanup_report_lambdas_not_running_stream_analysis(
                log_group
            )
            tb_ret.lines += lines

        return tb_ret

    def sub_cleanup_report_lambdas_not_running_stream_analysis(self,
            log_group
    ):
        """
        Lambda report checking if the last log stream is to old

        @param log_group:
        @return:
        """

        lines = []
        file_names = os.listdir(
            os.path.join(
                self.configuration.cache_dir,
                log_group.generate_dir_name(),
            )
        )

        last_file = str(max(int(file_name) for file_name in file_names))
        with open(
                os.path.join(
                    self.configuration.cache_dir,
                    log_group.generate_dir_name(),
                    last_file,
                ),
                encoding="utf-8",
        ) as file_handler:
            last_stream = json.load(file_handler)[-1]
        if CommonUtils.timestamp_to_datetime(
                last_stream["lastIngestionTime"] / 1000
        ) < datetime.datetime.now() - datetime.timedelta(days=365):
            lines.append(
                f"Cloudwatch log group '{log_group.name}' last event was more then year ago: {CommonUtils.timestamp_to_datetime(last_stream['lastIngestionTime'] / 1000)}"
            )
        elif CommonUtils.timestamp_to_datetime(
                last_stream["lastIngestionTime"] / 1000
        ) < datetime.datetime.now() - datetime.timedelta(days=62):
            lines.append(
                f"Cloudwatch log group '{log_group.name}' last event was more then 2 months ago: {CommonUtils.timestamp_to_datetime(last_stream['lastIngestionTime'] / 1000)}"
            )
        return lines

    def sub_cleanup_report_lambdas_old_code(self, permissions_only=False):
        """
        Find all lambdas, which code wasn't updated for a year or more.
        :return:
        """

        permissions = self.init_lambdas(permissions_only=permissions_only)

        if permissions_only:
            return permissions

        days_limit = 365
        tb_ret = TextBlock(f"Lambdas with code older than {days_limit} days")
        time_limit = datetime.datetime.now(
            tz=datetime.timezone.utc
        ) - datetime.timedelta(days=days_limit)
        lst_names_dates = []
        for aws_lambda in self.aws_api.lambdas:
            if aws_lambda.last_modified < time_limit:
                lst_names_dates.append([aws_lambda.name, aws_lambda.last_modified])

        lst_names_dates = sorted(lst_names_dates, key=lambda x: x[1])
        tb_ret.lines = [
            f"Lambda {name} was last update: {update_date.strftime('%Y-%m-%d %H:%M')}"
            for name, update_date in lst_names_dates
        ]

        return tb_ret

    def cleanup_report_old_ecr_images(self, permissions_only=False):
        """
        # todo: images compiled 6 months ago
        :return:
        """

        if permissions_only:
            return []
        return None

    def cleanup_report_ec2_instances(self, permissions_only=False):
        """
        Old AMI. It's important to renew AMIs on a regular basics.

        :return:
        """

        permissions = self.init_ec2_amis(permissions_only=permissions_only)
        permissions += self.init_ec2_instances(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("EC2 half a year and older AMIs.")
        half_year_date = datetime.datetime.now() - datetime.timedelta(days=6*30)
        for inst in self.aws_api.ec2_instances:
            amis = CommonUtils.find_objects_by_values(self.aws_api.amis, {"id": inst.image_id}, max_count=1)
            if not amis:
                tb_ret.lines.append(f"{inst.name} Can not find AMI, looks like it was either deleted or made private.")
                continue
            ami = amis[0]
            if ami.creation_date < half_year_date:
                tb_ret.lines.append(f"{inst.name} AMI created at: {ami.creation_date}")
        with open(self.configuration.ec2_instances_report_file_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        logger.info(f"Output in: {self.configuration.ec2_instances_report_file_path}")
        return tb_ret

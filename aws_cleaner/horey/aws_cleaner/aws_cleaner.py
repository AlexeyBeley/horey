"""
AWS Cleaner. Money, money, money...

"""
import os
import json
import datetime
# pylint: disable=no-name-in-module, too-many-lines
from collections import defaultdict
import requests

from horey.h_logger import get_logger
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.aws_cleaner.aws_cleaner_configuration_policy import AWSCleanerConfigurationPolicy
from horey.common_utils.text_block import TextBlock
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.common_utils.common_utils import CommonUtils
from horey.network.service import ServiceTCP, Service
from horey.network.ip import IP

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
        aws_api_configuration.aws_api_cache_dir = configuration.cache_dir
        self.aws_api = AWSAPI(aws_api_configuration)

    def init_cloudwatch_metrics(self, permissions_only=False):
        """
        Init cloudwatch metrics and alarms

        :return:
        """

        if not permissions_only and not self.aws_api.cloud_watch_metrics:
            self.aws_api.init_cloud_watch_metrics()

        return [{
                "Sid": "cloudwatchMetrics",
                "Effect": "Allow",
                "Action": "cloudwatch:ListMetrics",
                "Resource": "*"
            }
            ]

    def init_cloudwatch_alarms(self, permissions_only=False):
        """
        Init cloudwatch alarms

        :param permissions_only:
        :return:
        """

        if not permissions_only and not self.aws_api.cloud_watch_alarms:
            self.aws_api.init_cloud_watch_alarms()


        return [{
            "Sid": "CloudwatchAlarms",
            "Effect": "Allow",
            "Action": "cloudwatch:DescribeAlarms",
            "Resource": [f"arn:aws:cloudwatch:{region.region_mark}:{self.aws_api.acm_client.account_id}:alarm:*"
                         for region in AWSAccount.get_aws_account().regions.values()]
        }]

    def init_ecr_images(self, permissions_only=False):
        """
        Init ECR images

        :return:
        """
        if not permissions_only and not self.aws_api.ecr_images:
            self.aws_api.init_ecr_images()
        return [
            {
                "Sid": "ECRTags",
                "Effect": "Allow",
                "Action": "ecr:ListTagsForResource",
                "Resource": "*"
            },
            *[{
                "Sid": "GetECR",
                "Effect": "Allow",
                "Action": ["ecr:DescribeRepositories", "ecr:DescribeImages"],
                "Resource": f"arn:aws:ecr:{region.region_mark}:{self.aws_api.acm_client.account_id}:repository/*"
            } for region in AWSAccount.get_aws_account().regions.values()]]

    def init_cloud_watch_log_groups(self, permissions_only=False):
        """
        Init Cloudwatch logs groups

        :return:
        """

        if not permissions_only and \
                (not self.aws_api.cloud_watch_log_groups or not
                self.aws_api.cloud_watch_log_groups_metric_filters or not
                 self.aws_api.cloud_watch_alarms):
            self.aws_api.init_cloud_watch_log_groups()
            self.aws_api.init_cloud_watch_log_groups_metric_filters()

        return [{
            "Sid": "CloudwatchLogs",
            "Effect": "Allow",
            "Action": ["logs:DescribeLogGroups", "logs:ListTagsForResource"],
            "Resource": "*"
        },
            {
                "Sid": "DescribeMetricFilters",
                "Effect": "Allow",
                "Action": "logs:DescribeMetricFilters",
                "Resource": [f"arn:aws:logs:{region.region_mark}:{self.aws_api.acm_client.account_id}:log-group:*"
                             for region in AWSAccount.get_aws_account().regions.values()]
            }
        ]

    def init_lambdas(self, permissions_only=False):
        """
        Init AWS Lambdas

        :return:
        """

        if not permissions_only and not self.aws_api.lambdas:
            # cache_file = os.path.join(self.configuration.cache_dir, "lambdas.json")
            # self.aws_api.cache_objects(self.aws_api.lambdas, cache_file, indent=4)
            # self.aws_api.init_lambdas(from_cache=True, cache_file=cache_file)
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
            "Action": "ec2:DescribeSecurityGroups",
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
        Init ELB/ALB Load balancers

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

    def init_target_groups(self, permissions_only=False):
        """
        Init ELB/ALB target groups

        :return:
        """

        if not permissions_only and not self.aws_api.target_groups:
            self.aws_api.init_target_groups()

        return [{
            "Sid": "GetTargetGroups",
            "Effect": "Allow",
            "Action": [
                "elasticloadbalancing:DescribeTargetGroups",
                "elasticloadbalancing:DescribeTargetHealth"
            ],
            "Resource": "*"
        }]

    def init_dynamodb_tables(self, permissions_only=False):
        """
        Init dynamodb_tables

        :return:
        """

        if not permissions_only and not self.aws_api.dynamodb_tables:
            self.aws_api.init_dynamodb_tables(full_information=True)

        return [{
            "Sid": "getDynamodb",
            "Effect": "Allow",
            "Action": [
                "dynamodb:ListTables",
            ],
            "Resource": "*"
        },
            *[{
                "Sid": "getDynamodbTable",
                "Effect": "Allow",
                "Action": ["dynamodb:DescribeTable",
                           "dynamodb:ListTagsOfResource",
                           "dynamodb:DescribeContinuousBackups"],
                "Resource": f"arn:aws:dynamodb:{region.region_mark}:{self.aws_api.acm_client.account_id}:table/*"
            } for region in AWSAccount.get_aws_account().regions.values()]
        ]

    def init_route_tables(self, permissions_only=False):
        """
        Init route tables

        :return:
        """

        if not permissions_only and not self.aws_api.route_tables:
            self.aws_api.init_route_tables()

        return [{
            "Sid": "getRouteTables",
            "Effect": "Allow",
            "Action": ["ec2:DescribeRouteTables"],
            "Resource": "*"
        }]

    def init_subnets(self, permissions_only=False):
        """
        Init subnets

        :return:
        """

        if not permissions_only and not self.aws_api.subnets:
            self.aws_api.init_subnets()

        return [{
            "Sid": "DescribeSubnets",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeSubnets"
            ],
            "Resource": "*"
        }]

    def init_rds(self, permissions_only=False):
        """
        Init rds

        :return:
        """

        if not permissions_only and not self.aws_api.rds_db_clusters:
            self.aws_api.init_rds_db_clusters(full_information=True)
            self.aws_api.init_rds_db_subnet_groups()

        return [
            {
                "Sid": "getRDS",
                "Effect": "Allow",
                "Action": ["rds:DescribeDBClusters", "rds:ListTagsForResource"],
                "Resource": [f"arn:aws:rds:{region.region_mark}:{self.aws_api.acm_client.account_id}:cluster:*" for
                             region in AWSAccount.get_aws_account().regions.values()]
            },
            {
                "Sid": "DescribeDBSubnetGroups",
                "Effect": "Allow",
                "Action": ["rds:DescribeDBSubnetGroups"],
                "Resource": [f"arn:aws:rds:{region.region_mark}:{self.aws_api.acm_client.account_id}:subgrp:*" for
                             region in AWSAccount.get_aws_account().regions.values()]
            },
            {
                "Sid": "DescribeDBEngineVersions",
                "Effect": "Allow",
                "Action": [
                    "rds:DescribeDBEngineVersions"
                ],
                "Resource": "*"
            },
        ]

    def init_elasticsearch_domains(self, permissions_only=False):
        """
        Init elasticsearch_domains

        :return:
        """

        if not permissions_only and not self.aws_api.elasticsearch_domains:
            self.aws_api.init_elasticsearch_domains()

        return [{
            "Sid": "getElasticsearch",
            "Effect": "Allow",
            "Action": [
                "es:ListDomainNames",
            ],
            "Resource": "*"
        }]

    def init_elasticache_clusters(self, permissions_only=False):
        """
        Init elasticache_clusters

        :return:
        """

        if not permissions_only and not self.aws_api.elasticache_clusters:
            self.aws_api.init_elasticache_clusters()

        return [{
            "Sid": "getElasticache",
            "Effect": "Allow",
            "Action": [
                "elasticache:DescribeCacheClusters",
            ],
            "Resource": "*"
        }]

    def init_sqs_queues(self, permissions_only=False):
        """
        Init sqs_queues

        :return:
        """

        if not permissions_only and not self.aws_api.sqs_queues:
            self.aws_api.init_sqs_queues()

        return [
            *[{
                "Sid": "getSQS",
                "Effect": "Allow",
                "Action": ["sqs:ListQueues", "sqs:GetQueueAttributes", "sqs:ListQueueTags"],
                "Resource": f"arn:aws:sqs:{region.region_mark}:{self.aws_api.acm_client.account_id}:*"
            } for region in AWSAccount.get_aws_account().regions.values()]]

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

        ret_policy = {"Version": "2012-10-17",
                      "Statement": unique_statements}

        with open(self.configuration.permissions_file_path, "w", encoding="utf-8") as file_handler:
            json.dump(ret_policy, file_handler, indent=4)

        return ret_policy

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

        permissions = self.init_ec2_network_interfaces(permissions_only=permissions_only)
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
        "namespace" : "AWS/Lambda"
        dimensions: [{'Name': 'FunctionName', 'Value': ''}]

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
        python_versions = sorted([int(runtime.replace("python3.", "")) for runtime in runtime_to_deprecation_date if
                                  runtime.startswith("python3.")])
        python_last_version = f"python3.{max(python_versions)}"
        provided_last_version = max(
            runtime for runtime in runtime_to_deprecation_date if runtime.startswith("provided"))
        nodejs_last_version = max(
            int(runtime.replace("nodejs", "").replace(".x", "")) for runtime in runtime_to_deprecation_date if
            runtime.startswith("nodejs"))
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

            if os.path.exists(self.configuration.cloudwatch_log_groups_streams_cache_dir):
                lines = self.sub_cleanup_report_lambdas_not_running_stream_analysis(
                    log_group
                )
                tb_ret.lines += lines
            else:
                logger.error(f"No log group streams {self.configuration.cloudwatch_log_groups_streams_cache_dir}")

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

    def cleanup_report_ecr_images(self, permissions_only=False):
        """
        Images compiled 6 months ago and later.

        :return:
        """

        permissions = self.init_ecr_images(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("ECR Images half year and older")
        images_by_ecr_repo = defaultdict(list)
        for image in self.aws_api.ecr_images:
            images_by_ecr_repo[image.repository_name].append(image)

        half_year_date = None
        for images in images_by_ecr_repo.values():
            half_year_date = datetime.datetime.now(tz=images[0].image_pushed_at.tzinfo) - datetime.timedelta(
                days=6 * 30)
            break

        for repo_name, images in images_by_ecr_repo.items():
            last_image = sorted(images, key=lambda _image: _image.image_pushed_at)[-1]
            if last_image.image_pushed_at < half_year_date:
                tb_ret.lines.append(
                    f"Repository '{repo_name}' last image pushed at: {last_image.image_pushed_at.strftime('%Y-%m-%d %H:%M')} ")

        with open(self.configuration.ecr_report_file_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        logger.info(f"Output in: {self.configuration.ecr_report_file_path}")
        return tb_ret

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
        half_year_date = datetime.datetime.now() - datetime.timedelta(days=6 * 30)
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

    def cleanup_report_dynamodb(self, permissions_only=False):
        """
        DynamoDB has no backup.
        todo: Used read/write much less than reservation.

        :param permissions_only:
        :return:
        """

        permissions = self.init_dynamodb_tables(permissions_only=permissions_only)

        if permissions_only:
            return permissions

        tb_ret = TextBlock("DynamoDB tables have no backup configured.")
        for table in self.aws_api.dynamodb_tables:
            if not table.deletion_protection_enabled:
                tb_ret.lines.append(f"Table '{table.name}' deletion_protection is disabled")

            if table.continuous_backups["ContinuousBackupsStatus"] != "ENABLED":
                tb_ret.lines.append(f"Table '{table.name}' has no continuous backup enabled")

        with open(self.configuration.dynamodb_report_file_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        logger.info(f"Output in: {self.configuration.dynamodb_report_file_path}")
        return tb_ret

    def cleanup_report_rds(self, permissions_only=False):
        """
        RDS has no metrics

        :param permissions_only:
        :return:
        """

        permissions = self.init_rds(permissions_only=permissions_only)
        permissions += self.init_route_tables(permissions_only=permissions_only)
        permissions += self.init_security_groups(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("RDS Cleanups")
        for cluster in self.aws_api.rds_db_clusters:
            tb_ret_tmp = self.sub_cleanup_report_rds_cluster(cluster)
            if tb_ret_tmp:
                tb_ret.blocks.append(tb_ret_tmp)

        with open(self.configuration.rds_report_file_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        logger.info(f"Output in: {self.configuration.rds_report_file_path}")
        return tb_ret

    def sub_cleanup_report_rds_cluster(self, cluster):
        """
        All sub routines to clean the RDS cluster.

        :param cluster:
        :return:
        """

        tb_ret = TextBlock(f"Cluster '{cluster.id}' [{cluster.region}]")
        tb_ret_tmp = self.sub_cleanup_rds_best_practices(cluster)
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)
        tb_ret_tmp = self.sub_cleanup_rds_security_groups(cluster)
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)
        return tb_ret if tb_ret.blocks else None

    def sub_cleanup_rds_best_practices(self, cluster):
        """
        Best practices for prod cluster.

        :param cluster:
        :return:
        """

        tb_ret = TextBlock("Production environment best practices")

        if not cluster.deletion_protection:
            tb_ret.lines.append("Disabled: Deletion protection")
        if not cluster.storage_encrypted:
            tb_ret.lines.append("Disabled: Storage is not encryption")
        if not cluster.enabled_cloudwatch_logs_exports:
            tb_ret.lines.append("Disabled: Log export to cloudwatch.")
        if not cluster.multi_az:
            tb_ret.lines.append("Disabled: multi-az.")
        if cluster.engine_version != cluster.default_engine_version["EngineVersion"]:
            tb_ret.lines.append(
                f"Engine version '{cluster.engine_version}' is not the default "
                f"'{cluster.default_engine_version['EngineVersion']}'")

        subnet_group = \
        CommonUtils.find_objects_by_values(self.aws_api.rds_db_subnet_groups, {"name": cluster.db_subnet_group},
                                           max_count=1)[0]
        for dict_subnet in subnet_group.subnets:
            subnet_id = dict_subnet['SubnetIdentifier']
            subnet = CommonUtils.find_objects_by_values(self.aws_api.subnets, {"id": subnet_id}, max_count=1)[0]
            route_table = self.aws_api.find_route_table_by_subnet(cluster.region, subnet)

            default_route = route_table.get_default_route()
            if not default_route:
                tb_ret.lines.append(f"Can not find default route for {subnet_id} route table {route_table.id}")
                continue
            if default_route.get("GatewayId"):
                tb_ret.lines.append(f"Subnet is public: {dict_subnet['SubnetIdentifier']}")

        return tb_ret if tb_ret.lines else None

    def sub_cleanup_rds_security_groups(self, cluster):
        """
        Check the DB port is the only one open in all security groups.

        :return:
        """

        tb_ret = TextBlock("Security groups analysis")
        for dict_security_group in cluster.vpc_security_groups:
            sg_id = dict_security_group["VpcSecurityGroupId"]
            security_group = \
            CommonUtils.find_objects_by_values(self.aws_api.security_groups, {"id": sg_id}, max_count=1)[0]
            for ip, service in security_group.get_ingress_pairs():
                if service is Service.any():
                    tb_ret.lines.append(f"SG '{security_group.name}' {ip}:{service}")
                    continue
                if service.start != service.end != cluster.port:
                    tb_ret.lines.append(f"SG '{security_group.name}' {ip}:{service}")
        return tb_ret if tb_ret.lines else None

    def cleanup_opensearch(self, permissions_only=False):
        """
        RDS engine version
        RDS has no retention.
        opensearch has no metrics
        deletion_protection is disabled

        :param permissions_only:
        :return:
        """

        permissions = self.init_elasticsearch_domains(permissions_only=permissions_only)

        if permissions_only:
            return permissions

        tb_ret = TextBlock("EC2 half a year and older AMIs.")
        for table in self.aws_api.elasticsearch_domains:
            tb_ret.lines.append(f"{table.name} ike it was either deleted or made private.")

        with open(self.configuration.elasticsearch_domains_report_file_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        logger.info(f"Output in: {self.configuration.elasticsearch_domains_report_file_path}")
        return tb_ret

    def cleanup_report_elasticache(self, permissions_only=False):
        """
        Elasticache have public subnets
        Elasticache version

        :param permissions_only:
        :return:
        """

        permissions = self.init_elasticache_clusters(permissions_only=permissions_only)

        if permissions_only:
            return permissions

        tb_ret = TextBlock("EC2 half a year and older AMIs.")
        for table in self.aws_api.elasticache_clusters:
            tb_ret.lines.append(f"{table.name} ike it was either deleted or made private.")

        with open(self.configuration.elasticache_report_file_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        logger.info(f"Output in: {self.configuration.elasticache_report_file_path}")
        return tb_ret

    def cleanup_report_cloudwatch(self, permissions_only=False):
        """
        No metric_filters on logs.
        no alarms on metric
        disabled alarms

        :param permissions_only:
        :return:
        """

        permissions = self.init_cloud_watch_log_groups(permissions_only=permissions_only)
        permissions += self.init_cloudwatch_alarms(permissions_only=permissions_only)

        if permissions_only:
            return permissions

        tb_ret = TextBlock("Cloudwatch cleanup.")
        no_retention = []
        no_metrics = []
        all_metric_filters = []
        for group in self.aws_api.cloud_watch_log_groups:
            if group.retention_in_days is None:
                no_retention.append(f"{group.name}: No retention")

            metric_filters = CommonUtils.find_objects_by_values(self.aws_api.cloud_watch_log_groups_metric_filters,
                                                         {"log_group_name": group.name})
            all_metric_filters += metric_filters
            if not metric_filters:
                no_metrics.append(f"{group.name}: No metric filters")

            tb_ret_tmp = self.sub_cleanup_report_cloudwatch_logs_metrics(metric_filters)
            tb_ret_tmp.header = f"Group: {group.name}. {tb_ret_tmp.header}"
            metric_filters_patterns = defaultdict(list)
            for metric_filter in metric_filters:
                if metric_filter.filter_pattern:
                    metric_filters_patterns[metric_filter.filter_pattern].append(metric_filter)
            tb_ret_tmp.lines = [
                                   f"Same filter pattern '{filter_pattern}' appears in  multiple metric filters: {[metric.name for metric in _metric_filters]}"
                                   for filter_pattern, _metric_filters in metric_filters_patterns.items() if
                                   len(_metric_filters)>1] + tb_ret_tmp.lines

            if tb_ret_tmp.lines or tb_ret_tmp.blocks:
                tb_ret.blocks.append(tb_ret_tmp)
        tb_ret.lines = no_retention + no_metrics

        if len(all_metric_filters) != len(self.aws_api.cloud_watch_log_groups_metric_filters):
            tb_ret.lines.append(f"Something went wrong Checked metric filters count {len(all_metric_filters)} != fetched via AWS API {len(self.aws_api.cloud_watch_log_groups_metric_filters)}")

        with open(self.configuration.cloud_watch_report_file_path, "w+",
                  encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        logger.info(f"Output in: {self.configuration.cloud_watch_report_file_path}")
        return tb_ret

    def sub_cleanup_report_cloudwatch_logs_metrics(self, metrics):
        """
        Generate report for cloudwatch_metrics

        :param metrics:
        :return:
        """

        tb_ret = TextBlock("Cloudwatch metrics report")
        for metric in metrics:
            lines = self.sub_cleanup_lines_cloudwatch_log_metric(metric)
            tb_ret.lines += lines
        return tb_ret

    def sub_cleanup_lines_cloudwatch_log_metric(self, metric):
        """
        Generate report for cloudwatch metric

        :param metric:
        :return:
        """

        lines = []
        if not metric.metric_transformations or len(metric.metric_transformations) > 1:
            raise NotImplementedError("Can not check the metric filter")

        alarms = CommonUtils.find_objects_by_values(self.aws_api.cloud_watch_alarms,
                                                    {"namespace": metric.metric_transformations[
                                                        0]["metricNamespace"],
                                                     "metric_name":
                                                         metric.metric_transformations[
                                                             0]["metricName"]})
        if not alarms:
            lines.append(f"Metric '{metric.name}' has no alarms")
        for alarm in alarms:
            if not alarm.actions_enabled:
                lines.append(f"Metric: '{metric.name}' Disabled Alarm")
        return lines

    def cleanup_report_sqs(self, permissions_only=False):
        """
        No metrics on SQS.
        "namespace" :
        dimensions: [{'Name': 'QueueName', 'Value': ''}]
        sqs_alarms = CommonUtils.find_objects_by_values(self.aws_api.cloud_watch_alarms, {"namespace": "AWS/SQS"})

        :param permissions_only:
        :return:
        """

        permissions = self.init_sqs_queues(permissions_only=permissions_only)
        permissions += self.init_cloudwatch_alarms(permissions_only=permissions_only)

        if permissions_only:
            return permissions

        tb_ret = TextBlock("EC2 half a year and older AMIs.")
        for table in self.aws_api.sqs_queues:
            tb_ret.lines.append(f"{table.name} ike it was either deleted or made private.")

        with open(self.configuration.sqs_report_file_path, "w+",
                  encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        logger.info(f"Output in: {self.configuration.sqs_report_file_path}")
        return tb_ret

    def cleanup_report_load_balancers(self, permissions_only=False):
        """
        Generate load balancers' cleanup report.

        @return:
        """
        if permissions_only:
            permissions = self.sub_cleanup_classic_load_balancers(permissions_only=permissions_only)
            permissions += self.sub_cleanup_alb_load_balancers(permissions_only=permissions_only)
            permissions += self.sub_cleanup_target_groups(permissions_only=permissions_only)
            permissions += self.sub_cleanup_loadbalancer_private_subnet(permissions_only=permissions_only)
            permissions += self.sub_cleanup_loadbalancer_has_no_metrics(permissions_only=permissions_only)
            return permissions

        tb_ret = TextBlock("Load Balancers Cleanup")
        tb_ret_tmp = self.sub_cleanup_classic_load_balancers()
        if tb_ret_tmp is not None:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_cleanup_alb_load_balancers()
        if tb_ret_tmp is not None:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_cleanup_target_groups()
        if tb_ret_tmp.lines or tb_ret_tmp.blocks:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_cleanup_loadbalancer_private_subnet()
        if tb_ret_tmp.lines or tb_ret_tmp.blocks:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_cleanup_loadbalancer_has_no_metrics()
        if tb_ret_tmp.lines or tb_ret_tmp.blocks:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret.write_to_file(self.configuration.load_balancer_report_file_path)

        logger.info(f"Output in: {self.configuration.load_balancer_report_file_path}")

        return tb_ret

    def sub_cleanup_classic_load_balancers(self, permissions_only=False):
        """
        Generate cleanup report for classic load balancers.

        @return:
        """

        permissions = self.init_load_balancers(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("Cleanup report classic load balancers")
        tb_ret_no_instances = TextBlock(
            "No instances associated with these load balancers"
        )
        tb_ret_no_listeners = TextBlock(
            "No listeners associated with these load balancers"
        )
        for load_balancer in self.aws_api.classic_load_balancers:
            if not load_balancer.listeners:
                tb_ret_no_listeners.lines.append(load_balancer.name)

            if not load_balancer.instances:
                tb_ret_no_instances.lines.append(load_balancer.name)

        if len(tb_ret_no_instances.lines) > 0:
            tb_ret.blocks.append(tb_ret_no_instances)

        if len(tb_ret_no_listeners.lines) > 0:
            tb_ret.blocks.append(tb_ret_no_listeners)

        return tb_ret if len(tb_ret.blocks) > 0 else None

    def sub_cleanup_alb_load_balancers(self, permissions_only=False):
        """
        Generate cleanup report for alb load balancers.

        @return:
        """

        permissions = self.init_load_balancers(permissions_only=permissions_only)
        permissions += self.init_target_groups(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("Cleanup report ALBs")
        tb_ret_no_tgs = TextBlock(
            "No target groups associated with these load balancers"
        )
        tb_ret_no_listeners = TextBlock(
            "No listeners associated with these load balancers"
        )

        lbs_using_tg = set()
        for target_group in self.aws_api.target_groups:
            lbs_using_tg.update(target_group.load_balancer_arns)

        for load_balancer in self.aws_api.load_balancers:
            if not load_balancer.listeners:
                tb_ret_no_listeners.lines.append(load_balancer.name)

            if load_balancer.arn not in lbs_using_tg:
                tb_ret_no_tgs.lines.append(load_balancer.name)

        if len(tb_ret_no_tgs.lines) > 0:
            tb_ret.blocks.append(tb_ret_no_tgs)

        if len(tb_ret_no_listeners.lines) > 0:
            tb_ret.blocks.append(tb_ret_no_listeners)

        return tb_ret if len(tb_ret.blocks) > 0 else None

    def sub_cleanup_loadbalancer_private_subnet(self, permissions_only=False):
        """
        Check public load balancers have public subnet.
        Check private load balancers have private subnets.

        @return:
        """

        permissions = self.init_load_balancers(permissions_only=permissions_only)
        permissions += self.init_route_tables(permissions_only=permissions_only)
        permissions += self.init_subnets(permissions_only=permissions_only)

        if permissions_only:
            return permissions

        tb_ret = TextBlock("Load balancers with wrong subnet type association (public/private)")
        for load_balancer in self.aws_api.load_balancers:
            for availability_zone in load_balancer.availability_zones:
                subnet_id = availability_zone["SubnetId"]
                subnet = CommonUtils.find_objects_by_values(self.aws_api.subnets, {"id": subnet_id}, max_count=1)[0]
                route_table = self.aws_api.find_route_table_by_subnet(load_balancer.region, subnet)

                default_route = route_table.get_default_route()
                if not default_route:
                    tb_ret.lines.append(
                        f"Can not find default route for {availability_zone['SubnetId']} route table {route_table.id}")
                    continue
                if default_route.get("GatewayId") and load_balancer.scheme != "internet-facing":
                    tb_ret.lines.append(f"Internal LB {load_balancer.name} has public {availability_zone['SubnetId']}")
                elif not default_route.get("GatewayId") and load_balancer.scheme == "internet-facing":
                    tb_ret.lines.append(
                        f"Internet facing LB {load_balancer.name} has private {availability_zone['SubnetId']}")
        return tb_ret

    def sub_cleanup_loadbalancer_has_no_metrics(self, permissions_only=False):
        """
        No metrics configured to monitor Load Balancer.

        @return:
        """

        permissions = self.init_load_balancers(permissions_only=permissions_only)
        if permissions_only:
            return permissions
        tb_ret = TextBlock("todo: Load balancer with no metrics in cloudwatch")
        return tb_ret

    def sub_cleanup_target_groups(self, permissions_only=False):
        """
        Cleanup report find unhealthy target groups

        @return:
        """

        permissions = self.init_target_groups(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("Following target groups have health problems")
        for target_group in self.aws_api.target_groups:
            if not target_group.target_health:
                tb_ret.lines.append(target_group.name)
        return tb_ret if len(tb_ret.lines) > 0 else None

    def cleanup_report_security_groups(self, permissions_only=False):
        """
        Generating security group cleanup reports.

        @param permissions_only:
        @return:
        """

        if permissions_only:
            permissions = self.sub_cleanup_report_wrong_port_lbs_security_groups(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_unused_security_groups(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_dangerous_security_groups(permissions_only=permissions_only)
            return permissions

        tb_ret = TextBlock("EC2 security groups cleanup")
        tb_ret.blocks.append(self.sub_cleanup_report_wrong_port_lbs_security_groups())
        tb_ret.blocks.append(self.sub_cleanup_report_unused_security_groups())
        tb_ret.blocks.append(self.sub_cleanup_report_dangerous_security_groups())

        tb_ret.write_to_file(self.configuration.ec2_security_groups_report_file_path)
        return tb_ret

    def sub_cleanup_report_wrong_port_lbs_security_groups(self, permissions_only=False):
        """
        Checks load balancers' ports to security groups' internal ports.

        @return:
        """

        permissions = self.init_load_balancers(permissions_only=permissions_only)
        if permissions_only:
            permissions += self.sub_cleanup_report_wrong_port_lb_security_groups(None,
                                                                                 permissions_only=permissions_only)
            return permissions

        tb_ret = TextBlock("Wrong load balancer listeners ports")
        for load_balancer in self.aws_api.load_balancers + self.aws_api.classic_load_balancers:
            lines = self.sub_cleanup_report_wrong_port_lb_security_groups(load_balancer)
            tb_ret.lines += lines

        return tb_ret

    def sub_cleanup_report_unused_security_groups(self, permissions_only=False):
        """
        Unassigned security groups.

        @return:
        """

        permissions = self.init_security_groups(permissions_only=permissions_only)
        permissions += self.init_ec2_network_interfaces(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("Unused security groups")
        used_security_group_ids = []
        for interface in self.aws_api.network_interfaces:
            sg_ids = interface.get_used_security_group_ids()
            used_security_group_ids += sg_ids
        used_security_group_ids = list(set(used_security_group_ids))
        all_security_groups_dict = {sg.id: sg.name for sg in self.aws_api.security_groups}
        tb_ret.lines = [
            f"{sg_id} [{all_security_groups_dict[sg_id]}]"
            for sg_id in all_security_groups_dict
            if sg_id not in used_security_group_ids
        ]
        return tb_ret

    def sub_cleanup_report_dangerous_security_groups(self, permissions_only=False):
        """
        Security groups with to wide permissions.

        @return:
        """

        permissions = self.init_security_groups(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("Dangerously open security groups")
        for security_group in self.aws_api.security_groups:
            pairs = security_group.get_ingress_pairs()
            if len(pairs) == 0:
                tb_ret.lines.append(
                    f"No ingress rules in group {security_group.id} [{security_group.name}]"
                )
                continue
            for ip, service in pairs:
                if ip is IP.any():
                    tb_ret.lines.append(
                        f"Dangerously wide range of addresses {security_group.id} [{security_group.name}] - {ip}"
                    )

                if service is Service.any():
                    tb_ret.lines.append(
                        f"Dangerously wide range of services {security_group.id} [{security_group.name}] - {service}"
                    )

        return tb_ret

    def sub_cleanup_report_wrong_port_lb_security_groups(self, load_balancer, permissions_only=False):
        """
        Checks single load balancer's ports to security groups' internal ports.

        @param load_balancer:
        @return:
        """

        permissions = self.init_security_groups(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        lines = []
        if load_balancer.security_groups is None:
            lines.append(f"Load balancer '{load_balancer.name}' has no security groups assigned")
            return lines

        listeners_ports = [listener.port for listener in load_balancer.listeners]
        listeners_ports = set(listeners_ports)

        listeners_services = []
        for port in listeners_ports:
            service = ServiceTCP()
            service.start = port
            service.end = port
            listeners_services.append(service)

        for security_group_id in load_balancer.security_groups:
            security_group = CommonUtils.find_objects_by_values(
                self.aws_api.security_groups, {"id": security_group_id}, max_count=1
            )[0]
            security_group_dst_pairs = security_group.get_ingress_pairs()

            for _, sg_service in security_group_dst_pairs:
                for listener_service in listeners_services:
                    if listener_service.intersect(sg_service) is not None:
                        break
                else:
                    lines.append(
                        f"Security group '{security_group.name}' has and open service '{str(sg_service)}' but no LB '{load_balancer.name}' listener on this port"
                    )

            for listener_service in listeners_services:
                for _, sg_service in security_group_dst_pairs:
                    if listener_service.intersect(sg_service) is not None:
                        break
                else:
                    lines.append(
                        f"There is LB '{load_balancer.name}' listener service '{listener_service}' but no security group permits a traffic to it"
                    )
        return lines

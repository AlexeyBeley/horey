"""
AWS Cleaner. Money, money, money...

"""
import os
import json
import datetime
# pylint: disable=no-name-in-module, too-many-lines
from collections import defaultdict
from enum import Enum

import requests
from time import perf_counter

from horey.h_logger import get_logger
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.aws_cleaner.aws_cleaner_configuration_policy import AWSCleanerConfigurationPolicy
from horey.aws_cleaner.price_list_product import PriceListProduct
from horey.common_utils.text_block import TextBlock
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.common_utils.common_utils import CommonUtils
from horey.network.service import ServiceTCP, Service
from horey.network.ip import IP

logger = get_logger()


class Report:
    def __init__(self, aws_service):
        self.service = aws_service
        self.actions = []
        self.sub_reports = []

    def __add__(self, action_or_subreport):
        if isinstance(action_or_subreport, ReportAction):
            new_item = action_or_subreport.__class__(action_or_subreport.path)
            if new_item != action_or_subreport:
                self.actions.append(action_or_subreport)
        elif isinstance(action_or_subreport, Report):
            self.sub_reports.append(action_or_subreport)
        elif isinstance(action_or_subreport, list):
            for _action_or_subreport in action_or_subreport:
                self.__add__(_action_or_subreport)
        elif action_or_subreport is None:
            pass
        else:
            raise ValueError(f"Unsupported type: {type(action_or_subreport)}")
        return self

    def generate_text_block(self):
        """
        Generate readable format
        :return:
        """

        h_tb_ret = TextBlock(f"Report for service: {self.service}")
        h_tb_ret.lines = [line for action in self.actions for line in action.generate_lines()]
        h_tb_ret.blocks = [sub_report.generate_text_block() for sub_report in self.sub_reports]
        return h_tb_ret

    def write_to_file(self, file_path):
        """
        Write output in a readable format

        :return:
        """

        text_block = self.generate_text_block()
        text_block.write_to_file(file_path)
        logger.info(f"Output in: {file_path}")


class ReportAction:
    def __init__(self, path, reason=None):
        self.path = path
        self.reason = reason

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def generate_lines(self):
        """
        Standard.

        :return:
        """
        raise NotImplementedError()


class ReportActionCloudwatchAlarm(ReportAction):
    def __init__(self, path, reason=None):
        super().__init__(path, reason=reason)
        self.dimension_balckholes = []
        self.action_blackholes = []
        self.no_active_actions = False

    def generate_lines(self):
        """
        Standard.

        :return:
        """
        lst_ret = []
        base_str_ret = f"Alarm: '{self.path['arn']}'."

        if self.dimension_balckholes:
            lst_ret.append("Important: " + base_str_ret + "Metric with these dimensions does not exist")

        for action_arn in self.action_blackholes:
            lst_ret.append("Important: " + base_str_ret + f"Action destination does not exist: {action_arn}.")

        return lst_ret


class ReportActionCloudwatchLogGroupMetric(ReportAction):
    def __init__(self, path, reason=None):
        super().__init__(path, reason=reason)
        self.disabled_actions_alarms = []
        self.no_alarms = False
        self.no_log_group = False

    def generate_lines(self):
        """
        Standard.

        :return:
        """

        base_str_ret = f"Region: {self.path['region']}. LogGroup Filter Metric: '{self.path['name']}.'"

        if self.disabled_actions_alarms:
            if self.no_alarms:
                return ["Important: " + base_str_ret + "All Alarms are disabled!"]

            return ["Important: " + base_str_ret + f"Disabled Alarms: {self.disabled_actions_alarms}"]

        if self.no_alarms:
            return["Important: " + base_str_ret + " No alarms set"]
        
        if self.no_log_group:
            return ["Important: " + base_str_ret + " No such log group"]
        return []


class ReportActionCloudwatchLogGroup(ReportAction):
    def __init__(self, path, reason=None):
        super().__init__(path, reason=reason)
        self.no_retention = False
        self.no_metric_filter = False
        self._redundant_metric_filters = None
        self.size = None
        self.idle = False

    @property
    def redundant_metric_filters(self):
        """
        Standard.

        :return:
        """
        return self._redundant_metric_filters

    @redundant_metric_filters.setter
    def redundant_metric_filters(self, value):
        """
        Standard.

        :return:
        """
        if not value:
            return
        self._redundant_metric_filters = value

    def generate_lines(self):
        """
        Standard.

        :return:
        """

        lst_ret = []
        base_str_ret = f"Region: {self.path['region']}. LogGroup: '{self.path['name']}.'"

        if self.no_retention:
            lst_ret.append("Important: " + base_str_ret + " No retention")

        if self.no_metric_filter:
            lst_ret.append("Suggestion: " + base_str_ret + " No metric filter configured.")

        if self.redundant_metric_filters:
            for key, value in self.redundant_metric_filters.items():
                lst_ret.append("Important: " + base_str_ret + f" Filter by: {key}. Delete one of {value}")

        if self.size:
            lst_ret.append("Suggestion: " + base_str_ret + f" {self.size['order']}-th largest in size: {CommonUtils.bytes_to_str(self.size['stored_bytes'])}")

        if self.idle:
            lst_ret.append(
                "Important: " + base_str_ret + f" Is idle > month.")

        return lst_ret


class ReportActionECSCapacityProvider(ReportAction):
    def __init__(self, path, reason=None):
        super().__init__(path, reason=reason)
        self.unused_capacity_provider = False
        self.unused_container_instances = None

    def generate_lines(self):
        """
        Standard.

        :return:
        """
        lst_ret = []
        base_str_ret = f"ECS Capacity Provider: '{self.path['region']}' '{self.path['name']}'."

        if self.unused_capacity_provider:
            reason = self.reason or " Unused Capacity Provider"
            lst_ret.append(f"Important: {base_str_ret} {reason}")

        if self.unused_container_instances:
            reason = self.reason or f" Unused Container instances : {self.unused_container_instances}."
            lst_ret.append(f"Important: {base_str_ret} {reason}")

        return lst_ret


class AWSCleaner:
    """
    Main logic class.

    """

    def __init__(self, configuration: AWSCleanerConfigurationPolicy, aws_api=None):
        self.configuration = configuration

        if aws_api is None:
            aws_api_configuration = AWSAPIConfigurationPolicy()
            aws_api_configuration.accounts_file = self.configuration.managed_accounts_file_path
            aws_api_configuration.aws_api_account = self.configuration.aws_api_account_name
            aws_api_configuration.aws_api_cache_dir = configuration.cache_dir
            aws_api = AWSAPI(aws_api_configuration)
        self.aws_api = aws_api

    # pylint: disable= too-many-statements
    def cleanup_report_todo(self):
        """
        Adding tags for cost calculations:
        https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html
        And S3 tagging for cost calculations
        put_bucket_tagging

        :return:
        """

        tb_ret = TextBlock("In the plans")

        tb_ret_tmp = TextBlock("Lamda versions delete")
        tb_ret_tmp.lines.append("Delete old versions")
        tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = TextBlock("ECR TD and Images")
        tb_ret_tmp.lines.append("Delete old Task definitions")
        tb_ret_tmp.lines.append("Delete ECR repos that are not used in Lambda and Task definition / last pulled.")
        tb_ret.blocks.append(tb_ret_tmp)


        tb_ret_tmp = TextBlock("Event Bridge - event rules")
        tb_ret_tmp.lines.append("Check event bridge rule has valid destination")
        tb_ret_tmp.lines.append("Check the destination has resource policy permitting event bridge to trigger it")
        tb_ret.blocks.append(tb_ret_tmp)


        tb_ret_tmp = TextBlock("Cloudwatch")
        tb_ret_tmp.lines.append("Cloudwatch alarms can have issues. They can fault to be triggered.")
        tb_ret_tmp.lines.append("One reason - sns topic policy does not grant permissions to the alarm to publish.")
        tb_ret_tmp.lines.append(
            "Use client.describe_alarm_history functionality to fetch history about failed to trigger actios.")
        tb_ret_tmp.lines.append("Check if there are cloudwatch metrics to see failing alarm actions.")
        tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = TextBlock("VPC")
        tb_ret_tmp.lines.append("There are sometimes routing black holes towards erases VPC peering connection.")
        tb_ret_tmp.lines.append("Subnet naming - the name can contain public/private word but be the opposite.")
        tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = TextBlock("Opensearch")
        tb_ret_tmp.lines.append("Opensearch has no active cloudwatch alarms")
        tb_ret_tmp.lines.append("Opensearch engine version")
        tb_ret_tmp.lines.append("Opensearch has no retention.")
        tb_ret_tmp.lines.append("deletion_protection is disabled")
        tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = TextBlock("Elasticache")
        tb_ret_tmp.lines.append("Has public subnets configures")
        tb_ret_tmp.lines.append("Engine version is old")
        tb_ret_tmp.lines.append("Security group to wide")
        tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = TextBlock("SQS")
        tb_ret_tmp.lines.append("No cloudwatch alarms were configured for SQS queues")
        tb_ret_tmp.lines.append("No dead latter queue was configured for the queue")
        tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = TextBlock("Route 53")
        tb_ret_tmp.lines.append(" cleanup_report_route53_certificates")
        tb_ret_tmp.lines.append("ACM Certificates need to be validated using Route 53 records. "
                                "Expired/missing certificates information has to be cleaned from Route 53.")
        tb_ret_tmp.lines.append("Load balancers dns addresses: Missing Load Balancer.")
        tb_ret_tmp.lines.append(
            "Load balancers dns addresses: Missing DNS record pointing to the load balancer DNS address.")
        tb_ret_tmp.lines.append("AssociateVPCWithHostedZone: erased VPCs ids associated with hosted zone.")
        tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = TextBlock("ACM")
        tb_ret_tmp.lines.append("ACM Certificates Validation failed")
        tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = TextBlock("Lambda")
        tb_ret_tmp.lines.append("Lambda policy has no permissions to write logs")
        tb_ret_tmp.lines.append('"No log group streams" logic to implement')

        tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = TextBlock("SNS")
        tb_ret_tmp.lines.append(
            "find sns topics set to handle cloudwatch alarms but have no policy permitting cloudwatch sending sns.")
        tb_ret_tmp.lines.append("Too permissive default policy- policy permitting Topic deletion to *")
        tb_ret_tmp.lines.append("Delivery status logging disabled")
        tb_ret_tmp.lines.append("Delivery status logging is not permitting logging for subscription protocol")
        tb_ret_tmp.lines.append("Delivery status logging is permitting logging for protocol without subscription")
        tb_ret_tmp.lines.append("Resource ARN in the policy is not covering owning topic's ARN.")
        tb_ret.blocks.append(tb_ret_tmp)
        tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = TextBlock("IAM")
        tb_ret_tmp.lines.append(
            "Mention of deleted user/role in policies ARNs- for example explicit mention of a specific user.")
        tb_ret_tmp.lines.append(
            "Action per service: for example * action on  ECR:* and S3:* - bad idea, you must manage at least per service")
        tb_ret_tmp.lines.append(
            "Single role should permit deletion on *, all others must be restricted either by region or by resource arn")

        tb_ret_tmp.lines.append(
            "To check an option to do report per resource: for example who can delete RDS/ECS/Lambda - which roles/policies and who can use them - user/ec2-instance/lambda")
        tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = TextBlock("EC2")
        tb_ret_tmp.lines.append("cleanup_report_ec2_instances add deletion protection check")
        tb_ret_tmp.lines.append("cleanup_report_ec2_instances add iam instance profile role too permissive check")
        tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = TextBlock("DynamoDB")
        tb_ret_tmp.lines.append("Used read/write much less than reservation")
        tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = TextBlock("RDS")
        tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = TextBlock("SESv2")
        tb_ret_tmp.lines.append("sesv2 get_account presents excessive information about SES account.")
        tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = TextBlock("Cloudtrail")
        tb_ret_tmp.lines.append(
            "Check there are policies to trail user activity such as Delete and remove deletion protection")
        tb_ret.blocks.append(tb_ret_tmp)

        return tb_ret

    def init_ses(self, permissions_only=False):
        """
        Init SES related entities.
        "ses:GetIdentityDkimAttributes",
                "ses:GetIdentityMailFromDomainAttributes",
                "ses:GetIdentityNotificationAttributes",
                "ses:ListReceiptRuleSets",
                "ses:ListIdentityPolicies",
                "ses:DescribeReceiptRuleSet",
                "ses:GetIdentityPolicies",
                "ses:GetIdentityVerificationAttributes"
                on *

        :param permissions_only:
        :return:
        """

        if not permissions_only and not self.aws_api.sesv2_email_identities:
            self.aws_api.init_sesv2_configuration_sets()
            self.aws_api.init_sesv2_email_identities()
            self.aws_api.init_sesv2_accounts()

        return [{
            "Sid": "SES",
            "Effect": "Allow",
            "Action": ["ses:ListConfigurationSets"],
            "Resource": "*"
        },
            {
                "Sid": "SESConfigSet",
                "Effect": "Allow",
                "Action": ["ses:GetConfigurationSet"],
                "Resource": [
                    f"arn:aws:ses:{region.region_mark}:{self.aws_api.acm_client.account_id}:configuration-set/*"
                    for region in AWSAccount.get_aws_account().regions.values()]
            },
            {
                "Sid": "SESEmailIdentities",
                "Effect": "Allow",
                "Action": ["ses:ListEmailIdentities"],
                "Resource": "*"
            },
            {
                "Sid": "SESEmailIdentity",
                "Effect": "Allow",
                "Action": ["ses:GetEmailIdentity"],
                "Resource": [
                    f"arn:aws:ses:{region.region_mark}:{self.aws_api.acm_client.account_id}:identity/*"
                    for region in AWSAccount.get_aws_account().regions.values()]
            }
        ]

    def init_cloudwatch_metrics(self, permissions_only=False):
        """
        Init cloudwatch metrics.

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

    def init_iam_policies(self, permissions_only=False):
        """
        Init iam policies.

        :return:
        """

        if not permissions_only and not self.aws_api.iam_policies:
            self.aws_api.init_iam_policies()

        return [{
            "Sid": "IamPolicies",
            "Effect": "Allow",
            "Action": "cloudwatch:ListMetrics",
            "Resource": "*"
        }
        ]

    def init_sns(self, permissions_only=False):
        """
        Init SNS topics

        :return:
        """

        if not permissions_only and (not self.aws_api.sns_topics or not self.aws_api.sns_subscriptions):
            self.aws_api.init_sns_topics()
            self.aws_api.init_sns_subscriptions()

        return [{
            "Sid": "cloudwatchMetrics",
            "Effect": "Allow",
            "Action": "cloudwatch:ListMetrics",
            "Resource": "*"
        }
        ]

    def init_event_bridge_rules(self, permissions_only=False):
        """
        Init SNS topics

        :return:
        """
        if not permissions_only and (not self.aws_api.event_bridge_rules):
            self.aws_api.init_event_bridge_rules()

        return [{
            "Sid": "ListEventBridgeRules",
            "Effect": "Allow",
            "Action": "events:ListRules",
            "Resource": "*"
        }
        ]

    def init_autoscaling(self, permissions_only=False):
        """
        Init autoscaling policies

        :return:
        """

        if not permissions_only and (
                not self.aws_api.application_auto_scaling_policies or not self.aws_api.application_auto_scaling_scalable_targets or not self.aws_api.auto_scaling_groups):
            self.aws_api.init_application_auto_scaling_policies()
            self.aws_api.init_application_auto_scaling_scalable_targets()
            self.aws_api.init_auto_scaling_groups()

        return [{
            "Sid": "ApplicationAutoscaling",
            "Effect": "Allow",
            "Action": ["application-autoscaling:DescribeScalingPolicies",
                       "application-autoscaling:DescribeScalableTargets",],
            "Resource": "*"
        },
            {
                "Sid": "Autoscaling",
                "Effect": "Allow",
                "Action": [
                "autoscaling:DescribeAutoScalingGroups",
                "autoscaling:DescribePolicies"
                ],
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
        Init Cloudwatch logs groups and log group metric filters

        :return:
        """

        if not permissions_only and \
                (not self.aws_api.cloud_watch_log_groups or not
                self.aws_api.cloud_watch_log_groups_metric_filters):
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
                "Sid": "SpecificCertificate",
                "Effect": "Allow",
                "Action": ["acm:DescribeCertificate", "acm:ListTagsForCertificate"],
                "Resource": f"arn:aws:acm:{region.region_mark}:{self.aws_api.acm_client.account_id}:certificate/*"
            } for region in AWSAccount.get_aws_account().regions.values()]]

    def init_load_balancers(self, permissions_only=False):
        """
        Init Network, Classic and Application Load Balancers

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
        Init ELB target groups

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
        Init DynamoDB Tables

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
        Init VPC route tables

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
        Init RDS Clusters, Instances, Subnet Groups, Snapshots' metadata

        :return:
        """

        if not permissions_only and (not self.aws_api.rds_db_clusters or
                                     not self.aws_api.rds_db_subnet_groups or
                                     not self.aws_api.rds_db_instances):
            self.aws_api.init_rds_db_clusters(full_information=True)
            self.aws_api.init_rds_db_subnet_groups()
            self.aws_api.init_rds_db_cluster_snapshots()
            self.aws_api.init_rds_db_instances()

        return [
            {
                "Sid": "getRDS",
                "Effect": "Allow",
                "Action": ["rds:DescribeDBClusters", "rds:ListTagsForResource"],
                "Resource": [f"arn:aws:rds:{region.region_mark}:{self.aws_api.acm_client.account_id}:cluster:*" for
                             region in AWSAccount.get_aws_account().regions.values()]
            },
            {
                "Sid": "ListTagsForResourceDB",
                "Effect": "Allow",
                "Action": ["rds:ListTagsForResource"],
                "Resource": [f"arn:aws:rds:{region.region_mark}:{self.aws_api.acm_client.account_id}:db:*" for
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
                    "rds:DescribeDBEngineVersions",
                    "rds:DescribeDBClusterSnapshots",
                    "rds:DescribeDBInstances"
                ],
                "Resource": "*"
            },
            {
                "Sid": "DescribeDBClusterSnapshotAttributes",
                "Effect": "Allow",
                "Action": ["rds:DescribeDBClusterSnapshotAttributes", "rds:ListTagsForResource"],
                "Resource": [f"arn:aws:rds:{region.region_mark}:{self.aws_api.acm_client.account_id}:cluster-snapshot:*"
                             for
                             region in AWSAccount.get_aws_account().regions.values()]
            },
        ]

    def init_elasticsearch_domains(self, permissions_only=False):
        """
        Init Opensearch domains

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
        Init Elasticache clusters

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

    def init_ecs_clusters(self, permissions_only=False):
        """
        Init cloudwatch metrics.

        :return:
        """

        if not permissions_only and not self.aws_api.ecs_clusters:
            self.aws_api.init_ecs_clusters()

        return [{
            "Sid": "ecsClusters",
            "Effect": "Allow",
            "Action": ["ecs:ListClusters", "ecs:DescribeClusters"],
            "Resource": "*"
        }
        ]

    def init_ecs_container_instances(self, permissions_only=False):
        """
        Init cloudwatch metrics.

        :return:
        """

        if not permissions_only and not self.aws_api.ecs_container_instances:
            self.aws_api.init_ecs_container_instances()

        return [{
            "Sid": "ecsContainerInstances",
            "Effect": "Allow",
            "Action": ["ecs:ListContainerInstances", "ecs:DescribeContainerInstances"],
            "Resource": [f"arn:aws:ecs:{region.region_mark}:{self.aws_api.acm_client.account_id}:cluster/*" for region in AWSAccount.get_aws_account().regions.values()]
        }
        ]

    def init_ecs_task_definitions(self, permissions_only=False):
        """
        Init cloudwatch metrics.

        :return:
        """

        if not permissions_only and not self.aws_api.ecs_task_definitions:
            self.aws_api.init_ecs_task_definitions()

        return [{
            "Sid": "ecsTaskDefinitions",
            "Effect": "Allow",
            "Action": ["ecs:ListTaskDefinitions", "ecs:DescribeTaskDefinition"],
            "Resource": "*"
        }
        ]

    def init_ecs_capacity_providers(self, permissions_only=False):
        """
        Init cloudwatch metrics.

        :return:
        """

        if not permissions_only and not self.aws_api.ecs_capacity_providers:
            self.aws_api.init_ecs_capacity_providers()

        return [{
            "Sid": "ecsListDescribeCapacityProviders",
            "Effect": "Allow",
            "Action": "ecs:DescribeCapacityProviders",
            "Resource": "*"
        }
        ]

    def init_ecs_services(self, permissions_only=False):
        """
        Init cloudwatch metrics.

        :return:
        """

        if not permissions_only and not self.aws_api.ecs_services:
            self.aws_api.init_ecs_services()

        return [{
            "Sid": "ecsServices",
            "Effect": "Allow",
            "Action": ["ecs:ListServices", "ecs:DescribeServices"],
            "Resource": "*"
        }
        ]

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
        Generate IAM permissions based on the cleanup_report checks set to active.
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
        Generate multiple Cleanup and Usage reports for EBS Volumes:
        * Unused Volumes.
        * Volumes' types.
        * Sizes report.

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
        Find unattached volumes.

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
        Generate EBS Volume size report.

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
                attachment_string = volume.attachments[0]["InstanceId"]
            except IndexError:
                attachment_string = "Not-attached"

            tb_ret.lines.append(
                f"{volume.availability_zone}, {name}, {volume.volume_type}, {volume.size}GB, {volume.iops}IOPS, Attached:{attachment_string}")
        return tb_ret

    def sub_cleanup_report_ebs_volumes_types(self, permissions_only=False):
        """
        Generate EBS Volume sizes and size summarising by volume type.

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

    def cleanup_report_route_53_service(self, permissions_only=False):
        """
        Route 53 service reports.

        :return:
        """
        if permissions_only:
            permissions = self.sub_cleanup_report_route53_certificates(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_route53_loadbalancers(permissions_only=permissions_only)
            return permissions

        tb_ret = TextBlock("Route53 Report")
        tb_ret_tmp = self.sub_cleanup_report_route53_certificates()
        if tb_ret_tmp.blocks or tb_ret_tmp.lines:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_cleanup_report_route53_loadbalancers()
        if tb_ret_tmp.blocks or tb_ret_tmp.lines:
            tb_ret.blocks.append(tb_ret_tmp)

        with open(self.configuration.route53_report_file_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        logger.info(f"Output in: {self.configuration.route53_report_file_path}")
        return tb_ret

    def sub_cleanup_report_route53_certificates(self, permissions_only=False):
        """
        :return:
        """

        permissions = self.init_hosted_zones(permissions_only=permissions_only)
        permissions += self.init_acm_certificates(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("Route53 Certificate")
        return tb_ret

    def sub_cleanup_report_route53_loadbalancers(self, permissions_only=False):
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
        ACM Certificates cleanups: Unused, ineligible for renew, expired/short expiration period.

        :return:
        """

        if permissions_only:
            permissions = self.sub_cleanup_report_acm_unused(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_acm_failed(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_acm_ineligible(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_acm_expiration(permissions_only=permissions_only)
            return permissions

        tb_ret = TextBlock("ACM Report")

        tb_ret_tmp = self.sub_cleanup_report_acm_failed()
        tb_ret.blocks.append(tb_ret_tmp)

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

    def sub_cleanup_report_acm_failed(self, permissions_only=False):
        """
        ACM ineligible renewal Certificates

        :return:
        """

        permissions = self.init_acm_certificates(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("Failed to validate certificates")

        for certificate in self.aws_api.acm_certificates:
            if certificate.status == "FAILED":
                tb_ret.lines.append(
                    f"[{certificate.domain_name}] {certificate.arn}, Reason: {certificate.failure_reason}")
            for domain_validation_option in certificate.domain_validation_options:
                if domain_validation_option.get("ValidationStatus") == "FAILED":
                    tb_ret.lines.append(
                        f"Validation Domain: '{domain_validation_option.get('ValidationDomain')}' certificate domain: '{certificate.domain_name}' ARN: '{certificate.arn}'")

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
            if certificate.not_after is None:
                continue
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
        Cleanup report for unused ENIs

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
        Generated various lambdas' cleanup reports:

        * Lambdas which were not running - no logs or to old logs.
        * Lambdas with deprecates runtimes.
        * Oversize Lambdas.
        * Lambdas security groups should not have incoming ports.
        * Lambdas code is too old - Lambda was not deployed for too long.

        @return:
        """

        if permissions_only:
            permissions = self.sub_cleanup_report_lambdas_not_running(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_lambdas_deprecate(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_lambdas_large_size(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_lambdas_security_group(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_lambdas_old_code(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_lambdas_monitoring(permissions_only=permissions_only)
            return permissions

        tb_ret = TextBlock("AWS Lambdas cleanup")
        tb_ret_tmp = self.sub_cleanup_report_lambdas_not_running()
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_cleanup_report_lambdas_deprecate()
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_cleanup_report_lambdas_large_size()
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_cleanup_report_lambdas_security_group()
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_cleanup_report_lambdas_old_code()
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_cleanup_report_lambdas_monitoring()
        if tb_ret_tmp:
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
                                           "python3.12": None,
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
            if "Block function create" in table and "Python 3.13" in table:
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
                    f"Lambda '{aws_lambda.name}' never run [Log group does not exist]"
                )
                continue

            log_group = log_groups[0]
            if log_group.stored_bytes == 0:
                tb_ret.lines.append(
                    f"Lambda '{aws_lambda.name}' never run [Log group is empty]"
                )
                continue

            if CommonUtils.timestamp_to_datetime(
                    log_group.creation_time / 1000
            ) > datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=31):
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
        Lambda report checking if the last log stream is too old

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
        ) < datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=365):
            lines.append(
                f"Cloudwatch log group '{log_group.name}' last event was more then year ago: {CommonUtils.timestamp_to_datetime(last_stream['lastIngestionTime'] / 1000)}"
            )
        elif CommonUtils.timestamp_to_datetime(
                last_stream["lastIngestionTime"] / 1000
        ) < datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=62):
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
            f"Lambda '{name}' was last update: {update_date.strftime('%Y-%m-%d %H:%M')}"
            for name, update_date in lst_names_dates
        ]

        return tb_ret

    def sub_cleanup_report_lambdas_monitoring(self, permissions_only=False):
        """
        Lambda monitoring configuration

        * Lambda with no available cloudwatch metrics - looks like an idle Topic.
        * Disabled AWS Lambda cloudwatch alarms.
        * Crucial cloudwatch metrics have no alerts set.

        :return:
        """
        permissions = self.init_lambdas(permissions_only=permissions_only)
        permissions += self.init_cloudwatch_metrics(permissions_only=permissions_only)
        permissions += self.init_cloudwatch_alarms(permissions_only=permissions_only)

        if permissions_only:
            return permissions

        tb_ret = TextBlock("AWS Lambda monitoring report")

        for aws_lambda in self.aws_api.lambdas:
            dimension_value = aws_lambda.name
            namespaces = ["AWS/Lambda"]
            dimension_name = "FunctionName"
            metrics = self.find_cloudwatch_object_by_namespace_and_dimension(self.aws_api.cloud_watch_metrics,
                                                                             namespaces, dimension_name,
                                                                             dimension_value)
            if not metrics:
                tb_ret.lines.append(f"Lambda '{aws_lambda.name}' has no available metrics.")
                continue

            alarms = self.find_cloudwatch_object_by_namespace_and_dimension(self.aws_api.cloud_watch_alarms, namespaces,
                                                                            dimension_name, dimension_value)
            inactive_alarms = []
            crucial_alarms = ["Errors", "Invocations", "Duration", "ConcurrentExecutions"]
            for alarm in alarms:
                if not alarm.actions_enabled:
                    inactive_alarms.append(alarm)
                try:
                    crucial_alarms.remove(alarm.metric_name)
                except ValueError:
                    pass

            tb_ret_tmp = TextBlock(f"Lambda: {aws_lambda.name}")

            if inactive_alarms:
                tb_ret_tmp.lines.append(f"Disabled alarms: {[alarm.name for alarm in inactive_alarms]}")

            if crucial_alarms:
                tb_ret_tmp.lines.append(f"Crucial alarms not set: {crucial_alarms}")

            if tb_ret_tmp.lines:
                tb_ret.blocks.append(tb_ret_tmp)

        return tb_ret if tb_ret.lines or tb_ret.blocks else None

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
        Detect old AMIs. It's important to renew AMIs on a regular basics.

        :return:
        """

        permissions = self.init_ec2_amis(permissions_only=permissions_only)
        permissions += self.init_ec2_instances(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("EC2 half a year and older AMIs.")

        # amis don't have TZ
        # half_year_date = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=6 * 30)
        half_year_date = datetime.datetime.now() - datetime.timedelta(days=6 * 30)

        for inst in self.aws_api.ec2_instances:
            name = inst.name or inst.id
            amis = CommonUtils.find_objects_by_values(self.aws_api.amis, {"id": inst.image_id}, max_count=1)
            if not amis:
                tb_ret.lines.append(f"{name} Can not find AMI, looks like it was either deleted or made private.")
                continue
            ami = amis[0]
            if ami.creation_date < half_year_date:
                tb_ret.lines.append(f"{name} AMI created at: {ami.creation_date}")
        with open(self.configuration.ec2_instances_report_file_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        logger.info(f"Output in: {self.configuration.ec2_instances_report_file_path}")
        return tb_ret

    def cleanup_report_dynamodb(self, permissions_only=False):
        """
        DynamoDB Cleanup:
        * Backups are not enabled.
        * Deletion protection is disabled.

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
        ret = self.find_cloudwatch_metrics_by_namespace_excluding_dimension(["AWS/RDS"], ["DBInstanceIdentifier", "DBClusterIdentifier", "DbClusterIdentifier"])

        :param permissions_only:
        :return:
        """

        permissions = self.init_rds(permissions_only=permissions_only)
        permissions += self.init_route_tables(permissions_only=permissions_only)
        permissions += self.init_security_groups(permissions_only=permissions_only)
        permissions += self.init_subnets(permissions_only=permissions_only)

        if permissions_only:
            permissions += self.sub_cleanup_report_rds_cluster_monitoring(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_rds_instance_monitoring(permissions_only=permissions_only)
            permissions += self.sub_cleanup_report_rds_snapshots(permissions_only=permissions_only)
            return permissions

        tb_ret = TextBlock("RDS Cleanups")
        for cluster in self.aws_api.rds_db_clusters:
            tb_ret_tmp = self.sub_cleanup_report_rds_cluster(cluster)
            if tb_ret_tmp:
                tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_cleanup_report_rds_cluster_monitoring(permissions_only=permissions_only)
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_cleanup_report_rds_instance_monitoring(permissions_only=permissions_only)
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_cleanup_report_rds_snapshots(permissions_only=permissions_only)
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)

        with open(self.configuration.rds_report_file_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        logger.info(f"Output in: {self.configuration.rds_report_file_path}")
        return tb_ret

    def sub_cleanup_report_rds_cluster_monitoring(self, permissions_only=False):
        """
        Metrics and alarms misconfiguration.

        :return:
        """

        permissions = self.init_cloudwatch_alarms(permissions_only=permissions_only)
        permissions += self.init_cloudwatch_metrics(permissions_only=permissions_only)
        permissions = self.init_rds(permissions_only=permissions_only)

        if permissions_only:
            return permissions

        tb_ret = TextBlock("RDS monitoring report")
        for rds_cluster in self.aws_api.rds_db_clusters:
            dimension_value = rds_cluster.id
            namespaces = ["AWS/RDS"]
            dimension_name = "DBClusterIdentifier"
            metrics = self.find_cloudwatch_object_by_namespace_and_dimension(self.aws_api.cloud_watch_metrics,
                                                                             namespaces, dimension_name,
                                                                             dimension_value)
            dimension_name_1 = "DbClusterIdentifier"
            metrics += self.find_cloudwatch_object_by_namespace_and_dimension(self.aws_api.cloud_watch_metrics,
                                                                              namespaces, dimension_name_1,
                                                                              dimension_value)
            if not metrics:
                tb_ret.lines.append(f"RDS Cluster: {rds_cluster.id} has no available metrics.")
                continue

            alarms = self.find_cloudwatch_object_by_namespace_and_dimension(self.aws_api.cloud_watch_alarms, namespaces,
                                                                            dimension_name, dimension_value)
            dimension_name_1 = "DbClusterIdentifier"
            alarms += self.find_cloudwatch_object_by_namespace_and_dimension(self.aws_api.cloud_watch_alarms,
                                                                             namespaces, dimension_name_1,
                                                                             dimension_value)
            inactive_alarms = []
            active_alarms = []
            for alarm in alarms:
                if alarm.actions_enabled:
                    active_alarms.append(alarm)
                else:
                    inactive_alarms.append(alarm)

            tb_ret_tmp = TextBlock(f"RDS Cluster: {rds_cluster.id}")
            if inactive_alarms:
                tb_ret_tmp.lines.append(f"Disabled alarms: {[alarm.name for alarm in inactive_alarms]}")
            elif not active_alarms:
                tb_ret_tmp.lines.append("No Alarms. Following metrics are available:")
                tb_ret_tmp.lines += list({metric.name for metric in metrics})
            if tb_ret_tmp.lines:
                tb_ret.blocks.append(tb_ret_tmp)

        return tb_ret if tb_ret.lines or tb_ret.blocks else None

    def sub_cleanup_report_rds_instance_monitoring(self, permissions_only=False):
        """
        Metrics and alarms misconfiguration.

        :return:
        """

        permissions = self.init_cloudwatch_alarms(permissions_only=permissions_only)
        permissions += self.init_cloudwatch_metrics(permissions_only=permissions_only)
        permissions = self.init_rds(permissions_only=permissions_only)

        if permissions_only:
            return permissions

        tb_ret = TextBlock("RDS monitoring report")
        for rds_instance in self.aws_api.rds_db_instances:
            dimension_value = rds_instance.id
            namespaces = ["AWS/RDS"]
            dimension_name = "DBInstanceIdentifier"
            metrics = self.find_cloudwatch_object_by_namespace_and_dimension(self.aws_api.cloud_watch_metrics,
                                                                             namespaces, dimension_name,
                                                                             dimension_value)
            if not metrics:
                tb_ret.lines.append(f"RDS DB Instance: {rds_instance.id} has no available metrics.")
                continue

            alarms = self.find_cloudwatch_object_by_namespace_and_dimension(self.aws_api.cloud_watch_alarms, namespaces,
                                                                            dimension_name, dimension_value)
            inactive_alarms = []
            active_alarms = []
            for alarm in alarms:
                if alarm.actions_enabled:
                    active_alarms.append(alarm)
                else:
                    inactive_alarms.append(alarm)

            tb_ret_tmp = TextBlock(f"RDS DB Instance: {rds_instance.id}")
            if inactive_alarms:
                tb_ret_tmp.lines.append(f"Disabled alarms: {[alarm.name for alarm in inactive_alarms]}")
            elif not active_alarms:
                tb_ret_tmp.lines.append("No Alarms. Following metrics are available:")
                tb_ret_tmp.lines += list({metric.name for metric in metrics})
            if tb_ret_tmp.lines:
                tb_ret.blocks.append(tb_ret_tmp)

        return tb_ret if tb_ret.lines or tb_ret.blocks else None

    def sub_cleanup_report_rds_snapshots(self, permissions_only=False):
        """
        Metrics and alarms misconfiguration.

        :return:
        """

        permissions = self.init_cloudwatch_alarms(permissions_only=permissions_only)
        permissions += self.init_cloudwatch_metrics(permissions_only=permissions_only)
        permissions += self.init_rds(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("RDS snapshots report")
        for rds_snapshot in self.aws_api.rds_db_cluster_snapshots:
            if not rds_snapshot.storage_encrypted:
                tb_ret.lines.append(f"Snapshot {rds_snapshot.id} unencrypted storage")
            if rds_snapshot.master_username.lower() in ["root", "admin", "administrator"]:
                tb_ret.lines.append(f"Snapshot {rds_snapshot.id} obvious master_username")

        return tb_ret if tb_ret.lines or tb_ret.blocks else None

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
            route_table = self.aws_api.find_route_table_by_subnet(subnet)

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

        :param permissions_only:
        :return:
        """

        tb_ret = TextBlock("Elasticache cleanup")
        permissions = self.init_elasticache_clusters(permissions_only=permissions_only)

        for group in self.aws_api.elasticache_replication_groups:
            if not group.log_delivery_configurations:
                tb_ret.lines.append(f"{group.name} log_delivery_configuration not set")
                breakpoint()
            if group.multi_az == "disabled":
                tb_ret.lines.append(f"{group.name} multi_az disabled")
                breakpoint()
        """
        
            "CacheClusterIds":[
                'string',
            ],
        """
        from horey.aws_api.base_entities.region import Region
        filters_req = {"ReplicationGroupIds": ["demo-us-redis-shared"], "ServiceUpdateName":'elasticache-20241111-arm'}
        ret = list(self.aws_api.elasticache_client.execute(self.aws_api.elasticache_client.get_session_client(Region.get_region("us-west-2")).batch_apply_update_action, None, raw_data=True, filters_req=filters_req))
        ret = list(self.aws_api.elasticache_client.execute(self.aws_api.elasticache_client.get_session_client(Region.get_region("us-west-2")).describe_service_updates, None, raw_data=True))
        ret = list(self.aws_api.elasticache_client.execute(self.aws_api.elasticache_client.get_session_client(Region.get_region("us-west-2")).describe_update_actions, None, raw_data=True))


        if permissions_only:
            return permissions

        self.aws_api.elasticache_replication_groups
        for cluster in self.aws_api.elasticache_clusters:
            breakpoint()
            tb_ret.lines.append(f"{table.name} ike it was either deleted or made private.")

        with open(self.configuration.elasticache_report_file_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        logger.info(f"Output in: {self.configuration.elasticache_report_file_path}")
        return tb_ret

    def cleanup_report_cloudwatch(self, permissions_only=False):
        """
        Checks the following:
        * No metric_filters on logs.
        * No alarms on metric
        * Disabled alarms

        :param permissions_only:
        :return:
        """

        permissions = self.init_cloud_watch_log_groups(permissions_only=permissions_only)
        permissions += self.init_cloudwatch_alarms(permissions_only=permissions_only)

        if permissions_only:
            return permissions

        global_report = Report("Global")

        report = Report(self.aws_api.cloud_watch_logs_client.client_name)
        all_metric_filters = []
        for group in self.aws_api.cloud_watch_log_groups:
            action = ReportActionCloudwatchLogGroup({"region": group.region.region_mark, "name":group.name})
            if group.retention_in_days is None:
                action.no_retention = True

            metric_filters = CommonUtils.find_objects_by_values(self.aws_api.cloud_watch_log_groups_metric_filters,
                                                                {"log_group_name": group.name})
            all_metric_filters += metric_filters
            if not metric_filters:
                action.no_metric_filter = True

            # metrics
            metric_filters_patterns = defaultdict(list)
            for metric_filter in metric_filters:
                if metric_filter.filter_pattern:
                    metric_filters_patterns[metric_filter.filter_pattern].append(metric_filter)

            action.redundant_metric_filters = {filter_pattern: [_metric_filter.name for _metric_filter in _metric_filters] for filter_pattern, _metric_filters in metric_filters_patterns.items() if
                                   len(_metric_filters) > 1}

            last_ingestion_time = self.check_log_group_last_ingestion_exceeded_month(group)
            if last_ingestion_time:
                action.idle = True
                action.reason = f"Last ingestion was {last_ingestion_time.days} days ago"

            report += action

        for i, group in enumerate(sorted(self.aws_api.cloud_watch_log_groups, key=lambda _group: _group.stored_bytes,
                                     reverse=True)[:20]):
            action = ReportActionCloudwatchLogGroup({"region": group.region.region_mark, "name":group.name})
            action.size = {"order": i, "stored_bytes": group.stored_bytes}
            report += action

        if len(all_metric_filters) != len(self.aws_api.cloud_watch_log_groups_metric_filters):
            global_report += self.generate_cleaner_error_report(f"Something went wrong Checked metric filters count "
                                                         f"{len(all_metric_filters)} != fetched via AWS API "
                                                         f"{len(self.aws_api.cloud_watch_log_groups_metric_filters)}")

        global_report += report
        global_report += self.cleanup_report_cloudwatch_logs_metrics(all_metric_filters)
        global_report += self.sub_cleanup_report_cloudwatch_alarms(permissions_only=permissions_only)
        global_report.write_to_file(self.configuration.cloud_watch_report_file_path)

        return global_report

    def check_log_group_last_ingestion_exceeded_month(self, log_group):
        """
        Check if it is idle.

        :param log_group:
        :return:
        """

        now = datetime.datetime.now(tz=datetime.timezone.utc)
        limit = now - datetime.timedelta(days=31)
        if CommonUtils.timestamp_to_datetime(log_group.creation_time/1000) > limit:
            return False

        filters_req = {"orderBy":"LastEventTime", "descending":True}
        for response in self.aws_api.cloud_watch_logs_client.yield_log_group_streams(log_group, filters_req=filters_req):
            break
        else:
            return now - CommonUtils.timestamp_to_datetime(log_group.creation_time/1000)

        last_ingestion_time = CommonUtils.timestamp_to_datetime(
            response.last_ingestion_time / 1000
        )

        if last_ingestion_time > limit:
            return False

        return now - last_ingestion_time

    def generate_cleaner_error_report(self, str_error):
        breakpoint()
        return

    def sub_cleanup_report_cloudwatch_alarms(self, permissions_only=False):
        """


        :param permissions_only:
        :return:
        """

        permissions = self.init_cloud_watch_log_groups(permissions_only=permissions_only)
        permissions += self.init_sns(permissions_only=permissions_only)
        permissions += self.init_autoscaling(permissions_only=permissions_only)
        permissions += self.init_lambdas(permissions_only=permissions_only)
        permissions += self.init_cloudwatch_metrics(permissions_only=permissions_only)
        permissions += self.init_ecs_clusters(permissions_only=permissions_only)
        permissions += self.init_ecs_capacity_providers(permissions_only=permissions_only)
        permissions += self.init_ecs_services(permissions_only=permissions_only)
        permissions += self.init_dynamodb_tables(permissions_only=permissions_only)
        permissions += self.init_sqs_queues(permissions_only=permissions_only)
        permissions += self.init_rds(permissions_only=permissions_only)
        permissions += self.init_event_bridge_rules(permissions_only=permissions_only)
        permissions += self.init_ec2_instances(permissions_only=permissions_only)

        if permissions_only:
            return permissions

        report = Report(self.aws_api.cloud_watch_client.client_name)

        for alarm in self.aws_api.cloud_watch_alarms:
            report += self.sub_cleanup_report_cloudwatch_alarm(alarm)

        return report

    def sub_cleanup_report_cloudwatch_alarm(self, alarm):
        """
        Single alarm actions analysis.

        :param alarm:
        :return:
        """

        lst_ret = []
        all_actions = alarm.alarm_actions + alarm.ok_actions
        if not all_actions:
            report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                        reason="No actions configured")
            report_action.no_active_actions = True
            lst_ret.append(report_action)
        elif not alarm.actions_enabled:
            report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                        reason="All actions disabled")
            report_action.no_active_actions = True
            lst_ret.append(report_action)

        for alarm_action_arn in all_actions:
            if "arn:aws:autoscaling" in alarm_action_arn:
                found_policies = CommonUtils.find_objects_by_values(self.aws_api.application_auto_scaling_policies,
                                                                    {"arn": alarm_action_arn})
                if not found_policies:
                    report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                                reason="Autoscaling policy does not exist")
                    report_action.action_blackholes.append(alarm_action_arn)
                    lst_ret.append(report_action)
            elif "arn:aws:sns" in alarm_action_arn:
                found_topics = CommonUtils.find_objects_by_values(self.aws_api.sns_topics, {"arn": alarm_action_arn})
                if not found_topics:
                    report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                                reason="SNS topic does not exist")
                    report_action.action_blackholes.append(alarm_action_arn)
                    lst_ret.append(report_action)
            elif "arn:aws:lambda" in alarm_action_arn:
                lambdas = CommonUtils.find_objects_by_values(self.aws_api.lambdas, {"arn": alarm_action_arn})
                if not lambdas:
                    report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                                reason="Lambda does not exist")
                    report_action.action_blackholes.append(alarm_action_arn)
                    lst_ret.append(report_action)
            else:
                self.generate_cleaner_error_report(f"{alarm.arn} unknown action: {alarm_action_arn}")

        missing_alarm_dimension_actions = self.sub_cleanup_actions_cloudwatch_alarm_dimensions(alarm)

        lst_ret += missing_alarm_dimension_actions

        if alarm.dimensions:
            for metric in self.aws_api.cloud_watch_metrics:
                if metric.namespace != alarm.namespace:
                    continue
                if metric.name != alarm.metric_name:
                    continue
                metric_dimensions_dict = {dim["Name"]: dim["Value"] for dim in metric.dimensions}
                alarm_dimensions_dict = {dim["Name"]: dim["Value"] for dim in alarm.dimensions}
                if alarm_dimensions_dict != metric_dimensions_dict:
                    continue
                break
            else:
                report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                        reason="Metric does not exist")
                report_action.dimension_balckholes.append(alarm.dimensions)
                lst_ret.append(report_action)
        else:
            metric_filters = CommonUtils.find_objects_by_values(self.aws_api.cloud_watch_log_groups_metric_filters,
                                                                {"name": alarm.metric_name})
            if not metric_filters:
                report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                            reason="Metric filter does not exist")
                report_action.dimension_balckholes.append(alarm.dimensions)
                lst_ret.append(report_action)

        return lst_ret

    def sub_cleanup_actions_cloudwatch_alarm_dimensions(self, alarm):
        """
        Generate alarm dimensions report

        :param alarm:
        :return:
        """

        lst_ret = []
        for dimension in alarm.dimensions:
            match dimension["Name"]:
                case "ClusterName":
                    if not CommonUtils.find_objects_by_values(self.aws_api.ecs_clusters, {"name": dimension["Value"]}):
                        report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                                    reason="Resource does not exist")
                        report_action.dimension_balckholes.append(dimension)
                        lst_ret.append(report_action)
                        break
                case "CapacityProviderName":
                    if not CommonUtils.find_objects_by_values(self.aws_api.ecs_capacity_providers,
                                                              {"name": dimension["Value"]}):
                        report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                                    reason="Resource does not exist")
                        report_action.dimension_balckholes.append(dimension)
                        lst_ret.append(report_action)
                        break
                case "ServiceName":
                    if not CommonUtils.find_objects_by_values(self.aws_api.ecs_services,
                                                              {"name": dimension["Value"]}):
                        report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                                    reason="Resource does not exist")
                        report_action.dimension_balckholes.append(dimension)
                        lst_ret.append(report_action)
                        break
                case "TableName":
                    if alarm.namespace != "AWS/DynamoDB":
                        lst_ret.append(self.generate_cleaner_error_report(f"Alarm {alarm.arn} dimensions in namespace {alarm.namespace} not yet implemented"))
                        continue
                    if not CommonUtils.find_objects_by_values(self.aws_api.dynamodb_tables,
                                                              {"name": dimension["Value"]}):
                        report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                                    reason="Resource does not exist")
                        report_action.dimension_balckholes.append(dimension)
                        lst_ret.append(report_action)
                        break
                case "FunctionName":
                    if alarm.namespace != "AWS/Lambda":
                        lst_ret.append(self.generate_cleaner_error_report(
                            f"Alarm {alarm.arn} dimensions in namespace {alarm.namespace} not yet implemented"))
                        continue
                    if not CommonUtils.find_objects_by_values(self.aws_api.lambdas,
                                                              {"name": dimension["Value"]}):
                        report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                                    reason="Resource does not exist")
                        report_action.dimension_balckholes.append(dimension)
                        lst_ret.append(report_action)
                        break
                case "QueueName":
                    if alarm.namespace != "AWS/SQS":
                        lst_ret.append(self.generate_cleaner_error_report(
                            f"Alarm {alarm.arn} dimensions in namespace {alarm.namespace} not yet implemented"))
                        continue
                    if not CommonUtils.find_objects_by_values(self.aws_api.sqs_queues,
                                                              {"name": dimension["Value"]}):
                        report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                                    reason="Resource does not exist")
                        report_action.dimension_balckholes.append(dimension)
                        lst_ret.append(report_action)
                        break
                case "DBClusterIdentifier":
                    if alarm.namespace != "AWS/RDS":
                        lst_ret.append(self.generate_cleaner_error_report(
                            f"Alarm {alarm.arn} dimensions in namespace {alarm.namespace} not yet implemented"))
                        continue
                    if not CommonUtils.find_objects_by_values(self.aws_api.rds_db_clusters,
                                                              {"id": dimension["Value"]}):
                        report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                                    reason="Resource does not exist")
                        report_action.dimension_balckholes.append(dimension)
                        lst_ret.append(report_action)
                        break
                case "Role":
                    if alarm.namespace != "AWS/RDS":
                        lst_ret.append(self.generate_cleaner_error_report(
                            f"Alarm {alarm.arn} dimensions in namespace {alarm.namespace} not yet implemented"))
                case "DBInstanceIdentifier":
                    if alarm.namespace != "AWS/RDS":
                        lst_ret.append(self.generate_cleaner_error_report(
                            f"Alarm {alarm.arn} dimensions in namespace {alarm.namespace} not yet implemented"))
                        continue
                    if not CommonUtils.find_objects_by_values(self.aws_api.rds_db_instances,
                                                              {"id": dimension["Value"]}):
                        report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                                    reason="Resource does not exist")
                        report_action.dimension_balckholes.append(dimension)
                        lst_ret.append(report_action)
                        break
                case "RuleName":
                    if alarm.namespace != "AWS/Events":
                        lst_ret.append(self.generate_cleaner_error_report(
                            f"Alarm {alarm.arn} dimensions in namespace {alarm.namespace} not yet implemented"))
                        continue
                    if not CommonUtils.find_objects_by_values(self.aws_api.event_bridge_rules,
                                                              {"_name": dimension["Value"]}):
                        report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                                    reason="Resource does not exist")
                        report_action.dimension_balckholes.append(dimension)
                        lst_ret.append(report_action)
                        break
                case "LoadBalancer":
                    if alarm.namespace == "AWS/RDS":
                        self.aws_api.cloud_watch_client.dispose_alarms([alarm])
                        continue
                    breakpoint()
                    if alarm.namespace != "AWS/ALB":
                        lst_ret.append(self.generate_cleaner_error_report(
                            f"Alarm {alarm.arn} dimensions in namespace {alarm.namespace} not yet implemented"))
                        continue
                    if not CommonUtils.find_objects_by_values(self.aws_api.event_bridge_rules,
                                                              {"_name": dimension["Value"]}):
                        report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                                    reason="Resource does not exist")
                        report_action.dimension_balckholes.append(dimension)
                        lst_ret.append(report_action)
                        break
                case "TargetGroup":
                    if alarm.namespace == "AWS/RDS":
                        self.aws_api.cloud_watch_client.dispose_alarms([alarm])
                        continue
                    breakpoint()
                    if alarm.namespace != "AWS/ALB":
                        lst_ret.append(self.generate_cleaner_error_report(
                            f"Alarm {alarm.arn} dimensions in namespace {alarm.namespace} not yet implemented"))
                        continue
                    if not CommonUtils.find_objects_by_values(self.aws_api.event_bridge_rules,
                                                              {"_name": dimension["Value"]}):
                        report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                                    reason="Resource does not exist")
                        report_action.dimension_balckholes.append(dimension)
                        lst_ret.append(report_action)
                        break
                case "AvailabilityZone":
                    if alarm.namespace == "AWS/RDS" and ("TargetGroup" in str(alarm.dimensions) or "LoadBalancer" in str(alarm.dimensions)):
                        self.aws_api.cloud_watch_client.dispose_alarms([alarm])
                        continue
                    breakpoint()

                    if alarm.namespace != "AWS/ALB":
                        lst_ret.append(self.generate_cleaner_error_report(
                            f"Alarm {alarm.arn} dimensions in namespace {alarm.namespace} not yet implemented"))
                        continue
                    if not CommonUtils.find_objects_by_values(self.aws_api.event_bridge_rules,
                                                              {"_name": dimension["Value"]}):
                        report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                                    reason="Resource does not exist")
                        report_action.dimension_balckholes.append(dimension)
                        lst_ret.append(report_action)
                        break
                case "AutoScalingGroupName":
                    if alarm.namespace != "AWS/EC2":
                        lst_ret.append(self.generate_cleaner_error_report(
                            f"Alarm {alarm.arn} dimensions in namespace {alarm.namespace} not yet implemented"))
                        continue
                    if not CommonUtils.find_objects_by_values(self.aws_api.auto_scaling_groups,
                                                              {"name": dimension["Value"]}):
                        report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                                    reason="Resource does not exist")
                        report_action.dimension_balckholes.append(dimension)
                        lst_ret.append(report_action)
                        break
                case "InstanceId":
                    if alarm.namespace != "AWS/EC2":
                        lst_ret.append(self.generate_cleaner_error_report(
                            f"Alarm {alarm.arn} dimensions in namespace {alarm.namespace} not yet implemented"))
                        continue
                    if not CommonUtils.find_objects_by_values(self.aws_api.ec2_instances,
                                                              {"id": dimension["Value"]}):
                        report_action = ReportActionCloudwatchAlarm({"arn": alarm.arn},
                                                                    reason="Resource does not exist")
                        report_action.dimension_balckholes.append(dimension)
                        lst_ret.append(report_action)
                        break
                case _:
                    breakpoint()
                    lst_ret.append(self.generate_cleaner_error_report(
                        f"Alarm {alarm.arn} Unsupported dimensions: {alarm.dimensions}, Namespace: {alarm.namespace}"))

        return lst_ret

    def cleanup_report_cloudwatch_logs_metrics(self, metrics):
        """
        Generate report for cloudwatch_metrics

        :param metrics:
        :return:
        """

        report = Report(self.aws_api.cloud_watch_client.client_name)
        for metric in metrics:
            report += self.sub_cleanup_lines_cloudwatch_log_metric(metric)
        return report

    def sub_cleanup_lines_cloudwatch_log_metric(self, metric):
        """
        Generate report for cloudwatch metric

        :param metric:
        :return:
        """

        action = ReportActionCloudwatchLogGroupMetric({"region": metric.region.region_mark, "name": metric.name})

        if not metric.metric_transformations or len(metric.metric_transformations) > 1:
            raise NotImplementedError("Can not check the metric filter")

        alarms = CommonUtils.find_objects_by_values(self.aws_api.cloud_watch_alarms,
                                                    {"namespace": metric.metric_transformations[
                                                        0]["metricNamespace"],
                                                     "metric_name":
                                                         metric.metric_transformations[
                                                             0]["metricName"]})
        for alarm in alarms:
            if not alarm.actions_enabled:
                action.disabled_actions_alarms.append(alarm.name)
        if len(alarms) == len(action.disabled_actions_alarms):
            action.no_alarms = True

        log_groups = CommonUtils.find_objects_by_values(self.aws_api.cloud_watch_log_groups,
                                                    {"name": metric.log_group_name,
                                                     "region": metric.region})
        if not log_groups:
            action.no_log_group = True
            breakpoint()
        return action

    def cleanup_report_sqs(self, permissions_only=False):
        """
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
        ret = self.find_cloudwatch_metrics_by_namespace_excluding_dimension(["AWS/ApplicationELB", "AWS/NetworkELB"], ["TargetGroup", "LoadBalancer"])

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
        if tb_ret_tmp:
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
                route_table = self.aws_api.find_route_table_by_subnet(subnet)

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
        permissions += self.init_cloudwatch_metrics(permissions_only=permissions_only)
        permissions += self.init_cloudwatch_alarms(permissions_only=permissions_only)

        if permissions_only:
            return permissions

        tb_ret = TextBlock("Load Balancer monitoring report")
        for load_balancer in self.aws_api.load_balancers:
            dimension_value = load_balancer.arn[load_balancer.arn.find(":loadbalancer/") + len(":loadbalancer/"):]
            namespaces = ["AWS/ApplicationELB", "AWS/NetworkELB"]
            dimension_name = "LoadBalancer"
            metrics = self.find_cloudwatch_object_by_namespace_and_dimension(self.aws_api.cloud_watch_metrics,
                                                                             namespaces, dimension_name,
                                                                             dimension_value)
            if not metrics:
                tb_ret.lines.append(f"Load Balancer: {load_balancer.name} has no available metrics.")
                continue

            alarms = self.find_cloudwatch_object_by_namespace_and_dimension(self.aws_api.cloud_watch_alarms, namespaces,
                                                                            dimension_name, dimension_value)
            inactive_alarms = []
            active_alarms = []
            for alarm in alarms:
                if alarm.actions_enabled:
                    active_alarms.append(alarm)
                else:
                    inactive_alarms.append(alarm)

            tb_ret_tmp = TextBlock(f"Load Balancer: {load_balancer.name}")
            if inactive_alarms:
                tb_ret_tmp.lines.append(f"Disabled alarms: {[alarm.name for alarm in inactive_alarms]}")
            elif not active_alarms:
                tb_ret_tmp.lines.append("No Alarms. Following metrics are available:")
                tb_ret_tmp.lines += list({metric.name for metric in metrics})
            if tb_ret_tmp.lines:
                tb_ret.blocks.append(tb_ret_tmp)

        return tb_ret if tb_ret.lines or tb_ret.blocks else None

    def sub_cleanup_target_groups(self, permissions_only=False):
        """
        Cleanup report find unhealthy target groups

        @return:
        """

        permissions = self.init_target_groups(permissions_only=permissions_only)
        permissions += self.init_cloudwatch_alarms(permissions_only=permissions_only)
        permissions += self.init_cloudwatch_metrics(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("Following target groups have health problems")
        for target_group in self.aws_api.target_groups:
            if not target_group.target_health:
                tb_ret.lines.append(target_group.name)

        tb_ret = TextBlock("Target Groups monitoring report")
        for target_group in self.aws_api.target_groups:
            dimension_value = target_group.arn[target_group.arn.find(":targetgroup/") + 1:]
            namespaces = ["AWS/ApplicationELB", "AWS/NetworkELB"]
            dimension_name = "TargetGroup"
            metrics = self.find_cloudwatch_object_by_namespace_and_dimension(self.aws_api.cloud_watch_metrics,
                                                                             namespaces, dimension_name,
                                                                             dimension_value)
            if not metrics:
                tb_ret.lines.append(f"Target Group: {target_group.name} has no available metrics.")
                continue

            alarms = self.find_cloudwatch_object_by_namespace_and_dimension(self.aws_api.cloud_watch_alarms, namespaces,
                                                                            dimension_name, dimension_value)
            inactive_alarms = []
            active_alarms = []
            for alarm in alarms:
                if alarm.actions_enabled:
                    active_alarms.append(alarm)
                else:
                    inactive_alarms.append(alarm)

            tb_ret_tmp = TextBlock(f"Target Group: {target_group.name}")
            if inactive_alarms:
                tb_ret_tmp.lines.append(f"Disabled alarms: {[alarm.name for alarm in inactive_alarms]}")
            elif not active_alarms:
                tb_ret_tmp.lines.append("No Alarms. Following metrics are available:")
                tb_ret_tmp.lines += list({metric.name for metric in metrics})
            if tb_ret_tmp.lines:
                tb_ret.blocks.append(tb_ret_tmp)
        return tb_ret if tb_ret.lines or tb_ret.blocks else None

    def find_cloudwatch_metric_alarms(self, metric, alarms=None):
        """
        Find alarms matching the metric.

        :param metric:
        :param alarms:
        :return:
        """

        alarms = alarms if alarms is not None else self.aws_api.cloud_watch_alarms
        return [alarm for alarm in alarms if
                alarm.metric_name == metric.name and
                alarm.namespace == metric.namespace and
                alarm.dict_dimensions == metric.dict_dimensions]

    @staticmethod
    def find_cloudwatch_object_by_namespace_and_dimension(monitor_objects, namespaces, dimension_name, dimension_value):
        """
        Metrics or alarms are filtered the same way.

        :param monitor_objects:
        :param namespaces:
        :param dimension_name:
        :param dimension_value:
        :return:
        """

        lst_ret = []
        for mon_obj in monitor_objects:
            if mon_obj.namespace not in namespaces:
                continue

            if dimension_value not in [dimension["Value"] for dimension in mon_obj.dimensions if
                                       dimension["Name"] == dimension_name]:
                continue
            lst_ret.append(mon_obj)
        return lst_ret

    def find_cloudwatch_metrics_by_namespace_excluding_dimension(self, namespaces, dimension_names):
        """
        Metrics or alarms are filtered the same way.

        :param namespaces:
        :param dimension_names:
        :return:
        """

        lst_ret = []
        for mon_obj in self.aws_api.cloud_watch_metrics:
            if mon_obj.namespace not in namespaces:
                continue

            for dimension_name in dimension_names:
                if dimension_name in [dimension["Name"] for dimension in mon_obj.dimensions]:
                    break
            else:
                lst_ret.append(mon_obj)
        return lst_ret

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

    def cleanup_report_ses(self, permissions_only=False):
        """
        Generating ses cleanup reports.

        @param permissions_only:
        @return:
        """

        permissions = self.init_ses(permissions_only=permissions_only)
        if permissions_only:
            permissions += self.sub_ses_cloudwatch(permissions_only=permissions_only)
            return permissions

        tb_ret = TextBlock("SES cleanup")

        tb_ret_tmp = self.sub_ses_configuration_set()
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_ses_email_identity()
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_ses_cloudwatch(permissions_only=permissions_only)
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret.write_to_file(self.configuration.ses_report_file_path)
        return tb_ret

    def sub_ses_configuration_set(self):
        """

        :return:
        """

        tb_ret = TextBlock("Configuration sets report")
        for conf_set in self.aws_api.sesv2_configuration_sets:
            if conf_set.reputation_options and \
                    "ReputationMetricsEnabled" in conf_set.reputation_options and \
                    not conf_set.reputation_options.get("ReputationMetricsEnabled"):
                tb_ret.lines.append(f"Configuration Set {conf_set.name} Reputation metrics disabled.")
            if not conf_set.event_destinations:
                tb_ret.lines.append(f"Configuration Set '{conf_set.name}' Event destinations not set.")
            else:
                for event_destination in conf_set.event_destinations:
                    if not event_destination["Enabled"]:
                        tb_ret.lines.append(
                            f"Configuration Set '{conf_set.name}' Event destination '{event_destination['Name']}' disabled")

        return tb_ret if tb_ret.lines or tb_ret.blocks else None

    def sub_ses_email_identity(self):
        """
        Report SES identity.

        :return:
        """

        tb_ret = TextBlock("Email identities report")
        for identity in self.aws_api.sesv2_email_identities:
            if identity.verification_status != "SUCCESS":
                tb_ret.lines.append(f"Email identity '{identity.name}' verification status is not success!")
            if identity.dkim_attributes:
                if "SigningEnabled" in identity.dkim_attributes:
                    if not identity.dkim_attributes["SigningEnabled"]:
                        tb_ret.lines.append(f"Configuration Set '{identity.name}' DKIM Signing is disabled")
        return tb_ret if tb_ret.lines or tb_ret.blocks else None

    def sub_ses_cloudwatch(self, permissions_only=False):
        """
        Report SES cloudwatch monitoring.
        * Configured alarms are enabled.
        * Critical alarms are on - such as Reputation and Bounce.
        * Nice to have alarms are on - such as Send and Received.

        :return:
        """

        permissions = self.init_cloudwatch_alarms(permissions_only=permissions_only)
        permissions += self.init_cloudwatch_metrics(permissions_only=permissions_only)
        if permissions_only:
            return permissions

        tb_ret = TextBlock("SES monitoring report")
        metrics = [metric for metric in self.aws_api.cloud_watch_metrics if metric.namespace == "AWS/SES"]

        alarms = [alarm for alarm in self.aws_api.cloud_watch_alarms if alarm.namespace == "AWS/SES"]
        inactive_alarms = [alarm for alarm in alarms if not alarm.actions_enabled]

        if inactive_alarms:
            tb_ret.lines.append(f"Disabled alarms: {[alarm.name for alarm in inactive_alarms]}")

        if not metrics:
            tb_ret.lines.append("Could find AWS/SES metrics")
            return tb_ret

        recommended_metrics = ["Reputation.BounceRate",
                               "Reputation.ComplaintRate",
                               "Reputation.DeliveriesEligibleForBounceRate",
                               "Reputation.DeliveriesEligibleForComplaintRate",
                               "RenderingFailure",
                               "Bounce", "PublishFailure", "PublishExpired"]
        nice_to_have_metrics = ["Open", "Delivery", "Send", "PublishSuccess", "Received", "Click"]

        known_metrics = recommended_metrics + nice_to_have_metrics
        critical_report = []
        nice_to_have_report = []
        for metric in metrics:
            if {dimension["Name"] for dimension in metric.dimensions} == {"EMAIL", "ORG"}:
                continue

            metric_alarms = self.find_cloudwatch_metric_alarms(metric, alarms=alarms)
            if len(metric_alarms) > 1:
                tb_ret.lines.append(
                    f"Unknown Cloudwatch Metric status. Multiple alarms found for metric: {metric.name}: {[alarm.name for alarm in metric_alarms]}")

            if not metric_alarms:
                if metric.name in recommended_metrics:
                    critical_report.append(
                        f"Critical Alarm missing for metric: {metric.name}. {metric.dict_dimensions}")
                elif metric.name in nice_to_have_metrics:
                    nice_to_have_report.append(
                        f"Nice to have Alarm for metric: {metric.name}. {metric.dict_dimensions}")
                elif metric.name not in known_metrics:
                    tb_ret.lines.append(
                        f"Unknown Cloudwatch Metric: '{metric.name}'. {metric.dict_dimensions}. Can not deside if alarm is needed.")
        tb_ret.lines += critical_report + nice_to_have_report
        return tb_ret if tb_ret.lines or tb_ret.blocks else None

    def cleanup_report_sns(self, permissions_only=False):
        """
        https://docs.aws.amazon.com/sns/latest/dg/sns-topic-attributes.html Amazon SNS message delivery status cloudwatch

        * Data protection policy - monitor unexpected sensitive data.
        * Topics without subscriptions.
        * Encryption is set.
        * Failure feedback to cloudwatch is set.
        * Subscriptions pointing to deleted topics.
        * Dead letter queue is not configured.
        * Topic with no available cloudwatch metrics - looks like an idle Topic.
        * Disabled SNS cloudwatch alarms.
        * Crucial cloudwatch metrics have no alerts set.

        :param permissions_only:
        :return:
        """

        permissions = self.init_cloudwatch_alarms(permissions_only=permissions_only)
        permissions += self.init_cloudwatch_metrics(permissions_only=permissions_only)
        permissions += self.init_sns(permissions_only=permissions_only)

        if permissions_only:
            return permissions

        tb_ret = TextBlock("SNS Cleanup")

        tb_ret_tmp = self.sub_cleanup_report_sns_topics_without_subscriptions()
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_cleanup_report_sns_topics_recommended_configs()
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.sub_cleanup_report_sns_subscriptions_recommended_configs()
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)


        # todo: copied from alarm:
        breakpoint()
        # subscriptions = CommonUtils.find_objects_by_values(self.aws_api.sns_subscriptions,
        if not subscriptions:
            subreport_json["sns_action_blackhole"].append(action)
            errors.append(f"Alarm's '{alarm.name}' action sns-topic has no subscriptions: {action}")

        for subscription in subscriptions:
            if subscription.protocol == "lambda":
                lambdas = CommonUtils.find_objects_by_values(self.aws_api.lambdas,
                                                         {"arn": subscription.endpoint})
                if not lambdas:
                    subreport_json["sns_action_blackhole"].append(action)
                    errors.append(
                        f"Alarm's '{alarm.name}' action sns-topic lambda does not exist: {action}, {subscription.endpoint}")
                    continue
            else:
                raise NotImplementedError("Todo")
        # todo: end copy


        tb_ret_tmp = self.sub_cleanup_report_sns_monitoring()
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret.write_to_file(self.configuration.sns_report_file_path)

        logger.info(f"Output in: {self.configuration.sns_report_file_path}")

        return tb_ret

    def sub_cleanup_report_sns_topics_without_subscriptions(self):
        """
        Topic with no subscriptions

        :return:
        """

        all_subsriptions_topic_arns = [subscription.topic_arn for subscription in self.aws_api.sns_subscriptions]

        tb_ret = TextBlock("SNS topics without subscriptions")
        for topic in self.aws_api.sns_topics:
            if topic.arn not in all_subsriptions_topic_arns:
                tb_ret.lines.append(
                    f"Topic: {topic.arn} has no subscriptions")
        return tb_ret if tb_ret.lines or tb_ret.blocks else None

    def sub_cleanup_report_sns_topics_recommended_configs(self):
        """
        SNS recommended configurations for prod environment.

        * Data protection policy - monitor unexpected sensitive data.
        * Topics without subscriptions.
        * Encryption is set.
        * Failure feedback to cloudwatch is set.

        :return:
        """
        tb_ret = TextBlock("Topics recommended configurations")
        for topic in self.aws_api.sns_topics:
            if not topic.data_protection_policy:
                tb_ret.lines.append(
                    f"Topic: {topic.name} Data Protection Policy was not set")

            if int(topic.attributes.get("SubscriptionsConfirmed")) < 1:
                tb_ret.lines.append(
                    f"Topic: {topic.name} has no confirmed subscriptions")

            if not topic.attributes.get("KmsMasterKeyId"):
                tb_ret.lines.append(
                    f"Topic: {topic.name} Encryption not set")

            for attribute_name, value in topic.attributes.items():
                if "FailureFeedbackRoleArn" in attribute_name and value:
                    break
            else:
                tb_ret.lines.append(
                    f"Topic: {topic.name} Delivery status logging not set")

        return tb_ret if tb_ret.lines or tb_ret.blocks else None

    def sub_cleanup_report_sns_subscriptions_recommended_configs(self):
        """
        SNS recommended configurations for prod environment.
        * Subscriptions pointing to deleted topics.
        * Dead letter queue is not configured.

        :return:
        """

        all_topic_arns = [topic.arn for topic in self.aws_api.sns_topics]
        tb_ret = TextBlock("Subscriptions recommended configurations")
        for subscription in self.aws_api.sns_subscriptions:
            if subscription.topic_arn not in all_topic_arns:
                tb_ret.lines.append(
                    f"Subscription: {subscription.arn} Topic does not exist")

            if not subscription.attributes.get("RedrivePolicy"):
                tb_ret.lines.append(
                    f"Subscription: {subscription.arn} Dead letter queue not configured")
            else:
                policy = json.loads(subscription.attributes.get("RedrivePolicy"))
                if not policy.get("deadLetterTargetArn"):
                    tb_ret.lines.append(
                        f"Subscription: {subscription.arn} Dead letter queue not configured")

        return tb_ret if tb_ret.lines or tb_ret.blocks else None

    def sub_cleanup_report_sns_monitoring(self):
        """
        SNS monitoring configuration

        * Topic with no available cloudwatch metrics - looks like an idle Topic.
        * Disabled SNS cloudwatch alarms.
        * Crucial cloudwatch metrics have no alerts set.

        :return:
        """

        tb_ret = TextBlock("RDS monitoring report")

        for topic in self.aws_api.sns_topics:
            dimension_value = topic.name
            namespaces = ["AWS/SNS"]
            dimension_name = "TopicName"
            metrics = self.find_cloudwatch_object_by_namespace_and_dimension(self.aws_api.cloud_watch_metrics,
                                                                             namespaces, dimension_name,
                                                                             dimension_value)
            if not metrics:
                tb_ret.lines.append(f"Topic: {topic.name} has no available metrics.")
                continue

            alarms = self.find_cloudwatch_object_by_namespace_and_dimension(self.aws_api.cloud_watch_alarms, namespaces,
                                                                            dimension_name, dimension_value)
            inactive_alarms = []
            active_alarms = []
            for alarm in alarms:
                if alarm.actions_enabled:
                    active_alarms.append(alarm)
                else:
                    inactive_alarms.append(alarm)

            tb_ret_tmp = TextBlock(f"Topic: {topic.name}")
            if inactive_alarms:
                tb_ret_tmp.lines.append(f"Disabled alarms: {[alarm.name for alarm in inactive_alarms]}")
            elif not active_alarms:
                tb_ret_tmp.lines.append("No cloudwatch alarms configured. Following metrics are available:")
                tb_ret_tmp.lines += list({metric.name for metric in metrics})
            if tb_ret_tmp.lines:
                tb_ret.blocks.append(tb_ret_tmp)

        return tb_ret if tb_ret.lines or tb_ret.blocks else None

    def cleanup_report_ec2_pricing(self, regions):
        """
        Generate EC2 instance types pricing reports

        :param regions:
        :return:
        """

        for region in regions:
            self.cleanup_report_ec2_pricing_per_region(region)

    def cleanup_report_ec2_pricing_per_region(self, region, permissions_only=False):
        """
        Generate EC2 instance types pricing report per region

        :return:
        """

        if permissions_only:
            permissions = self.sub_cleanup_report_ec2_pricing_per_region(region, permissions_only=permissions_only)
            return permissions

        tb_ret = TextBlock("Pricing cleanup")

        tb_ret_tmp = self.sub_cleanup_report_ec2_pricing_per_region(region)
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret.write_to_file(
            self.configuration.ec2_pricing_per_region_report_file_template.format(region=region.region_mark))
        return tb_ret

    def sub_cleanup_report_ec2_pricing_per_region(self, region, permissions_only=False):
        """
        Generate report based on available region ec2 instance types

        :param region:
        :return:
        """

        if permissions_only:
            return [{
                "Sid": "DescribeInstanceTypes",
                "Effect": "Allow",
                "Action": "ec2:DescribeInstanceTypes",
                "Resource": "*"
            },
                {
                    "Sid": "Pricing",
                    "Effect": "Allow",
                    "Action": ["pricing:ListPriceLists", "pricing:GetPriceListFileUrl"],
                    "Resource": "*"
                }
            ]

        region_instance_types = self.aws_api.ec2_client.get_region_instance_types(region)
        region_instance_types = [_type.instance_type for _type in region_instance_types]

        service_code = "AmazonEC2"
        price_list = self.aws_api.get_price_list(region, service_code)

        region_products = self.get_region_available_instance_type_products(region_instance_types, price_list)
        tb_ret = TextBlock(f"Cleanup report of ec2 pricing in region {region.region_mark}")

        tb_ret_tmp = self.sub_cleanup_report_ec2_cpu_pricing_per_region(region_products, price_list)
        tb_ret.blocks.append(tb_ret_tmp)
        output_file = self.configuration.aws_api_cleanups_ec2_cpu_pricing_file_template.format(
            region=region.region_mark)

        tb_ret_tmp.write_to_file(output_file)
        logger.info(f"Output is at {output_file}")

        tb_ret_tmp = self.sub_cleanup_report_ec2_ratio_pricing_per_region(region_products, price_list)
        tb_ret.blocks.append(tb_ret_tmp)
        return tb_ret

    def sub_cleanup_report_ec2_ratio_pricing_per_region(self, region_products, price_list):
        """
        CPU / RAM ratio pricing.

        :param region_products:
        :param price_list:
        :return:
        """

        available_ratios = defaultdict(list)
        for product in region_products:
            ratio = round(product.cpu / product.float_ram, 3)
            available_ratios[ratio].append(product)
        required_ratios = {0.5: defaultdict(list), 1: defaultdict(list)}

        for cpu_ram_ratio, products_by_price_dict in required_ratios.items():
            min_ratio = cpu_ram_ratio * 0.8
            max_ratio = cpu_ram_ratio * 1.2
            for available_ratio, products in available_ratios.items():
                if min_ratio <= available_ratio <= max_ratio:
                    for product in products:
                        price = self.get_price_by_sku(price_list, product.sku)
                        products_by_price_dict[price].append(product)

        tb_ret = TextBlock("Best prices per ratio")
        for ratio, products_by_price_dict in required_ratios.items():
            tb_ret_ratio = TextBlock(f"Sorted from cheapest: for CPU/RAM {ratio=}")
            for price in sorted(products_by_price_dict):
                types = [
                    f'{product.instance_type}-{product.cpu}/{product.ram}'
                    for product in products_by_price_dict[price]]
                types = list(set(types))
                if types:
                    tb_ret_ratio.lines.append(f"{price=}, {types=}")
            tb_ret.blocks.append(tb_ret_ratio)

        for ratio, price_to_product_dict in required_ratios.items():
            tb_ret_ratio = TextBlock(f"Sorted by price per 1GB RAM: for CPU/RAM {ratio=}")

            dict_per_giga_ram = defaultdict(list)
            for price, products in price_to_product_dict.items():
                for product in products:
                    dict_per_giga_ram[price / product.float_ram].append((price, product))

            for price_per_giga_ram in sorted(dict_per_giga_ram):
                for price, product in dict_per_giga_ram[price_per_giga_ram]:
                    line = f'{product.instance_type}-{product.cpu}/{product.ram}'
                    tb_ret_ratio.lines.append(f"{price_per_giga_ram=}, {price=}, {line}")
            tb_ret.blocks.append(tb_ret_ratio)

        return tb_ret

    @staticmethod
    def get_region_available_instance_type_products(region_instance_types, price_list):
        """
        Get only products available in the region.

        :param region_instance_types:
        :param price_list:
        :return:
        """
        lst_ret = []
        for product in price_list.products.values():
            if product["productFamily"] != "Compute Instance":
                continue

            if product["attributes"]["operatingSystem"] != "Linux":
                continue

            if product["attributes"]["instanceType"] not in region_instance_types:
                continue
            lst_ret.append(PriceListProduct(product))
        return lst_ret

    def sub_cleanup_report_ec2_cpu_pricing_per_region(self, region_products, price_list,
                                                      min_cores=2,
                                                      max_cores=16,
                                                      capacitystatus="Used",
                                                      tenancy="Shared"):
        """
        Generate per cpu costs.
        https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/capacity-reservations-pricing-billing.html
        "For example, if you create a Capacity Reservation for 20 m4.large Linux instances and run 15 m4.large
        Linux instances in the same Availability Zone, you will be charged for 15 active instances and for 5 unused
        instances in the reservation."

        :param max_cores:
        :param min_cores:
        :param region_products:
        :param price_list:
        :param capacitystatus:
        :param tenancy:
        :return:
        """
        seen_types = {}
        tb_ret = TextBlock(
            f"Instance types sorted by single core price [not gravitron, {tenancy=}, {capacitystatus=}, {min_cores=}, {max_cores=}]")
        products_by_cpu_cost = defaultdict(list)
        for product in region_products:
            if product.cpu > max_cores or product.cpu < min_cores:
                continue

            if product.capacitystatus != capacitystatus:
                continue

            if product.tenancy != tenancy:
                continue

            if "graviton" in str(product.physical_processor).lower():
                continue

            price = self.get_price_by_sku(price_list, product.sku)
            if price == 0:
                continue

            products_by_cpu_cost[price / product.cpu].append(product)

        for price in sorted(products_by_cpu_cost):
            price_products = products_by_cpu_cost[price]
            for product in price_products:
                if product.instance_type in seen_types:
                    report_line = f"{price}$: {product.instance_type} [{product.cpu} Cores/ {product.ram} RAM]"
                    for attr_name, attr_value in product.attributes.items():
                        if seen_types[product.instance_type].attributes[attr_name] != attr_value:
                            report_line += " {" + f"{attr_name}: '{seen_types[product.instance_type].attributes[attr_name]}'/'{attr_value}'" + "}"
                else:
                    seen_types[product.instance_type] = product
                    report_line = f"{price}$: {product.instance_type} [{product.cpu} Cores/ {product.ram} RAM]"
                tb_ret.lines.append(report_line)
        return tb_ret

    def cleanup_report_lambda_pricing(self, regions):
        """
        Generate Lambda pricing report

        :return:
        """

        for region in regions:
            self.cleanup_report_lambda_pricing_per_region(region)

    def cleanup_report_lambda_pricing_per_region(self, region):
        """
        Generate Lambda pricing report per region

        :param region:
        :return:
        """

        service_code = "AWSLambda"
        price_lists = self.aws_api.get_price_list(region, service_code)
        prices_with_products = []
        for product in price_lists["products"].values():
            try:
                range_point = None
                if product["attributes"]["usagetype"] in ["Lambda-GB-Second", "Lambda-GB-Second-ARM"]:
                    range_point = 0
                price = self.get_price_by_sku(price_lists, product["sku"], range_point=range_point)
            except self.ServiceUsageRangePointMissingError as error_inst:
                raise RuntimeError(product) from error_inst
            if product["attributes"]["groupDescription"] == "Invocation call for a Lambda function":
                print(product["attributes"])
            prices_with_products.append(
                (price, product["attributes"]["groupDescription"], product["attributes"]["usagetype"]))

        for line in sorted(prices_with_products, key=lambda x: x[0]):
            print(line)

    def get_price_by_sku(self, price_list, sku, range_point=None):
        """
        Get the actual price by SKU.

        :param range_point:
        :param price_list:
        :param sku:
        :return:
        """

        if len(price_list.terms["OnDemand"][sku]) != 1:
            raise NotImplementedError(f"{price_list.terms['OnDemand'][sku]=}")

        for sku_value in price_list.terms["OnDemand"][sku].values():
            if len(sku_value["priceDimensions"]) == 1:
                for price_dimension in sku_value["priceDimensions"].values():
                    return float(price_dimension["pricePerUnit"]["USD"])

            if range_point is None:
                raise self.ServiceUsageRangePointMissingError(
                    f"Range point should be set if there are multiple ranges: {sku_value['priceDimensions']}")

            for price_dimension in sku_value["priceDimensions"].values():
                if float(price_dimension["beginRange"]) <= range_point <= float(price_dimension["endRange"]):
                    return float(price_dimension["pricePerUnit"]["USD"])

        raise RuntimeError(f"Could not find price for SKU: {sku}")

    class ServiceUsageRangePointMissingError(RuntimeError):
        """
        No value set for range decision
        """

    def cleanup_report_iam(self, permissions_only=False):
        """
        Generating ses cleanup reports.

        @param permissions_only:
        @return:
        """

        if permissions_only:
            permissions = self.sub_cleanup_report_iam_policies(permissions_only=permissions_only)
            return permissions

        tb_ret = TextBlock("IAM cleanup")

        tb_ret_tmp = self.sub_cleanup_report_iam_policies()
        if tb_ret_tmp:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret.write_to_file(self.configuration.iam_report_file_path)
        return tb_ret

    def sub_cleanup_report_iam_policies(self, permissions_only=False):
        """
        Generate cleanup report for policies.

        :param permissions_only:
        :return:
        """

        permissions = self.init_iam_policies(permissions_only=permissions_only)
        if permissions_only:
            return permissions

    def cleanup_report_ecs(self, permissions_only=False):
        """
        Checks the ECS best practices.:

        :param permissions_only:
        :return:
        """

        permissions = self.init_ecs_services(permissions_only=permissions_only)
        permissions += self.init_ecs_clusters(permissions_only=permissions_only)
        permissions += self.init_ecs_container_instances(permissions_only=permissions_only)

        if permissions_only:
            return permissions

        global_report = Report("Global")

        global_report += self.cleanup_report_ecs_container_instance_usage()
        global_report.write_to_file(self.configuration.ecs_report_file_path)

        return global_report

    def cleanup_report_ecs_container_instance_usage(self):
        """
        Generate ecs capacity providers report per region

        :return:
        """
        lst_ret = []
        for cluster in self.aws_api.ecs_clusters:
            lst_ret += self.cleanup_report_ecs_container_instance_usage_per_cluster(cluster)
        return lst_ret

    def cleanup_report_ecs_container_instance_usage_per_cluster(self, cluster):
        """
        Generate actions per container instance per cluster

        :param cluster:
        :return:
        """

        lst_ret = []
        cluster_container_instances = CommonUtils.find_objects_by_values(self.aws_api.ecs_container_instances, {"cluster_name": cluster.name})
        if not cluster_container_instances:
            return []

        container_instances_per_cap_provider = defaultdict(list)
        for container_instance in cluster_container_instances:
            container_instances_per_cap_provider[container_instance.capacity_provider_name].append(container_instance)

        for cap_provider_name, container_instances in container_instances_per_cap_provider.items():
            cpu_reserved = 0
            cpu_free = 0
            memory_reserved = 0
            memory_free = 0

            unused_container_instances = []
            for container_instance in container_instances:
                container_instance_remaining_cpu = None
                container_instance_registered_cpu = None
                for resource in container_instance.remaining_resources:
                    if resource["name"] == "CPU":
                        container_instance_remaining_cpu = resource["integerValue"]
                        cpu_free += resource["integerValue"]
                    elif resource["name"] == "MEMORY":
                        memory_free += resource["integerValue"]

                for resource in container_instance.registered_resources:
                    if resource["name"] == "CPU":
                        container_instance_registered_cpu = resource["integerValue"]
                        cpu_reserved += resource["integerValue"]
                    elif resource["name"] == "MEMORY":
                        memory_reserved += resource["integerValue"]

                if container_instance_remaining_cpu is None and container_instance_registered_cpu is None:
                    raise NotImplementedError("container_instance_registered_cpu or container_instance_remaining_cpu is None")
                if container_instance_remaining_cpu == container_instance_registered_cpu:
                    unused_container_instances.append(container_instance)

            if memory_free == memory_reserved and cpu_free == cpu_reserved:
                action = ReportActionECSCapacityProvider({"region": cluster.region.region_mark, "name": cap_provider_name},
                                                         reason=f"Capacity provider has no running tasks. "
                                                                f"Can delete {len(container_instances)} instances."
                                                                "Make sure there are no scheduled tasks configured to run on EC2!")
                action.unused_capacity_provider = True
                lst_ret.append(action)
                continue

            free_cpu_percent = int((cpu_free / cpu_reserved) * 100)
            if free_cpu_percent > 20:
                instance_ids = [unused_container_instance.ec2_instance_id for unused_container_instance in unused_container_instances]
                action = ReportActionECSCapacityProvider({"region": cluster.region.region_mark, "name": cap_provider_name},
                                                 reason=f"Capacity provider usage = {100-free_cpu_percent}% < 80%. "
                                                        f"Delete unused container instances: {instance_ids}")
                action.unused_container_instances = instance_ids
                lst_ret.append(action)

        return lst_ret

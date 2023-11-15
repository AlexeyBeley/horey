"""
Module to handle cross service interaction

"""
# pylint: disable= too-many-lines

import json
import os
import datetime

import time
import zipfile
from collections import defaultdict

from horey.aws_api.aws_clients.ecr_client import ECRClient

from horey.aws_api.aws_clients.ec2_client import EC2Client
from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
from horey.aws_api.aws_services_entities.ec2_security_group import EC2SecurityGroup
from horey.aws_api.aws_services_entities.ec2_spot_fleet_request import (
    EC2SpotFleetRequest,
)
from horey.aws_api.aws_services_entities.ec2_launch_template import EC2LaunchTemplate
from horey.aws_api.aws_services_entities.ec2_launch_template_version import (
    EC2LaunchTemplateVersion,
)

from horey.aws_api.aws_clients.glue_client import GlueClient

from horey.aws_api.aws_clients.ecs_client import ECSClient
from horey.aws_api.aws_clients.pricing_client import PricingClient
from horey.aws_api.aws_clients.auto_scaling_client import AutoScalingClient
from horey.aws_api.aws_clients.application_auto_scaling_client import (
    ApplicationAutoScalingClient,
)
from horey.aws_api.aws_services_entities.auto_scaling_group import AutoScalingGroup
from horey.aws_api.aws_clients.s3_client import S3Client
from horey.aws_api.aws_services_entities.s3_bucket import S3Bucket

from horey.aws_api.aws_clients.elbv2_client import ELBV2Client

from horey.aws_api.aws_clients.acm_client import ACMClient
from horey.aws_api.aws_services_entities.acm_certificate import ACMCertificate

from horey.aws_api.aws_clients.kms_client import KMSClient
from horey.aws_api.aws_services_entities.kms_key import KMSKey

from horey.aws_api.aws_services_entities.managed_prefix_list import ManagedPrefixList

from horey.aws_api.aws_clients.elb_client import ELBClient
from horey.aws_api.aws_services_entities.elb_load_balancer import ClassicLoadBalancer

from horey.aws_api.aws_clients.lambda_client import LambdaClient

from horey.aws_api.aws_clients.route53_client import Route53Client
from horey.aws_api.aws_services_entities.route53_hosted_zone import HostedZone

from horey.aws_api.aws_clients.rds_client import RDSClient
from horey.aws_api.aws_services_entities.rds_db_instance import RDSDBInstance
from horey.aws_api.aws_services_entities.rds_db_cluster_parameter_group import (
    RDSDBClusterParameterGroup,
)
from horey.aws_api.aws_services_entities.rds_db_cluster_snapshot import (
    RDSDBClusterSnapshot,
)
from horey.aws_api.aws_services_entities.rds_db_parameter_group import (
    RDSDBParameterGroup,
)

from horey.aws_api.aws_clients.iam_client import IamClient
from horey.aws_api.aws_services_entities.iam_policy import IamPolicy
from horey.aws_api.aws_services_entities.iam_user import IamUser
from horey.aws_api.aws_services_entities.iam_role import IamRole
from horey.aws_api.aws_services_entities.iam_instance_profile import IamInstanceProfile

from horey.aws_api.aws_clients.cloud_watch_logs_client import CloudWatchLogsClient
from horey.aws_api.aws_services_entities.cloud_watch_log_group import CloudWatchLogGroup
from horey.aws_api.aws_services_entities.cloud_watch_log_group_metric_filter import (
    CloudWatchLogGroupMetricFilter,
)

from horey.aws_api.aws_services_entities.cloud_watch_metric import CloudWatchMetric
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm

from horey.aws_api.aws_clients.cloud_watch_client import CloudWatchClient

from horey.aws_api.aws_clients.dynamodb_client import DynamoDBClient

from horey.aws_api.aws_clients.stepfunctions_client import StepfunctionsClient
from horey.aws_api.aws_clients.cloudfront_client import CloudfrontClient
from horey.aws_api.aws_services_entities.cloudfront_distribution import (
    CloudfrontDistribution,
)
from horey.aws_api.aws_services_entities.cloudfront_origin_access_identity import (
    CloudfrontOriginAccessIdentity,
)

from horey.aws_api.aws_clients.events_client import EventsClient
from horey.aws_api.aws_services_entities.event_bridge_rule import EventBridgeRule

from horey.aws_api.aws_clients.sts_client import STSClient

from horey.aws_api.aws_clients.secrets_manager_client import SecretsManagerClient
from horey.aws_api.aws_services_entities.secrets_manager_secret import (
    SecretsManagerSecret,
)

from horey.aws_api.aws_clients.servicediscovery_client import ServicediscoveryClient
from horey.aws_api.aws_services_entities.servicediscovery_service import (
    ServicediscoveryService,
)
from horey.aws_api.aws_services_entities.servicediscovery_namespace import (
    ServicediscoveryNamespace,
)

from horey.aws_api.aws_clients.elasticsearch_client import ElasticsearchClient
from horey.aws_api.aws_services_entities.elasticsearch_domain import ElasticsearchDomain

from horey.aws_api.aws_clients.elasticache_client import ElasticacheClient
from horey.aws_api.aws_clients.sqs_client import SQSClient
from horey.aws_api.aws_services_entities.elasticache_cluster import ElasticacheCluster
from horey.aws_api.aws_services_entities.elasticache_cache_parameter_group import (
    ElasticacheCacheParameterGroup,
)
from horey.aws_api.aws_services_entities.elasticache_cache_subnet_group import (
    ElasticacheCacheSubnetGroup,
)
from horey.aws_api.aws_services_entities.elasticache_cache_security_group import (
    ElasticacheCacheSecurityGroup,
)
from horey.aws_api.aws_services_entities.elasticache_replication_group import (
    ElasticacheReplicationGroup,
)

from horey.aws_api.aws_services_entities.vpc import VPC
from horey.aws_api.aws_services_entities.subnet import Subnet
from horey.aws_api.aws_services_entities.availability_zone import AvailabilityZone
from horey.aws_api.aws_services_entities.ami import AMI
from horey.aws_api.aws_services_entities.key_pair import KeyPair
from horey.aws_api.aws_services_entities.internet_gateway import InternetGateway
from horey.aws_api.aws_services_entities.vpc_peering import VPCPeering
from horey.aws_api.aws_services_entities.route_table import RouteTable
from horey.aws_api.aws_services_entities.elastic_address import ElasticAddress
from horey.aws_api.aws_services_entities.nat_gateway import NatGateway
from horey.aws_api.aws_services_entities.ecr_repository import ECRRepository
from horey.aws_api.aws_services_entities.ecs_cluster import ECSCluster
from horey.aws_api.aws_services_entities.ecs_capacity_provider import (
    ECSCapacityProvider,
)
from horey.aws_api.aws_services_entities.ecs_service import ECSService
from horey.aws_api.aws_services_entities.lambda_event_source_mapping import (
    LambdaEventSourceMapping,
)
from horey.aws_api.aws_services_entities.dynamodb_table import DynamoDBTable
from horey.aws_api.aws_clients.sesv2_client import SESV2Client
from horey.aws_api.aws_clients.ses_client import SESClient

from horey.aws_api.aws_clients.sns_client import SNSClient

from horey.aws_api.aws_clients.eks_client import EKSClient
from horey.aws_api.aws_services_entities.eks_addon import EKSAddon
from horey.aws_api.aws_services_entities.eks_cluster import EKSCluster

from horey.common_utils.common_utils import CommonUtils

from horey.h_logger import get_logger
from horey.common_utils.text_block import TextBlock

from horey.network.dns_map import DNSMap
from horey.aws_api.base_entities.aws_account import AWSAccount

logger = get_logger()


# pylint: disable=too-many-instance-attributes
class AWSAPI:
    """
    AWS access management and some small functionality to coordinate different services.
    """

    # pylint: disable= too-many-statements
    def __init__(self, configuration=None):
        self.glue_client = GlueClient()
        self.ec2_client = EC2Client()
        self.lambda_client = LambdaClient()
        self.iam_client = IamClient()
        self.s3_client = S3Client()
        self.elbv2_client = ELBV2Client()
        self.elb_client = ELBClient()
        self.rds_client = RDSClient()
        self.route53_client = Route53Client()
        self.cloud_watch_logs_client = CloudWatchLogsClient()
        self.cloud_watch_client = CloudWatchClient()
        self.ecs_client = ECSClient()
        self.pricing_client = PricingClient()
        self.dynamodb_client = DynamoDBClient()
        self.sesv2_client = SESV2Client()
        self.ses_client = SESClient()
        self.sns_client = SNSClient()
        self.autoscaling_client = AutoScalingClient()
        self.application_autoscaling_client = ApplicationAutoScalingClient()
        self.cloudfront_client = CloudfrontClient()
        self.stepfunctions_client = StepfunctionsClient()
        self.events_client = EventsClient()
        self.secretsmanager_client = SecretsManagerClient()
        self.servicediscovery_client = ServicediscoveryClient()
        self.elasticsearch_client = ElasticsearchClient()
        self.ecr_client = ECRClient()
        self.acm_client = ACMClient()
        self.kms_client = KMSClient()
        self.eks_client = EKSClient()
        self.elasticache_client = ElasticacheClient()
        self.sqs_client = SQSClient()
        self.sts_client = STSClient()

        self.network_interfaces = []
        self.iam_policies = []
        self.iam_groups = []
        self.ec2_instances = []
        self.ec2_volumes = []
        self.spot_fleet_requests = []
        self.s3_buckets = []
        self.load_balancers = []
        self.classic_load_balancers = []
        self.hosted_zones = []
        self.users = []
        self.rds_db_instances = []
        self.rds_db_subnet_groups = []
        self.rds_db_cluster_parameter_groups = []
        self.rds_db_cluster_snapshots = []
        self.rds_db_parameter_groups = []
        self.rds_db_clusters = []
        self.security_groups = []
        self.target_groups = []
        self.acm_certificates = []
        self.kms_keys = []
        self.ec2_launch_templates = []
        self.ec2_launch_template_versions = []
        self.lambdas = []
        self.iam_roles = []
        self.iam_instance_profiles = []
        self.cloud_watch_log_groups = []
        self.cloud_watch_log_groups_metric_filters = []
        self.cloud_watch_alarms = []
        self.cloud_watch_metrics = []
        self.cloudfront_distributions = []
        self.cloudfront_origin_access_identities = []
        self.event_bridge_rules = []
        self.secrets_manager_secrets = []
        self.servicediscovery_services = []
        self.servicediscovery_namespaces = []
        self.elasticsearch_domains = []
        self.managed_prefix_lists = []
        self.vpcs = []
        self.subnets = []
        self.availability_zones = []
        self.amis = []
        self.key_pairs = []
        self.internet_gateways = []
        self.vpc_peerings = []
        self.route_tables = []
        self.elastic_addresses = []
        self.nat_gateways = []
        self.dynamodb_tables = []
        self.dynamodb_endpoints = []
        self.sesv2_email_identities = []
        self.ses_identities = []
        self.sesv2_accounts = []
        self.sesv2_email_templates = []
        self.sesv2_configuration_sets = []
        self.ecr_images = []
        self.ecr_repositories = []
        self.ecs_clusters = []
        self.ecs_capacity_providers = []
        self.auto_scaling_groups = []
        self.auto_scaling_policies = []
        self.application_auto_scaling_policies = []
        self.application_auto_scaling_scalable_targets = []
        self.ecs_task_definitions = []
        self.ecs_tasks = []
        self.ecs_services = []
        self.elasticache_clusters = []
        self.elasticache_cache_parameter_groups = []
        self.elasticache_cache_subnet_groups = []
        self.elasticache_cache_security_groups = []
        self.elasticache_replication_groups = []
        self.sqs_queues = []
        self.lambda_event_source_mappings = []
        self.glue_databases = []
        self.glue_tables = []
        self.sns_topics = []
        self.sns_subscriptions = []
        self.eks_addons = []
        self.eks_clusters = []

        self.configuration = configuration
        self.aws_accounts = None
        self.init_configuration()

    def init_configuration(self):
        """
        Sets current active account from configuration
        """

        if self.configuration is None:
            return

        STSClient().main_cache_dir_path = self.configuration.aws_api_cache_dir
        self.aws_accounts = self.get_all_managed_accounts()
        AWSAccount.set_aws_account(
            self.aws_accounts[self.configuration.aws_api_account]
        )

    def get_all_managed_accounts(self):
        """
        Get all accounts from the accounts file.

        @return:
        """

        return CommonUtils.load_object_from_module(
            self.configuration.accounts_file, "main"
        )

    @staticmethod
    def add_managed_region(region):
        """
        Add another region to the managed regions.

        @param region:
        @return:
        """

        account = AWSAccount.get_aws_account()
        account.add_region(region)

    @staticmethod
    def get_managed_regions():
        """
        Get all regions of the current account.

        @return:
        """
        account = AWSAccount.get_aws_account()
        return account.get_regions()

    def init_managed_prefix_lists(
            self, from_cache=False, cache_file=None, region=None, full_information=True
    ):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @param region:
        @param full_information:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ManagedPrefixList)
        else:
            objects = self.ec2_client.get_all_managed_prefix_lists(
                region=region, full_information=full_information
            )

        self.managed_prefix_lists = objects

    def init_vpcs(self, from_cache=False, cache_file=None, region=None):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, VPC)
        else:
            if not isinstance(region, list):
                region = [region]

            objects = []
            for _region in region:
                objects += self.ec2_client.get_all_vpcs(region=_region)

        self.vpcs = objects

    def init_subnets(self, from_cache=False, cache_file=None, region=None):
        """
        Ec2 Subnets

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, Subnet)
        else:
            if not isinstance(region, list):
                region = [region]

            objects = []
            for _region in region:
                objects += self.ec2_client.get_all_subnets(region=_region)

        self.subnets = objects

    def init_glue_tables(self, from_cache=False, cache_file=None, region=None):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, Subnet)
        else:
            if not isinstance(region, list):
                region = [region]

            objects = []
            for _region in region:
                objects += self.glue_client.get_all_tables(region=_region)

        self.glue_tables = objects

    def init_glue_databases(self, from_cache=False, cache_file=None, region=None):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, Subnet)
        else:
            if not isinstance(region, list):
                region = [region]

            objects = []
            for _region in region:
                objects += self.glue_client.get_all_databases(region=_region)

        self.glue_databases = objects

    def init_availability_zones(self, from_cache=False, cache_file=None):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, AvailabilityZone)
        else:
            objects = self.ec2_client.get_all_availability_zones()

        self.availability_zones = objects

    def init_nat_gateways(self, from_cache=False, cache_file=None, region=None):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, NatGateway)
        else:
            objects = self.ec2_client.get_all_nat_gateways(region=region)

        self.nat_gateways = objects

    def init_dynamodb_tables(self, region=None, full_information=False):
        """
        Self-explanatory.

        @param region:
        @param full_information:
        @return:
        """

        self.dynamodb_tables = self.dynamodb_client.get_all_tables(region=region, full_information=full_information)

    def init_dynamodb_endpoints(self, from_cache=False, cache_file=None, region=None):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, DynamoDBTable)
        else:
            objects = self.dynamodb_client.get_all_endpoints(region=region)

        self.dynamodb_endpoints = objects

    def init_sesv2_email_identities(
            self,region=None
    ):
        """
        Standard

        @param region:
        @return:
        """

        self.sesv2_email_identities = self.sesv2_client.get_all_email_identities(region=region)

    def init_ses_identities(
            self, region=None
    ):
        """
        Standard

        @param region:
        @return:
        """

        self.ses_identities = list(self.ses_client.yield_identities(region=region, full_information=True))

    def init_sesv2_accounts(
            self, region=None
    ):
        """
        Standard

        @param region:
        @return:
        """

        self.sesv2_accounts = list(self.sesv2_client.yield_accounts(region=region))

    def init_sesv2_email_templates(self, region=None):
        """
        Standard

        @param region:
        @return:
        """

        self.sesv2_email_templates = self.sesv2_client.get_all_email_templates(region=region)

    def init_sesv2_configuration_sets(
            self, region=None, full_information=True
    ):
        """
        Standard

        @param region:
        @return:
        :param full_information:
        """

        self.sesv2_configuration_sets = self.sesv2_client.get_all_configuration_sets(region=region, full_information=full_information)

    def init_sns_topics(self, region=None):
        """
        Standard.

        @param region:
        @return:
        """

        self.sns_topics = self.sns_client.get_all_topics(region=region)

    def init_sns_subscriptions(self, region=None):
        """
        Standard.

        @param region:
        @return:
        """

        self.sns_subscriptions = self.sns_client.get_all_subscriptions(region=region)

    def init_eks_clusters(self, from_cache=False, region=None):
        """
        Standard.

        @param from_cache:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_from_cache(EKSCluster)
        else:
            objects = self.eks_client.get_all_clusters(region=region)
            self.write_to_cache(objects)

        self.eks_clusters = objects
        return objects

    def init_eks_addons(self, from_cache=False, region=None):
        """
        Standard.

        @param from_cache:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_from_cache(EKSAddon)
        else:
            objects = self.eks_client.get_all_addons(region=region)
            self.write_to_cache(objects)

        self.eks_addons = objects
        return objects

    def init_ecr_images(self):
        """
        Standard.

        @return:
        """

        self.ecr_images = self.ecr_client.get_all_images()

    def init_ecr_repositories(self, from_cache=False, cache_file=None, region=None):
        """
        Standard.

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ECRRepository)
        else:
            objects = self.ecr_client.get_all_repositories(region=region)

        self.ecr_repositories = objects

    def init_ecs_clusters(self, from_cache=False, cache_file=None, region=None):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ECSCluster)
        else:
            objects = self.ecs_client.get_all_clusters(region=region)

        self.ecs_clusters = objects

    def init_ecs_capacity_providers(
            self, from_cache=False, cache_file=None, region=None
    ):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ECSCapacityProvider)
        else:
            objects = self.ecs_client.get_all_capacity_providers(region=region)

        self.ecs_capacity_providers = objects

    def init_ecs_services(self, from_cache=False, cache_file=None, region=None):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        objects = []
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ECSService)
        else:
            for cluster in self.ecs_clusters:
                if region is not None and cluster.region != region:
                    continue
                objects += self.ecs_client.get_all_services(cluster)

        self.ecs_services = objects

    def init_ecs_task_definitions(self, from_cache=False, cache_file=None, region=None):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ECSService)
        else:
            objects = self.ecs_client.get_all_task_definitions(region=region)

        self.ecs_task_definitions = objects

    def init_ecs_tasks(self, from_cache=False, cache_file=None, region=None):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ECSService)
        else:
            objects = self.ecs_client.get_all_tasks(region=region)

        self.ecs_tasks = objects

    def init_auto_scaling_groups(self, from_cache=False, cache_file=None, region=None):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ECSCluster)
        else:
            objects = self.autoscaling_client.get_all_auto_scaling_groups(region=region)

        self.auto_scaling_groups = objects

    def init_auto_scaling_policies(
            self, from_cache=False, cache_file=None, region=None
    ):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ECSCluster)
        else:
            objects = self.autoscaling_client.get_all_policies(region=region)

        self.auto_scaling_policies = objects

    def init_application_auto_scaling_policies(
            self, from_cache=False, cache_file=None, region=None
    ):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ECSCluster)
        else:
            objects = self.application_autoscaling_client.get_all_policies(
                region=region
            )

        self.application_auto_scaling_policies = objects

    def init_application_auto_scaling_scalable_targets(
            self, from_cache=False, cache_file=None, region=None
    ):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ECSCluster)
        else:
            objects = self.application_autoscaling_client.get_all_scalable_targets(
                region=region
            )

        self.application_auto_scaling_scalable_targets = objects

    def init_amis(self, from_cache=False, cache_file=None):
        """
        Standard.

        @param from_cache:
        @param cache_file:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, AMI)
        else:
            objects = self.ec2_client.get_all_amis()

        self.amis = objects

    def init_key_pairs(self, from_cache=False, cache_file=None):
        """
        Ec2 key pairs used for SSH.

        @param from_cache:
        @param cache_file:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, KeyPair)
        else:
            objects = self.ec2_client.get_all_key_pairs()

        self.key_pairs = objects

    def init_internet_gateways(self, from_cache=False, cache_file=None):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, InternetGateway)
        else:
            objects = self.ec2_client.get_all_internet_gateways()

        self.internet_gateways = objects

    def init_vpc_peerings(self, from_cache=False, cache_file=None, region=None):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, VPCPeering)
        else:
            objects = self.ec2_client.get_all_vpc_peerings(region=region)

        self.vpc_peerings = objects

    def init_route_tables(self, from_cache=False, cache_file=None, region=None):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, RouteTable)
        else:
            objects = self.ec2_client.get_all_route_tables(region=region)

        self.route_tables = objects

    def init_elastic_addresses(self, from_cache=False, cache_file=None, region=None):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @param region:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ElasticAddress)
        else:
            objects = self.ec2_client.get_all_elastic_addresses(region=region)

        self.elastic_addresses = objects

    def init_network_interfaces(self):
        """
        Init ec2 instances.

        @return:
        """

        self.network_interfaces = self.ec2_client.get_all_interfaces()

        return self.network_interfaces

    def init_ec2_instances(self, from_cache=False, cache_file=None, region=None):
        """
        Init ec2 instances.

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, EC2Instance)
        else:
            objects = self.ec2_client.get_all_instances(region=region)

        self.ec2_instances = objects

    def init_ec2_volumes(self, region=None):
        """
        Init ec2 volumes.

        @return:
        """

        self.ec2_volumes = self.ec2_client.get_all_volumes(region=region)

    def init_spot_fleet_requests(self, from_cache=False, cache_file=None):
        """
        Init spot fleet requests instances.

        @param from_cache:
        @param cache_file:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, EC2SpotFleetRequest)
        else:
            objects = self.ec2_client.get_all_spot_fleet_requests()

        self.spot_fleet_requests = objects

    def init_ec2_launch_templates(self, from_cache=False, cache_file=None):
        """
        Init ec2 launch templates.

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, EC2LaunchTemplate)
        else:
            objects = self.ec2_client.get_all_ec2_launch_templates()

        self.ec2_launch_templates = objects

    def init_ec2_launch_template_versions(self, from_cache=False, cache_file=None):
        """
        Init ec2 launch template_versions.

        @param from_cache:
        @param cache_file:
        @return:
        """
        objects = []
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, EC2LaunchTemplateVersion)
        else:
            objects += self.ec2_client.get_all_launch_template_versions()

        self.ec2_launch_template_versions = objects

    def init_s3_buckets(self, from_cache=False, cache_file=None, full_information=True):
        """
        Init all s3 buckets.

        @param from_cache:
        @param cache_file:
        @param full_information:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, S3Bucket)
        else:
            objects = self.s3_client.get_all_buckets(full_information=full_information)

        self.s3_buckets = objects

    def init_iam_users(self, from_cache=False, cache_file=None):
        """
        Init IAM users.

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, IamUser)
        else:
            objects = self.iam_client.get_all_users()

        self.users = objects

    def init_iam_roles(self, from_cache=False, cache_file=None):
        """
        Init iam roles

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, IamRole)
        else:
            objects = self.iam_client.get_all_roles()

        self.iam_roles = objects

    def init_iam_instance_profiles(self, from_cache=False, cache_file=None):
        """
        Init iam roles

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, IamInstanceProfile)
        else:
            objects = self.iam_client.get_all_instance_profiles()

        self.iam_instance_profiles = objects

    def cache_raw_cloud_watch_metrics(self, cache_dir):
        """
        Cache the cloudwatch metrics.

        @param cache_dir:
        @return:
        """

        metrics_generator = self.cloud_watch_client.yield_cloud_watch_metrics()
        self.cache_objects_from_generator(metrics_generator, cache_dir)

    def init_cloud_watch_alarms(self, from_cache=False, cache_file=None):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(cache_file, CloudWatchAlarm)
        else:
            objects = self.cloud_watch_client.get_all_alarms()

        self.cloud_watch_alarms = objects

    def init_cloud_watch_metrics(self, update_info=False):
        """
        Self-explanatory.

        @param update_info:
        @return:
        """

        self.cloud_watch_metrics = self.cloud_watch_client.get_all_metrics(update_info=update_info)

    def init_cloud_watch_log_groups(self, from_cache=False, cache_file=None):
        """
        Init the cloudwatch log groups.

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, CloudWatchLogGroup)
        else:
            objects = self.cloud_watch_logs_client.get_cloud_watch_log_groups()

        self.cloud_watch_log_groups = objects

    def init_cloud_watch_log_groups_metric_filters(
            self, from_cache=False, cache_file=None
    ):
        """
        Init the cloudwatch log groups.

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(
                cache_file, CloudWatchLogGroupMetricFilter
            )
        else:
            objects = self.cloud_watch_logs_client.get_log_group_metric_filters()

        self.cloud_watch_log_groups_metric_filters = objects

    def init_and_cache_raw_large_cloud_watch_log_groups(
            self, cloudwatch_log_groups_streams_cache_dir, log_group_names=None
    ):
        """
        Because cloudwatch groups can grow very large I use the same mechanism like in S3.

        @param cloudwatch_log_groups_streams_cache_dir:
        @return:
        """
        log_groups = self.cloud_watch_logs_client.get_cloud_watch_log_groups(
        )
        for log_group in log_groups:
            if log_group_names is not None:
                if log_group.name not in log_group_names:
                    continue
            sub_dir = os.path.join(
                cloudwatch_log_groups_streams_cache_dir, log_group.generate_dir_name()
            )
            os.makedirs(sub_dir, exist_ok=True)
            logger.info(f"Begin collecting from stream: {sub_dir}")

            stream_generator = self.cloud_watch_logs_client.yield_log_group_streams_raw(
                log_group
            )
            self.cache_objects_from_generator(stream_generator, sub_dir)

    def init_iam_policies(self, from_cache=False, cache_file=None):
        """
        Init iam policies.

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, IamPolicy)
        else:
            objects = self.iam_client.get_all_policies()

        self.iam_policies = objects

    def init_iam_groups(self, from_cache=False, cache_file=None):
        """
        Init iam groups.

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, IamPolicy)
        else:
            objects = self.iam_client.get_all_groups()

        self.iam_groups = objects

    def init_and_cache_s3_bucket_objects_synchronous(self, buckets_objects_cache_dir):
        """
        If there are small buckets the caching can be done synchronously:
        Init all objects (RAM) and then run the loop splitting them to files.

        @param buckets_objects_cache_dir:
        @return:
        """
        max_count = 100000
        for bucket in self.s3_buckets:
            bucket_dir = os.path.join(buckets_objects_cache_dir, bucket.name)

            print(bucket.name)
            bucket_objects = list(self.s3_client.yield_bucket_objects(bucket))
            len_bucket_objects = len(bucket_objects)

            os.makedirs(bucket_dir, exist_ok=True)

            if len_bucket_objects == 0:
                continue

            for i in range(int(len_bucket_objects / max_count) + 1):
                first_key_index = max_count * i
                last_key_index = (min(max_count * (i + 1), len_bucket_objects)) - 1
                file_name = bucket_objects[last_key_index].key.replace("/", "_")
                file_path = os.path.join(bucket_dir, file_name)

                data_to_dump = [
                    obj.convert_to_dict()
                    for obj in bucket_objects[first_key_index:last_key_index]
                ]

                with open(file_path, "w", encoding="utf-8") as fd:
                    json.dump(data_to_dump, fd)

            print(f"{bucket.name}: {len(bucket_objects)}")

    def init_and_cache_all_s3_bucket_objects(
            self, buckets_objects_cache_dir, bucket_name=None
    ):
        """
        each bucket object represented as ~388.586973867 B string in file
        :param buckets_objects_cache_dir:
        :param bucket_name:
        :return:
        """
        max_count = 100000
        for bucket in self.s3_buckets:
            if bucket_name is not None and bucket.name != bucket_name:
                continue

            bucket_dir = os.path.join(buckets_objects_cache_dir, bucket.name)
            os.makedirs(bucket_dir, exist_ok=True)
            logger.info(f"Starting collecting from bucket: {bucket.name}")
            try:
                self.cache_s3_bucket_objects(bucket, max_count, bucket_dir)
            except self.s3_client.NoReturnStringError as received_exception:
                logger.warning(
                    f"bucket {bucket.name} has no return string: {received_exception} "
                )
                continue

    def init_lambdas(self, full_information=True):
        """
        Init AWS lambdas
        @param full_information:
        @return:
        """

        self.lambdas = self.lambda_client.get_all_lambdas(
                full_information=full_information
            )

    def init_load_balancers(self, region=None):
        """
        Init elbs v2

        @return:
        """

        self.load_balancers = self.elbv2_client.get_all_load_balancers(region=region)

    def init_classic_load_balancers(self, from_cache=False, cache_file=None):
        """
        Init elbs.

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ClassicLoadBalancer)
        else:
            objects = self.elb_client.get_all_load_balancers()

        self.classic_load_balancers = objects

    def init_hosted_zones(
            self, from_cache=False, cache_file=None, full_information=True
    ):
        """
        Init hosted zones
        @param from_cache:
        @param cache_file:
        @param full_information:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, HostedZone)
        else:
            objects = self.route53_client.get_all_hosted_zones(
                full_information=full_information
            )

        self.hosted_zones = objects

    def init_cloudfront_distributions(
            self, from_cache=False, cache_file=None, full_information=True
    ):
        """
        Init cloudfront distributions
        @param from_cache:
        @param cache_file:
        @param full_information:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, CloudfrontDistribution)
        else:
            objects = self.cloudfront_client.get_all_distributions(
                full_information=full_information
            )

        self.cloudfront_distributions = objects

    def init_cloudfront_origin_access_identities(
            self, from_cache=False, cache_file=None, full_information=True
    ):
        """
        Init cloudfront distributions
        @param from_cache:
        @param cache_file:
        @param full_information:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(
                cache_file, CloudfrontOriginAccessIdentity
            )
        else:
            objects = self.cloudfront_client.get_all_origin_access_identities(
                full_information=full_information
            )

        self.cloudfront_origin_access_identities = objects

    def init_event_bridge_rules(
            self, from_cache=False, cache_file=None, full_information=True
    ):
        """
        Init event_bridge distributions
        @param from_cache:
        @param cache_file:
        @param full_information:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, EventBridgeRule)
        else:
            objects = self.events_client.get_all_rules(
                full_information=full_information
            )

        self.event_bridge_rules = objects

    def init_servicediscovery_services(
            self, from_cache=False, cache_file=None, full_information=True
    ):
        """
        Init servicediscovery serivces
        @param from_cache:
        @param cache_file:
        @param full_information:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ServicediscoveryService)
        else:
            objects = self.servicediscovery_client.get_all_services(
                full_information=full_information
            )

        self.servicediscovery_services = objects

    def init_servicediscovery_namespaces(
            self, from_cache=False, cache_file=None, full_information=True
    ):
        """
        Init servicediscovery serivces
        @param from_cache:
        @param cache_file:
        @param full_information:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(
                cache_file, ServicediscoveryNamespace
            )
        else:
            objects = self.servicediscovery_client.get_all_namespaces(
                full_information=full_information
            )

        self.servicediscovery_namespaces = objects

    def init_elasticsearch_domains(
            self, from_cache=False, cache_file=None,
    ):
        """
        Init elasticsearch services

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ElasticsearchDomain)
        else:
            objects = self.elasticsearch_client.get_all_domains()

        self.elasticsearch_domains = objects

    def init_secrets_manager_secrets(
            self, from_cache=False, cache_file=None, full_information=True
    ):
        """
        Init secrets_manager_secrets
        @param from_cache:
        @param cache_file:
        @param full_information:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, SecretsManagerSecret)
        else:
            objects = self.secretsmanager_client.get_all_secrets(
                full_information=full_information
            )

        self.secrets_manager_secrets = objects

    def init_rds_db_subnet_groups(self, from_cache=False, cache_file=None, region=None):
        """
        Init RDSs

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, RDSDBInstance)
        else:
            objects = self.rds_client.get_all_db_subnet_groups(region=region)

        self.rds_db_subnet_groups = objects

    def init_rds_db_cluster_parameter_groups(
            self, from_cache=False, cache_file=None, region=None
    ):
        """
        Init RDSs

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(
                cache_file, RDSDBClusterParameterGroup
            )
        else:
            objects = self.rds_client.get_all_db_cluster_parameter_groups(region=region)

        self.rds_db_cluster_parameter_groups = objects

    def init_rds_db_cluster_snapshots(
            self, from_cache=False, cache_file=None, region=None
    ):
        """
        Init RDSs

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, RDSDBClusterSnapshot)
        else:
            objects = self.rds_client.get_all_db_cluster_snapshots(region=region)

        self.rds_db_cluster_snapshots = objects

    def init_rds_db_parameter_groups(
            self, from_cache=False, cache_file=None, region=None
    ):
        """
        Init RDSs

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, RDSDBParameterGroup)
        else:
            objects = self.rds_client.get_all_db_parameter_groups(region=region)

        self.rds_db_parameter_groups = objects

    def init_rds_db_instances(self, from_cache=False, cache_file=None, region=None):
        """
        Init RDSs

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, RDSDBInstance)
        else:
            objects = self.rds_client.get_all_db_instances(region=region)

        self.rds_db_instances = objects

    def init_rds_db_clusters(self, from_cache=False, cache_file=None, region=None, full_information=False):
        """
        Init RDSs

        @param from_cache:
        @param cache_file:
        @param full_information:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, RDSDBInstance)
        else:
            objects = self.rds_client.get_all_db_clusters(region=region, full_information=full_information)

        self.rds_db_clusters = objects

    def init_elasticache_clusters(self, from_cache=False, cache_file=None, region=None):
        """

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ElasticacheCluster)
        else:
            objects = self.elasticache_client.get_all_clusters(region=region)

        self.elasticache_clusters = objects

    def init_elasticache_cache_parameter_groups(
            self, from_cache=False, cache_file=None, region=None
    ):
        """

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(
                cache_file, ElasticacheCacheParameterGroup
            )
        else:
            objects = self.elasticache_client.get_all_cache_parameter_groups(
                region=region
            )

        self.elasticache_cache_parameter_groups = objects

    def init_elasticache_cache_subnet_groups(
            self, from_cache=False, cache_file=None, region=None
    ):
        """

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(
                cache_file, ElasticacheCacheSubnetGroup
            )
        else:
            objects = self.elasticache_client.get_all_cache_subnet_groups(region=region)

        self.elasticache_cache_subnet_groups = objects

    def init_elasticache_cache_security_groups(
            self, from_cache=False, cache_file=None, region=None
    ):
        """
        Self explanatory.

        @param from_cache:
        @param cache_file:
        @return:
        """

        if from_cache:
            objects = self.load_objects_from_cache(
                cache_file, ElasticacheCacheSecurityGroup
            )
        else:
            objects = self.elasticache_client.get_all_cache_security_groups(
                region=region
            )

        self.elasticache_cache_security_groups = objects

    def init_elasticache_replication_groups(
            self, from_cache=False, cache_file=None, region=None
    ):
        """

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(
                cache_file, ElasticacheReplicationGroup
            )
        else:
            objects = self.elasticache_client.get_all_replication_groups(region=region)

        self.elasticache_replication_groups = objects

    def init_sqs_queues(self, region=None):
        """
        Standard

        @return:
        """

        self.sqs_queues = self.sqs_client.get_all_queues(region=region)

    def init_lambda_event_source_mappings(
            self, from_cache=False, cache_file=None, region=None
    ):
        """

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, LambdaEventSourceMapping)
        else:
            objects = self.lambda_client.get_all_event_source_mappings(region=region)

        self.lambda_event_source_mappings = objects

    def init_target_groups(self, update_info=False):
        """
        Init ELB target groups

        @param update_info:
        @return:
        """

        self.target_groups = self.elbv2_client.get_all_target_groups(update_info=update_info)

    def init_acm_certificates(self, from_cache=False, cache_file=None):
        """
        Init ELB target groups
        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ACMCertificate)
        else:
            objects = self.acm_client.get_all_certificates()

        self.acm_certificates = objects

    def init_kms_keys(self, from_cache=False, cache_file=None):
        """
        Init ELB target groups
        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, KMSKey)
        else:
            objects = self.kms_client.get_all_keys()

        self.kms_keys = objects

    def init_security_groups(
            self, from_cache=False, cache_file=None
    ):
        """
        Init security groups

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, EC2SecurityGroup)
        else:
            objects = self.ec2_client.get_all_security_groups(
            )
        self.security_groups = objects

    @staticmethod
    def cache_objects_from_generator(generator, sub_dir):
        """
        Run on a generator and write chunks of cache data into files.

        @param generator:
        @param sub_dir:
        @return:
        """
        total_counter = 0
        counter = 0
        max_count = 100000
        buffer = []

        for dict_src in generator:
            counter += 1
            total_counter += 1
            buffer.append(dict_src)

            if counter < max_count:
                continue
            logger.info(f"Objects total_counter: {total_counter}")
            logger.info(f"Writing chunk of {max_count} to file {sub_dir}")

            file_path = os.path.join(sub_dir, str(total_counter))

            with open(file_path, "w", encoding="utf-8") as fd:
                json.dump(buffer, fd)

            counter = 0
            buffer = []

        logger.info(f"Dir {sub_dir} total count of objects: {total_counter}")

        if total_counter == 0:
            return

        file_path = os.path.join(sub_dir, str(total_counter))

        with open(file_path, "w", encoding="utf-8") as fd:
            json.dump(buffer, fd)

    def cache_s3_bucket_objects(self, bucket, max_count, bucket_dir):
        """
        Cache single bucket objects in multiple files - each file is a chunk of objects.
        @param bucket:
        @param max_count:
        @param bucket_dir:
        @return:
        """
        bucket_objects_iterator = self.s3_client.yield_bucket_objects(bucket)
        total_counter = 0
        counter = 0

        buffer = []
        bucket_object = None
        for bucket_object in bucket_objects_iterator:
            counter += 1
            total_counter += 1
            buffer.append(bucket_object)

            if counter < max_count:
                continue

            logger.info(f"Bucket objects total_counter: {total_counter}")
            logger.info(
                f"Writing chunk of {max_count} objects for bucket {bucket.name}"
            )
            counter = 0
            file_name = bucket_object.key.replace("/", "_")
            file_path = os.path.join(bucket_dir, file_name)

            data_to_dump = [obj.convert_to_dict() for obj in buffer]

            buffer = []

            with open(file_path, "w", encoding="utf-8") as fd:
                json.dump(data_to_dump, fd)

        logger.info(f"Bucket {bucket.name} total count of objects: {total_counter}")

        if total_counter == 0:
            return

        file_name = bucket_object.key.replace("/", "_")
        file_path = os.path.join(bucket_dir, file_name)

        data_to_dump = [obj.convert_to_dict() for obj in buffer]

        with open(file_path, "w", encoding="utf-8") as fd:
            json.dump(data_to_dump, fd)

    def load_objects_from_cache(self, file_name, class_type):
        """
        Load objects from cached file

        @param file_name:
        @param class_type:
        @return:
        """
        with open(file_name, encoding="utf-8") as fil:
            return [
                class_type(dict_src, from_cache=True) for dict_src in json.load(fil)
            ]

    def generate_cache_file_path(self, class_type):
        """
        Generate cache file path for this class

        :param class_type:
        :return:
        """

        return os.path.join(self.configuration.aws_api_cache_dir,
                            self.configuration.aws_api_account,
                            class_type.get_cache_file_sub_path())

    def load_from_cache(self, class_type):
        """
        Generate the file path automatically.

        :param class_type:
        :return:
        """
        with open(self.generate_cache_file_path(class_type), encoding="utf-8") as fil:
            return [
                class_type(dict_src, from_cache=True) for dict_src in json.load(fil)
            ]

    def write_to_cache(self, objects, indent=None):
        """
        Prepare a cache file from objects.

        @param objects:
        @return:
        """
        file_path = self.generate_cache_file_path(objects[0])
        objects_dicts = [obj.convert_to_dict() for obj in objects]

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        with open(file_path, "w", encoding="utf-8") as fil:
            json.dump(objects_dicts, fil, indent=indent)

    def cache_objects(self, objects, file_name, indent=None):
        """
        Prepare a cache file from objects.

        @param objects:
        @param file_name:
        @param indent:
        @return:
        """
        objects_dicts = [obj.convert_to_dict() for obj in objects]

        if not os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name))

        with open(file_name, "w", encoding="utf-8") as fil:
            json.dump(objects_dicts, fil, indent=indent)

    def get_down_instances(self):
        """
        Find down instances
        @return:
        """
        ret = []
        for instance in self.ec2_instances:
            # 'state', {'Code': 80, 'Name': 'stopped'})
            if instance.state["Name"] in ["terminated", "stopped"]:
                ret.append(instance)
        return ret

    def prepare_hosted_zones_mapping(self):
        """
        Prepare mapping of a known objects into hosted zones Map

        @return:
        """

        dns_map = DNSMap(self.hosted_zones)
        seed_end_points = []

        for obj in self.ec2_instances:
            seed_end_points.append(obj)

        for obj in self.rds_db_clusters:
            seed_end_points.append(obj)

        for obj in self.load_balancers:
            seed_end_points.append(obj)

        for obj in self.classic_load_balancers:
            seed_end_points.append(obj)

        for obj in self.cloudfront_distributions:
            seed_end_points.append(obj)

        for obj in self.s3_buckets:
            seed_end_points.append(obj)

        for seed in seed_end_points:
            for dns_name in seed.get_dns_records():
                dns_map.add_resource_node(dns_name, seed)

        dns_map.prepare_map()
        return dns_map

    @staticmethod
    def cleanup_report_s3_buckets_objects(summarised_data_file, output_file):
        """
        Generating S3 cleanup report from the previously generated summarized data file.

        @param summarised_data_file:
        @param output_file:
        @return:
        """

        # pylint: disable= too-many-locals
        with open(summarised_data_file, encoding="utf-8") as fh:
            all_buckets = json.load(fh)

        by_bucket_sorted_data = {}

        for bucket_name, bucket_data in all_buckets.items():
            by_bucket_sorted_data[bucket_name] = {
                "total_size": 0,
                "total_keys": 0,
                "years": {},
            }
            logger.info(f"Init bucket '{bucket_name}'")

            for year, year_data in sorted(bucket_data.items(), key=lambda x: x[0]):
                year_dict = {"total_size": 0, "total_keys": 0, "months": {}}
                by_bucket_sorted_data[bucket_name]["years"][year] = year_dict

                for month, month_data in sorted(
                        year_data.items(), key=lambda x: int(x[0])
                ):
                    year_dict["months"][month] = {"total_size": 0, "total_keys": 0}
                    for day_data in month_data.values():
                        year_dict["months"][month]["total_size"] += day_data["size"]
                        year_dict["months"][month]["total_keys"] += day_data["keys"]
                    year_dict["total_size"] += year_dict["months"][month]["total_size"]
                    year_dict["total_keys"] += year_dict["months"][month]["total_keys"]

                by_bucket_sorted_data[bucket_name]["total_size"] += year_dict[
                    "total_size"
                ]
                by_bucket_sorted_data[bucket_name]["total_keys"] += year_dict[
                    "total_keys"
                ]

        tb_ret = TextBlock("Buckets sizes report per years")
        for bucket_name, bucket_data in sorted(
                by_bucket_sorted_data.items(),
                reverse=True,
                key=lambda x: x[1]["total_size"],
        ):
            tb_bucket = TextBlock(
                f"Bucket_Name: '{bucket_name}' size: {CommonUtils.bytes_to_str(bucket_data['total_size'])}, keys: {CommonUtils.int_to_str(bucket_data['total_keys'])}"
            )

            for year, year_data in bucket_data["years"].items():
                tb_year = TextBlock(
                    f"{year} size: {CommonUtils.bytes_to_str(year_data['total_size'])}, keys: {CommonUtils.int_to_str(year_data['total_keys'])}"
                )

                for month, month_data in year_data["months"].items():
                    line = f"Month: {month}, Size: {CommonUtils.bytes_to_str(month_data['total_size'])}, keys: {CommonUtils.int_to_str(month_data['total_keys'])}"
                    tb_year.lines.append(line)

                tb_bucket.blocks.append(tb_year)

            tb_ret.blocks.append(tb_bucket)

        with open(output_file, "w", encoding="utf-8") as fh:
            fh.write(tb_ret.format_pprint())

        return tb_ret

    @staticmethod
    def generate_summarised_s3_cleanup_data(buckets_dir_path, summarised_data_file):
        """
        Because the amount of data can be very large I use data summarization before generating report.
        The data is being written to a file.

        @param buckets_dir_path:
        @param summarised_data_file:
        @return:
        """
        all_buckets = {}
        for bucket_dir in os.listdir(buckets_dir_path):
            by_date_split = defaultdict(
                lambda: defaultdict(lambda: defaultdict(lambda: {"keys": 0, "size": 0}))
            )
            logger.info(f"Init bucket in dir '{bucket_dir}'")

            bucket_dir_path = os.path.join(buckets_dir_path, bucket_dir)
            for objects_buffer_file in os.listdir(bucket_dir_path):
                logger.info(
                    f"Init objects chunk in dir {bucket_dir}/{objects_buffer_file}"
                )
                objects_buffer_file_path = os.path.join(
                    bucket_dir_path, objects_buffer_file
                )

                with open(objects_buffer_file_path, encoding="utf-8") as fh:
                    lst_objects = json.load(fh)

                for dict_object in lst_objects:
                    bucket_object = S3Bucket.BucketObject(dict_object, from_cache=True)
                    by_date_split[bucket_object.last_modified.year][
                        bucket_object.last_modified.month
                    ][bucket_object.last_modified.day]["keys"] += 1
                    by_date_split[bucket_object.last_modified.year][
                        bucket_object.last_modified.month
                    ][bucket_object.last_modified.day]["size"] += bucket_object.size
            all_buckets[bucket_dir] = by_date_split
        with open(summarised_data_file, "w", encoding="utf-8") as fh:
            json.dump(all_buckets, fh)

    @staticmethod
    def cleanup_report_s3_buckets_objects_large(all_buckets):
        """
        Generate cleanup report for s3 large buckets- buckets, with a metadata to large for RAM.

        @param all_buckets:
        @return:
        """

        tb_ret = TextBlock(header="Large buckets")
        lst_buckets_total = []
        for bucket_name, by_year_split in all_buckets:
            bucket_total = sum(
                per_year_data["size"] for per_year_data in by_year_split.values()
            )
            lst_buckets_total.append((bucket_name, bucket_total))

        lst_buckets_total_sorted = sorted(
            lst_buckets_total, reverse=True, key=lambda x: x[1]
        )
        for name, size in lst_buckets_total_sorted[:20]:
            tb_ret.lines.append(f"{name}: {CommonUtils.bytes_to_str(size)}")
        # raise NotImplementedError("Replacement of pdb.set_trace")
        return tb_ret

    def account_id_from_arn(self, arn):
        """
        Fetch Account id from AWS ARN
        @param arn:
        @return:
        """
        if isinstance(arn, list):
            print(arn)
            raise NotImplementedError("Replacement of pdb.set_trace")
        if not arn.startswith("arn:aws:iam::"):
            raise ValueError(arn)

        account_id = arn[len("arn:aws:iam::"):]
        account_id = account_id[: account_id.find(":")]
        if not account_id.isdigit():
            raise ValueError(arn)
        return account_id

    def cleanup_report_iam_roles(self, output_file):
        """
        Generate report

        :param output_file:
        :return:
        """

        time_limit = datetime.datetime.now(
            tz=datetime.timezone.utc
        ) - datetime.timedelta(days=30)
        tb_ret = TextBlock("Unused IAM roles. Last use time > 30 days")

        for role in self.iam_roles:
            if role.role_last_used_time is None:
                tb_ret.lines.append(f"Role: '{role.name}' last used: Never")
                continue
            if role.role_last_used_time < time_limit:
                tb_ret.lines.append(
                    f"Role: '{role.name}' last used: {role.role_last_used_time}"
                )

        with open(output_file, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        return tb_ret

    def cleanup_report_ec2_instances(self, output_file):
        """
        Genreate cleanup report for EC2 instances.

        :param output_file:
        :return:
        """

        tb_ret = TextBlock("EC2 Instances")
        for inst in self.ec2_instances:
            try:
                name = inst.get_tagname()
            except RuntimeError as exception_instance:
                if "No tag" not in repr(exception_instance):
                    raise
                name = inst.id
            logger.info(f"{name}: {inst.cpu_options}")
        with open(output_file, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

    @staticmethod
    def cleanup_report_cloud_watch_metrics(metrics_dir, output_file):
        """
        800 150 130 +50

        @param metrics_dir:
        @param output_file:
        @return:
        """

        tb_ret = TextBlock("Cloudwatch metrics report")
        chunk_files = os.listdir(metrics_dir)
        metrics = None
        for chunk_file_name in chunk_files:
            chunk_file_path = os.path.join(metrics_dir, chunk_file_name)
            with open(chunk_file_path, encoding="utf-8") as file_handler:
                metrics_dicts = json.load(file_handler)

            metrics = [CloudWatchMetric(metric) for metric in metrics_dicts]

        namespaces = defaultdict(list)
        for metric in metrics:
            namespaces[metric.namespace].append(metric)

        for namespace, metrics in sorted(
                namespaces.items(),
                reverse=True,
                key=lambda namespace_metrics: len(namespace_metrics[1]),
        ):
            tb_namespace = TextBlock(
                f"Namespace: '{namespace}', metrics count: '{len(metrics)}'"
            )
            metrics_per_name = defaultdict(list)
            for metric in metrics:
                metrics_per_name[metric.name].append(metric)
            tb_namespace.lines = [
                f"Metric name: '{metric_name}': Different Dimensions: {len(metrics_per_name[metric_name])}"
                for metric_name in metrics_per_name
            ]
            tb_ret.blocks.append(tb_namespace)

        with open(output_file, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())
        return tb_ret

    def cleanup_report_cloud_watch_log_groups(
            self, streams_dir, output_file, top_streams_count=100
    ):
        """
        Generate cleanup report for cloudwatch log groups - too big, too old etc.

        @param streams_dir: Full path to the streams' cache dir
        @param output_file:
        @param top_streams_count: Top most streams count to show in the report.
        @return:
        """
        # pylint: disable= too-many-locals

        dict_total = {"size": 0, "streams_count": 0, "data": []}
        log_group_subdirs = os.listdir(streams_dir)
        for i, log_group_subdir in enumerate(log_group_subdirs):
            logger.info(f"Log group sub directory {i}/{len(log_group_subdirs)}")
            dict_log_group = {
                "name": log_group_subdir,
                "size": 0,
                "streams_count": 0,
                "data": {"streams_by_date": []},
            }
            log_group_full_path = os.path.join(streams_dir, log_group_subdir)

            log_group_chunk_files = os.listdir(log_group_full_path)
            for j, chunk_file in enumerate(log_group_chunk_files):
                logger.info(
                    f"Chunk files in log group dir {j}/{len(log_group_chunk_files)}"
                )

                with open(
                        os.path.join(log_group_full_path, chunk_file), encoding="utf-8"
                ) as fh:
                    streams = json.load(fh)
                log_group_name = streams[0]["arn"].split(":")[6]
                log_group = CommonUtils.find_objects_by_values(
                    self.cloud_watch_log_groups, {"name": log_group_name}, max_count=1
                )[0]
                dict_log_group["size"] = log_group.stored_bytes
                for stream in streams:
                    dict_log_group["streams_count"] += 1
                    self.cleanup_report_cloud_watch_log_groups_handle_sorted_streams(
                        top_streams_count, dict_log_group, stream
                    )

            dict_total["size"] += dict_log_group["size"]
            dict_total["streams_count"] += dict_log_group["streams_count"]
            dict_total["data"].append(dict_log_group)
        dict_total["data"] = sorted(
            dict_total["data"], key=lambda x: x["size"], reverse=True
        )
        tb_ret = self.cleanup_report_cloud_watch_log_groups_prepare_tb(
            dict_total, top_streams_count
        )
        with open(output_file, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())
        return tb_ret

    @staticmethod
    def enter_n_sorted(items, get_item_weight, item_to_insert):
        """
        Inserting item into sorted array.
        items- array of items.
        get_item_weight- function to comapre 2 items- each item in array and candidate.
        item_to_insert - candidate to be inserted

        """
        item_to_insert_weight = get_item_weight(item_to_insert)

        if len(items) == 0:
            raise ValueError("Not inited items (len=0)")

        i = 0
        for i, item in enumerate(items):
            if item_to_insert_weight < get_item_weight(item):
                logger.info(
                    f"Found new item to insert with weight {item_to_insert_weight} at place {i} where current weight is {get_item_weight(item)}"
                )
                break

        while i > -1:
            item_to_insert_tmp = items[i]
            items[i] = item_to_insert
            item_to_insert = item_to_insert_tmp
            i -= 1

    def cleanup_report_cloud_watch_log_groups_handle_sorted_streams(
            self, top_streams_count, dict_log_group, stream
    ):
        """
        Insert cloudwatch log_grup_stream into dict_log_group if it meets the requirements of top_streams_count.
        @param top_streams_count:
        @param dict_log_group:
        @param stream:
        @return:
        """
        if top_streams_count < 0:
            return

        if dict_log_group["streams_count"] < top_streams_count:
            dict_log_group["data"]["streams_by_date"].append(stream)
            return

        if dict_log_group["streams_count"] == top_streams_count:
            dict_log_group["data"]["streams_by_date"] = sorted(
                dict_log_group["data"]["streams_by_date"],
                key=lambda x: -(
                    x["lastIngestionTime"]
                    if "lastIngestionTime" in x
                    else x["creationTime"]
                ),
            )
            return

        self.enter_n_sorted(
            dict_log_group["data"]["streams_by_date"],
            lambda x: -(
                x["lastIngestionTime"]
                if "lastIngestionTime" in x
                else x["creationTime"]
            ),
            stream,
        )

    @staticmethod
    def cleanup_report_cloud_watch_log_groups_prepare_tb(dict_total, top_streams_count):
        """
        Creates the real report from analyzed data.
        @param dict_total:
        @param top_streams_count:
        @return:
        """
        tb_ret = TextBlock("Cloudwatch Logs and Streams")
        line = f"size: {CommonUtils.bytes_to_str(dict_total['size'])} streams: {CommonUtils.int_to_str(dict_total['streams_count'])}"
        tb_ret.lines.append(line)

        for dict_log_group in dict_total["data"]:
            tb_log_group = TextBlock(
                f"{dict_log_group['name']} size: {CommonUtils.bytes_to_str(dict_log_group['size'])}, streams: {CommonUtils.int_to_str(dict_log_group['streams_count'])}"
            )
            logger.info(dict_log_group["name"])

            if dict_log_group["streams_count"] > top_streams_count:
                lines = []
                for stream in dict_log_group["data"]["streams_by_date"]:
                    logger.info(stream["logStreamName"])
                    name = stream["logStreamName"]
                    last_accessed = (
                        stream["lastIngestionTime"]
                        if "lastIngestionTime" in stream
                        else stream["creationTime"]
                    )
                    last_accessed = CommonUtils.timestamp_to_datetime(
                        last_accessed / 1000.0
                    )
                    lines.append(f"{name} last_accessed: {last_accessed}")

                tb_streams_by_date = TextBlock(f"{top_streams_count} ancient streams")
                tb_streams_by_date.lines = lines
                tb_log_group.blocks.append(tb_streams_by_date)

            tb_ret.blocks.append(tb_log_group)
        return tb_ret

    def find_loadbalnacers_target_groups(self, load_balancer):
        """
        Find the loadbalancer's target groups.

        @param load_balancer:
        @return:
        """

        return [
            target_group
            for target_group in self.target_groups
            if load_balancer.arn in target_group.load_balancer_arns
        ]

    def cleanup_report_dns_records(self, output_file):
        """
        Find unused dns records.
        @param output_file: file to print the report in.
        @return:
        """
        tb_ret = TextBlock("DNS cleanup")
        dns_map = self.prepare_hosted_zones_mapping()
        zone_to_records_mapping = defaultdict(list)
        for zone, record in dns_map.unmapped_records:
            zone_to_records_mapping[zone.name].append(record)

        for zone_name, records in zone_to_records_mapping.items():
            tb_zone = TextBlock(f"Hosted zone '{zone_name}'")
            tb_zone.lines = [
                f"{record.name} -> {[resource_record['Value'] for resource_record in record.resource_records]}"
                for record in records
            ]
            tb_ret.blocks.append(tb_zone)

        with open(output_file, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())
        return tb_ret

    def cleanup_report_iam_policies(self, output_file):
        """
        Clean IAM policies

        @return:
        """

        tb_ret = TextBlock("Iam Policies")

        tb_ret.blocks.append(self.cleanup_report_iam_unused_policies())

        tb_ret.blocks.append(self.cleanup_report_iam_policies_statements_optimize())

        with open(output_file, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        return tb_ret

    def cleanup_report_iam_unused_policies(self):
        """
        Generate cleanup report

        @return:
        """

        used_policies = self.find_all_used_policy_names()
        lines = []
        for policy in self.iam_policies:
            if policy.name not in used_policies:
                lines.append(policy.name)

        tb_ret = TextBlock(f"Unused Policies: {len(lines)}")
        tb_ret.lines = lines

        return tb_ret

    def find_all_used_policy_names(self):
        """
        Get all used policies' names
        @return:
        """
        lst_ret = []
        for role in self.iam_roles:
            lst_ret += [policy.name for policy in role.policies]
        return list(set(lst_ret))

    def cleanup_report_iam_policies_statements_optimize(self):
        """
        Optimizing policies and generating report
        @return:
        """
        tb_ret = TextBlock("Iam Policies optimize statements")
        for policy in self.iam_policies:
            logger.info(f"Optimizing policy {policy.name}")
            tb_policy = self.cleanup_report_iam_policy_statements_optimize(policy)
            if tb_policy.blocks or tb_policy.lines:
                tb_ret.blocks.append(tb_policy)

        return tb_ret

    def cleanup_report_iam_policy_statements_optimize(self, policy):
        """
        1) action is not of the resource - solved by AWS in creation process.
        2) resource has no action
        3) effect allow + NotResources
        4) resource arn without existing resource
        5) Resources completely included into other resource
        :param policy:
        :return:
        """

        tb_ret = TextBlock(f"Policy_Name: {policy.name}")
        for statement in policy.document.statements:
            lines = self.cleanup_report_iam_policy_statements_optimize_not_statement(
                statement
            )
            if len(lines) > 0:
                tb_ret.lines += lines

        lines = self.cleanup_report_iam_policy_statements_intersecting_statements(
            policy
        )
        tb_ret.lines += lines

        return tb_ret

    def cleanup_report_iam_policy_statements_optimize_not_statement(self, statement):
        """
        https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_notresource.html
        :param statement:
        :return:
        """
        lines = []

        if statement.effect == statement.Effects.ALLOW:
            if statement.not_action != {}:
                lines.append(
                    f"Potential risk in too permissive not_action. Effect: 'Allow', not_action: '{statement.not_action}'"
                )
            if statement.not_resource is not None:
                lines.append(
                    f"Potential risk in too permissive not_resource. Effect: 'Allow', not_resource: '{statement.not_resource}'"
                )
        return lines

    @staticmethod
    def cleanup_report_iam_policy_statements_intersecting_statements(policy):
        """
        Generating report of intersecting policies.
        @param policy:
        @return:
        """

        statements = policy.document.statements

        lines = []

        for i, statement_1 in enumerate(statements):
            for j in range(i + 1, len(statements)):
                statement_2 = statements[j]
                common_resource = statement_1.intersect_resource(statement_2)

                if len(common_resource) == 0:
                    continue
                common_action = statement_1.intersect_action(statement_2)

                if len(common_action) == 0:
                    continue

                if statement_1.condition is not None:
                    lines.append(f"Statement 1 has condition: {statement_1.condition}")
                if statement_2.condition is not None:
                    lines.append(f"Statement 2 has condition: {statement_2.condition}")
                lines.append(
                    f"Policy: '{policy.name}' Common Action: {common_action} Common resource {common_resource}"
                )
                lines.append(str(statement_1.dict_src))
                lines.append(str(statement_2.dict_src))
        return lines

    def get_secret_value(self, secret_name, region=None, ignore_missing=False):
        """
        Retrieve secret value from secrets manager.

        @param secret_name:
        @param region:
        @param ignore_missing:
        @return:
        """

        return self.secretsmanager_client.raw_get_secret_string(
            secret_name, region=region, ignore_missing=ignore_missing
        )

    def put_secret_value(self, secret_name, value, region=None):
        """
        Save secret in secrets manager service.

        @param secret_name:
        @param value:
        @param region:
        @return:
        """

        return self.secretsmanager_client.raw_put_secret_string(
            secret_name, value, region=region
        )

    def put_secret_file(self, secret_name, file_path, region=None):
        """
        Read file contents into aws secrets manager service secret.

        @param secret_name:
        @param file_path:
        @param region:
        @return:
        """

        with open(file_path, encoding="utf-8") as file_handler:
            contents = file_handler.read()
        self.put_secret_value(secret_name, contents, region=region)

    # pylint: disable= too-many-arguments
    def get_secret_file(self, secret_name, dir_path: str, region=None, file_name=None, ignore_missing=False):
        """
        Get secrets manager value and save it to file.

        @param secret_name:
        @param dir_path:
        @param region:
        @param file_name:
        @param ignore_missing:

        @return:
        """

        if dir_path.endswith(secret_name):
            dir_path = os.path.dirname(dir_path)

        os.makedirs(dir_path, exist_ok=True)
        contents = self.get_secret_value(secret_name, region=region, ignore_missing=ignore_missing)

        if contents is None:
            return None

        if file_name is None:
            file_name = secret_name

        dst_file_path = os.path.join(dir_path, file_name)
        with open(
                dst_file_path, "w+", encoding="utf-8"
        ) as file_handler:
            file_handler.write(contents)
        return dst_file_path

    def copy_secrets_manager_secret_to_region(
            self, secret_name, region_src, region_dst
    ):
        """
        Copy secrets manager secret from one region to another region.

        @param secret_name:
        @param region_src:
        @param region_dst:
        @return:
        """

        secret = self.secretsmanager_client.get_secret(
            secret_name, region_name=region_src
        )
        self.secretsmanager_client.put_secret(secret, region_name=region_dst)

    def provision_managed_prefix_list(self, managed_prefix_list, declarative=False):
        """
        Self explanatory

        @param managed_prefix_list:
        @param declarative:
        @return:
        """

        cidrs = []
        for entry in managed_prefix_list.entries:
            if entry.cidr in cidrs:
                raise ValueError(
                    f"{managed_prefix_list.name} [{managed_prefix_list.region.region_mark}] -"
                    f" multiple entries with same cidr {entry.cidr}"
                )
            cidrs.append(entry.cidr)

        if not declarative:
            descriptions = []
            for entry in managed_prefix_list.entries:
                if entry.description in descriptions:
                    raise ValueError(
                        f"{managed_prefix_list.name} [{managed_prefix_list.region.region_mark}] -"
                        f" multiple entries with same description '{entry.description}'"
                    )
                descriptions.append(entry.description)

        self.ec2_client.provision_managed_prefix_list(
            managed_prefix_list, declarative=declarative
        )

    def provision_hosted_zone(self, hosted_zone, master_hosted_zone_name=None):
        """
        master_hosted_zone_name - in case this hosted zone is a subdomain of some master
        you need to register a NS to point this hosted zone server in the master hosted zone.


        @param hosted_zone:
        @param master_hosted_zone_name:
        @return:
        """
        self.route53_client.provision_hosted_zone(hosted_zone)

        if master_hosted_zone_name is None:
            return

        hzs_master = self.route53_client.get_all_hosted_zones(
            name=master_hosted_zone_name
        )
        if len(hzs_master) > 1:
            raise NotImplementedError(
                f"Found more then 1 hosted zone with name {master_hosted_zone_name}"
            )

        master_hosted_zone = hzs_master[0]

        record = None
        for record in hosted_zone.records:
            if record.type == "NS" and record.name == hosted_zone.name:
                break
        else:
            raise RuntimeError(
                f"Can not find NS record for hosted zone '{hosted_zone.name}'"
            )

        changes = [
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": record.name,
                    "Type": record.type,
                    "TTL": record.ttl,
                    "ResourceRecords": record.resource_records,
                },
            }
        ]

        request = {
            "HostedZoneId": master_hosted_zone.id,
            "ChangeBatch": {"Changes": changes},
        }
        self.route53_client.change_resource_record_sets_raw(request)

    def dispose_hosted_zone_resource_record_sets(self, hosted_zone, records):
        """
        Self explanatory

        @param hosted_zone:
        @param records:
        @return:
        """

        if hosted_zone.id is None:
            self.route53_client.update_hosted_zone_information(
                hosted_zone, full_information=True
            )

        to_del_records_names = [record.name.strip(".") for record in records]

        changes = []

        for existing_record in hosted_zone.records:
            if existing_record.name.strip(".") in to_del_records_names:
                changes.append(existing_record.generate_dispose_request())

        if not changes:
            return
        request = {"HostedZoneId": hosted_zone.id, "ChangeBatch": {"Changes": changes}}
        self.route53_client.change_resource_record_sets_raw(request)

    def dispose_load_balancer(self, load_balancer):
        """
        Self explanatory

        @param load_balancer:
        @return:
        """

        self.elbv2_client.dispose_load_balancer(load_balancer)

    def add_elasticsearch_access_policy_raw_statements(
            self, elasticsearch_domain, raw_statements
    ):
        """
        Add raw statements to Opensesarch service.

        @param elasticsearch_domain:
        @param raw_statements:
        @return:
        """

        access_policies = json.loads(elasticsearch_domain.access_policies)
        new_statements = []
        for raw_statement in raw_statements:
            for access_policies_statement in access_policies["Statement"]:
                if access_policies_statement["Effect"] != raw_statement["Effect"]:
                    continue
                if access_policies_statement["Principal"] != raw_statement["Principal"]:
                    continue
                if access_policies_statement["Action"] != raw_statement["Action"]:
                    continue
                if access_policies_statement["Resource"] != raw_statement["Resource"]:
                    continue
                if (
                        access_policies_statement["Condition"]["IpAddress"]["aws:SourceIp"]
                        != raw_statement["Condition"]["IpAddress"]["aws:SourceIp"]
                ):
                    continue
                break
            else:
                new_statements.append(raw_statement)

        if len(new_statements) == 0:
            return
        access_policies["Statement"] += new_statements
        access_policies_str = json.dumps(access_policies)

        request = {
            "DomainName": elasticsearch_domain.name,
            "AccessPolicies": access_policies_str,
        }
        self.elasticsearch_client.raw_update_elasticsearch_domain_config(
            request, region=elasticsearch_domain.region
        )

    def modify_elasticsearch_access_policy_raw_statements(
            self, elasticsearch_domain, statements_to_add, statements_to_remove
    ):
        """
        Remove raw statements from Opensesarch service.

        @param elasticsearch_domain:
        @param statements_to_add:
        @return:
        """

        access_policies = json.loads(elasticsearch_domain.access_policies)
        new_statements = []
        # remove
        for access_policies_statement in access_policies["Statement"]:
            found = False
            for raw_statement in statements_to_remove:
                if access_policies_statement["Effect"] == raw_statement["Effect"] and \
                        access_policies_statement["Principal"] == raw_statement["Principal"] and \
                        access_policies_statement["Action"] == raw_statement["Action"] and \
                        access_policies_statement["Resource"] == raw_statement["Resource"] and \
                        access_policies_statement["Condition"]["IpAddress"]["aws:SourceIp"] == \
                        raw_statement["Condition"]["IpAddress"]["aws:SourceIp"]:
                    logger.info(f"Removing statement: {raw_statement}")
                    found = True
                    break
            if not found:
                new_statements.append(access_policies_statement)

        # add
        for raw_statement in statements_to_add:
            for access_policies_statement in new_statements:
                if access_policies_statement["Effect"] == raw_statement["Effect"] and \
                        access_policies_statement["Principal"] == raw_statement["Principal"] and \
                        access_policies_statement["Action"] == raw_statement["Action"] and \
                        access_policies_statement["Resource"] == raw_statement["Resource"] and \
                        access_policies_statement["Condition"]["IpAddress"]["aws:SourceIp"] == \
                        raw_statement["Condition"]["IpAddress"]["aws:SourceIp"]:
                    break
            else:
                logger.info(f"Adding statement: {raw_statement}")
                new_statements.append(raw_statement)

        access_policies["Statement"] = new_statements
        access_policies_str = json.dumps(access_policies)

        request = {
            "DomainName": elasticsearch_domain.name,
            "AccessPolicies": access_policies_str,
        }
        self.elasticsearch_client.raw_update_elasticsearch_domain_config(
            request, region=elasticsearch_domain.region
        )

    def provision_cloudwatch_log_group(self, log_group):
        """
        Self explanatory

        @param log_group:
        @return:
        """

        self.cloud_watch_logs_client.provision_log_group(log_group)

    def provision_vpc(self, vpc):
        """
        Self explanatory

        @param vpc:
        @return:
        """

        self.ec2_client.provision_vpc(vpc)

    def provision_subnets(self, subnets):
        """
        Self explanatory

        @param subnets:
        @return:
        """

        self.ec2_client.provision_subnets(subnets)

    def provision_security_group(self, security_group, provision_rules=True):
        """
        Self explanatory

        @param security_group:
        @param provision_rules:
        @return:
        """

        self.ec2_client.provision_security_group(security_group, provision_rules=provision_rules)

    def provision_internet_gateway(self, internet_gateway):
        """
        Self explanatory

        @param internet_gateway:
        @return:
        """

        self.ec2_client.provision_internet_gateway(internet_gateway)

    def provision_vpc_peering(self, vpc_peering):
        """
        Self explanatory

        @param vpc_peering:
        @return:
        """

        self.ec2_client.provision_vpc_peering(vpc_peering)

    def provision_launch_template(self, launch_template):
        """
        Self explanatory

        @param launch_template:
        @return:
        """

        self.ec2_client.provision_launch_template(launch_template)

    def provision_auto_scaling_group(self, autoscaling_group):
        """
        Self explanatory

        @param autoscaling_group:
        @return:
        """

        self.autoscaling_client.provision_auto_scaling_group(autoscaling_group)

    def provision_auto_scaling_policy(self, autoscaling_policy):
        """
        Self explanatory

        @param autoscaling_policy:
        @return:
        """

        self.autoscaling_client.provision_policy(autoscaling_policy)

    def provision_application_auto_scaling_policy(self, autoscaling_policy):
        """
        Self explanatory

        @param autoscaling_policy:
        @return:
        """

        self.application_autoscaling_client.provision_policy(autoscaling_policy)

    def provision_application_auto_scaling_scalable_target(self, target):
        """
        Self explanatory

        @param target:
        @return:
        """

        self.application_autoscaling_client.provision_scalable_target(target)

    def provision_glue_table(self, glue_table):
        """
        Self explanatory

        @param glue_table:
        @return:
        """

        self.glue_client.provision_table(glue_table)

    def provision_glue_database(self, glue_database):
        """
        Self explanatory

        @param glue_database:
        @return:
        """

        self.glue_client.provision_database(glue_database)

    def provision_dynamodb_table(self, dynamodb_table):
        """
        Self explanatory

        @param dynamodb_table:
        @return:
        """

        self.dynamodb_client.provision_table(dynamodb_table)

    def provision_nat_gateways(self, nat_gateways):
        """
        Self explanatory

        @param nat_gateways:
        @return:
        """

        for nat_gateway in nat_gateways:
            self.provision_nat_gateway(nat_gateway)

        aws_propagation_timeout = 60
        time_to_sleep = 10
        nat_gateways_tmp = nat_gateways[:]
        while len(nat_gateways_tmp) > 0:
            to_del = []
            for nat_gateway_tmp in nat_gateways_tmp:
                for region_gateway in self.ec2_client.get_region_nat_gateways(
                        nat_gateways_tmp[0].region
                ):
                    if region_gateway.get_state() not in [
                        region_gateway.State.PENDING,
                        region_gateway.State.AVAILABLE,
                    ]:
                        continue

                    if region_gateway.id == nat_gateway_tmp.id:
                        if region_gateway.get_state() == region_gateway.State.AVAILABLE:
                            to_del.append(nat_gateway_tmp)
                            break
                        break
                else:
                    if aws_propagation_timeout <= 0:
                        raise RuntimeError(
                            f"Can not find nat_gateway '{nat_gateway_tmp.get_tagname()}' in region nat_gateways"
                        )
                    aws_propagation_timeout -= time_to_sleep

            for ngw in to_del:
                nat_gateways_tmp.remove(ngw)

            if nat_gateways_tmp:
                logger.info(
                    f"Waiting for {len(nat_gateways_tmp)} NAT gateways creation. Going to sleep for {time_to_sleep} seconds"
                )
                time.sleep(time_to_sleep)

    def provision_nat_gateway(self, nat_gateway):
        """
        Self explanatory

        @param nat_gateway:
        @return:
        """

        self.ec2_client.provision_nat_gateway(nat_gateway)

    def provision_elastic_address(self, elastic_address):
        """
        Self explanatory

        @param elastic_address:
        @return:
        """

        self.ec2_client.provision_elastic_address(elastic_address)

    def provision_route_table(self, route_table):
        """
        Self explanatory

        @param route_table:
        @return:
        """

        self.ec2_client.provision_route_table(route_table)

    def provision_ec2_instance(self, ec2_instance, wait_until_active=False):
        """
        Self explanatory

        @param ec2_instance:
        @param wait_until_active:
        @return:
        """

        self.ec2_client.provision_ec2_instance(
            ec2_instance, wait_until_active=wait_until_active
        )

    def provision_ecs_capacity_provider(self, ecs_capacity_provider):
        """
        Self explanatory

        @param ecs_capacity_provider:
        @return:
        """

        self.ecs_client.provision_capacity_provider(ecs_capacity_provider)

    def provision_ecs_cluster(self, ecs_cluster):
        """
        Self explanatory

        @param ecs_cluster:
        @return:
        """

        self.ecs_client.provision_cluster(ecs_cluster)

    def provision_ecs_service(self, ecs_service, wait_timeout=10*60):
        """
        Self explanatory

        @param ecs_service:
        @param wait_timeout:
        @return:
        """

        self.ecs_client.provision_service(ecs_service, wait_timeout=wait_timeout)

    def provision_key_pair(
            self, key_pair: KeyPair, save_to_secrets_manager=None, secrets_manager_region=None
    ):
        """
        Self explanatory

        @param key_pair:
        @param save_to_secrets_manager:
        @param secrets_manager_region:
        @return:
        """

        logger.info(f"provisioning ssh key pair {key_pair.name}")
        if key_pair.key_type is None:
            key_pair.key_type = "ed25519"

        response = self.ec2_client.provision_key_pair(key_pair)
        if response is None:
            return None

        if save_to_secrets_manager:
            AWSAccount.set_aws_region(secrets_manager_region)
            self.put_secret_value(key_pair.name if key_pair.name.endswith(".key") else key_pair.name + ".key",
                                  response["KeyMaterial"])

        return response

    def provision_generated_ssh_key(
            self, output_file_path, owner_email, region
    ):
        """
        Self explanatory

        @param output_file_path:
        @param owner_email:
        @param region:
        @return:
        """

        logger.info(f"Generating ssh key pair {output_file_path}")
        key_name = os.path.basename(output_file_path)
        output_public_file_path = output_file_path + ".pub"
        key_name_public = key_name + ".pub"
        key_value = self.secretsmanager_client.raw_get_secret_string(key_name, region=region, ignore_missing=True)
        key_public_value = self.secretsmanager_client.raw_get_secret_string(key_name_public, region=region,
                                                                            ignore_missing=True)

        if (key_value is None) ^ (key_public_value is None):
            raise RuntimeError(f"Either {key_name} or {key_name_public} does not exist in Secrets manager")

        if key_value is not None:
            logger.info(f"Found {key_name} and {key_name_public} in secrets")
            with open(output_file_path, "w", encoding="utf-8") as file_handler:
                file_handler.write(key_value)

            with open(output_public_file_path, "w", encoding="utf-8") as file_handler:
                file_handler.write(key_public_value)

            return

        CommonUtils.generate_ed25519_key(owner_email, output_file_path)

        AWSAccount.set_aws_region(region)
        logger.info(f"Generated {key_name} and {key_name_public}. Uploading to secrets")
        self.put_secret_file(key_name, output_file_path)
        self.put_secret_file(key_name_public, output_public_file_path)

    def provision_load_balancer(self, load_balancer):
        """
        Self explanatory

        @param load_balancer:
        @return:
        """

        self.elbv2_client.provision_load_balancer(load_balancer)

    def provision_load_balancer_target_group(self, load_balancer):
        """
        Self explanatory

        @param load_balancer:
        @return:
        """

        self.elbv2_client.provision_load_balancer_target_group(load_balancer)

    def provision_load_balancer_listener(self, listener):
        """
        Self explanatory

        @param listener:
        @return:
        """

        self.elbv2_client.provision_load_balancer_listener(listener)

    def provision_load_balancer_rule(self, rule):
        """
        Self explanatory

        @param rule:
        @return:
        """

        self.elbv2_client.provision_load_balancer_rule(rule)

    def associate_elastic_address(self, ec2_instance, elastic_address):
        """
        Self explanatory

        @param ec2_instance:
        @param elastic_address:
        @return:
        """

        request = {"AllocationId": elastic_address.id, "InstanceId": ec2_instance.id}
        self.ec2_client.associate_elastic_address_raw(request)

    def find_route_table_by_subnet(self, _, subnet):
        """
        Find route table attached to subnet.

        @param subnet:
        @param _: was region before
        @return:
        """

        main_route_tables = []
        logger.info(f"Looking for subnet route table {subnet.id=}, {subnet.region.region_mark=}")
        route_tables = [route_table for route_table in self.route_tables if route_table.region == subnet.region]

        if len(route_tables) == 0:
            route_tables = self.ec2_client.get_region_route_tables(subnet.region)

        for route_table in route_tables:
            if route_table.vpc_id != subnet.vpc_id:
                continue
            if route_table.check_subnet_associated(subnet.id):
                return route_table
            for association in route_table.associations:
                if association["Main"]:
                    main_route_tables.append(route_table)

        if len(main_route_tables) != 1:
            raise RuntimeError(f"{len(main_route_tables)} != 1")

        return main_route_tables[0]

    def find_subnet_public_addresses(self, subnet: Subnet):
        """
        Find 0.0.0.0 route and its public IP.

        @return:
        """
        if not self.route_tables:
            self.init_route_tables(region=subnet.region)

        route_table = self.find_route_table_by_subnet(subnet.region, subnet)
        for route in route_table.routes:
            if route["State"] != "active":
                continue
            if route["DestinationCidrBlock"] != "0.0.0.0/0":
                continue

            nat_gateway_id = route.get("NatGatewayId")
            if nat_gateway_id is not None:
                custom_filters = [
                    {"Name": "nat-gateway-id", "Values": [nat_gateway_id]}
                ]
                nat_gateways = self.ec2_client.get_region_nat_gateways(
                    region=subnet.region, custom_filters=custom_filters
                )
                if len(nat_gateways) != 1:
                    raise RuntimeError(f"len(nat_gateways) = {len(nat_gateways)}")
                nat_gateway = nat_gateways[0]
                if nat_gateway.connectivity_type != "public":
                    raise NotImplementedError(nat_gateway.dict_src)

                return nat_gateway.get_public_ip_addresses()

            gateway_id = route.get("GatewayId")
            if gateway_id is not None:
                return []

        raise RuntimeError(
            f"Could not find public address for subnet {subnet.id} in region {subnet.region.region_mark}"
        )

    def find_subnet_default_route_nat_gateway(self, subnet):
        """
        Find subnets 0.0.0.0/0 route nat gateway is there is such.

        @param subnet:
        @return:
        """

        route_table = self.find_route_table_by_subnet(subnet.region, subnet)
        for route in route_table.routes:
            if route["State"] != "active":
                continue

            if route.get("DestinationCidrBlock") is None:
                if route.get("DestinationIpv6CidrBlock") is None:
                    raise RuntimeError(f"Can't analyze route: {route}")
                continue

            if route.get("DestinationCidrBlock") != "0.0.0.0/0":
                continue

            nat_gateway_id = route.get("NatGatewayId")
            if nat_gateway_id is not None:
                custom_filters = [
                    {"Name": "nat-gateway-id", "Values": [nat_gateway_id]}
                ]
                nat_gateways = self.ec2_client.get_region_nat_gateways(
                    region=subnet.region, custom_filters=custom_filters
                )
                if len(nat_gateways) != 1:
                    raise RuntimeError(f"len(nat_gateways) = {len(nat_gateways)}")
                nat_gateway = nat_gateways[0]
                if nat_gateway.connectivity_type != "public":
                    raise NotImplementedError(nat_gateway.dict_src)

                return nat_gateway
        return None

    def get_ecr_authorization_info(self, region=None):
        """
        Info needed to register to ECR service.

        @param region:
        @return:
        """

        return self.ecr_client.get_authorization_info(region=region)

    def provision_ecs_task_definition(self, task_definition):
        """
        Self explanatory.

        @param task_definition:
        @return:
        """

        self.ecs_client.provision_ecs_task_definition(task_definition)

    # region acm certificate
    def provision_acm_certificate(self, certificate, master_hosted_zone_name):
        """
        Self explanatory

        @param certificate:
        @param master_hosted_zone_name:
        @return:
        """

        self.acm_client.provision_certificate(certificate)

        certificate.print_dict_src()

        if certificate.status == "ISSUED":
            return

        if (
                certificate.status is not None
                and certificate.status != "PENDING_VALIDATION"
        ):
            raise ValueError(certificate.status)

        self.validate_certificate(certificate, master_hosted_zone_name)

        new_certificate = self.wait_for_certificate_validation(certificate)
        certificate.update_from_raw_response(new_certificate.dict_src)

    def provision_sns_topic(self, topic):
        """
        Self explanatory

        @param topic:
        @return:
        """

        self.sns_client.provision_topic(topic)

    def provision_sns_subscription(self, subscription):
        """
        Self explanatory

        @param subscription:
        @return:
        """

        self.sns_client.provision_subscription(subscription)

    def validate_certificate(self, certificate, master_hosted_zone_name):
        """
        Validate https certificate with DNS record in Route53

        @param certificate:
        @param master_hosted_zone_name:
        @return:
        """
        max_time = 5 * 60
        sleep_time = 10
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(seconds=max_time)
        while datetime.datetime.now() < end_time:
            certificate = self.acm_client.get_certificate(certificate.arn)
            # pylint: disable= unsubscriptable-object
            if (
                    certificate.domain_validation_options[0].get("ResourceRecord")
                    is not None
            ):
                break

            logger.info(
                f"Waiting for certificate validation request. Going to sleep for {sleep_time} seconds: {certificate.arn}"
            )
            time.sleep(sleep_time)

        if len(certificate.domain_validation_options) != 1:
            raise NotImplementedError(certificate.domain_validation_options)

        hosted_zones = self.route53_client.get_all_hosted_zones(
            name=master_hosted_zone_name
        )

        if len(hosted_zones) == 0:
            raise ValueError(f"Can not find hosted zone: '{master_hosted_zone_name}'")
        if len(hosted_zones) > 1:
            raise ValueError(
                f"More then one hosted_zones with name '{master_hosted_zone_name}'"
            )
        hosted_zone = hosted_zones[0]

        dict_record = {
            "Name": certificate.domain_validation_options[0]["ResourceRecord"]["Name"],
            "Type": certificate.domain_validation_options[0]["ResourceRecord"]["Type"],
            "TTL": 300,
            "ResourceRecords": [
                {
                    "Value": certificate.domain_validation_options[0]["ResourceRecord"][
                        "Value"
                    ]
                }
            ],
        }

        record = HostedZone.Record(dict_record)
        hosted_zone.records = [record]

        self.provision_hosted_zone(hosted_zone)

    def wait_for_certificate_validation(self, certificate):
        """
        Certificate validation takes time.

        @param certificate:
        @return:
        """

        max_time = 5 * 60
        sleep_time = 30
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(seconds=max_time)
        while datetime.datetime.now() < end_time:
            certificate = self.acm_client.get_certificate(certificate.arn)
            if certificate.status == "ISSUED":
                logger.info(
                    f"Finished issuing in {datetime.datetime.now() - start_time}"
                )
                return certificate

            if certificate.status == "PENDING_VALIDATION":
                logger.info(
                    f"Waiting for certificate validation going to sleep for {sleep_time} seconds: {certificate.arn}"
                )
                time.sleep(sleep_time)
            else:
                raise ValueError(certificate.status)
        raise TimeoutError(
            f"Finished waiting {max_time} seconds for certificate validation. Finished with status: {certificate.status}"
        )

    # endregion

    # region sesv2_domain_email_identity
    def provision_sesv2_domain_email_identity(
            self, email_identity, wait_for_validation=True
    ):
        """
        Self explanatory

        @param email_identity:
        @param wait_for_validation:
        @return:
        """

        self.sesv2_client.provision_email_identity(email_identity)

        if email_identity.dkim_attributes["Status"] == "SUCCESS":
            return

        max_time = 5 * 60
        sleep_time = 10
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(seconds=max_time)
        while datetime.datetime.now() < end_time:
            logger.info(
                f"Waiting for sesv2 domain validation request. Going to sleep for {sleep_time} seconds: {email_identity.name}"
            )
            time.sleep(sleep_time)
            self.sesv2_client.update_email_identity_information(email_identity)

            if email_identity.dkim_attributes["Status"] != "NOT_STARTED":
                break
        else:
            raise TimeoutError(f"Reached timeout for {email_identity.name}")

        if email_identity.dkim_attributes["Status"] != "PENDING":
            raise ValueError(
                f"Unknown status {email_identity.dkim_attributes['Status']}"
            )

        self.validate_sesv2_domain_email_identity(email_identity)

        if wait_for_validation:
            self.wait_for_sesv2_domain_email_identity_validation(email_identity)

    def validate_sesv2_domain_email_identity(self, email_identity):
        """
        Validate SESv3 domain email identity.

        @param email_identity:
        @return:
        """

        hosted_zones = self.route53_client.get_all_hosted_zones(
            name=email_identity.name
        )

        if len(hosted_zones) == 0:
            raise ValueError(f"Can not find hosted zone: '{email_identity.name}'")

        if len(hosted_zones) > 1:
            raise ValueError(
                f"More then one hosted_zones with name '{email_identity.name}'"
            )

        hosted_zone = hosted_zones[0]

        for token in email_identity.dkim_attributes["Tokens"]:
            dict_record = {
                "Name": f"{token}._domainkey.{email_identity.name}",
                "Type": "CNAME",
                "TTL": 1800,
                "ResourceRecords": [{"Value": f"{token}.dkim.amazonses.com"}],
            }
            record = HostedZone.Record(dict_record)
            hosted_zone.records.append(record)

        self.provision_hosted_zone(hosted_zone)

    def wait_for_sesv2_domain_email_identity_validation(self, email_identity):
        """
        Wait for DNS records to catch after provisioning SESv2 email_identity

        @param email_identity:
        @return:
        """

        max_time = 5 * 60
        sleep_time = 30
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(seconds=max_time)
        while datetime.datetime.now() < end_time:
            self.sesv2_client.update_email_identity_information(email_identity)
            if email_identity.dkim_attributes["Status"] == "SUCCESS":
                logger.info(
                    f"Finished validating in {datetime.datetime.now() - start_time}"
                )
                break

            if email_identity.dkim_attributes["Status"] == "PENDING":
                logger.info(
                    f"Waiting for sesv2_domain_email_identity validation going to sleep for {sleep_time} seconds: {email_identity.name}"
                )
                time.sleep(sleep_time)
            else:
                raise ValueError(email_identity.dkim_attributes["Status"])
        else:
            raise TimeoutError(
                f"Finished waiting {max_time} seconds for sesv2_domain_email_identity validation. Finished with status: {email_identity.dkim_attributes['Status']}"
            )

    # endregion

    def provision_sesv2_email_template(self, email_template):
        """
        Provision SESv2 email template

        @param email_template:
        @return:
        """

        self.sesv2_client.provision_email_template(email_template)

    def provision_sesv2_configuration_set(self, configuration_set):
        """
        Provision SESv2 configuration_set

        @param configuration_set:
        @return:
        """

        self.sesv2_client.provision_configuration_set(configuration_set)

    def provision_rds_db_cluster(self, cluster, snapshot=None):
        """
        Self explanatory.

        @param cluster:
        @param snapshot:
        @return:
        """

        snapshot_id = snapshot.id if snapshot is not None else None
        self.rds_client.provision_db_cluster(cluster, snapshot_id=snapshot_id)

    def get_security_group_by_vpc_and_name(self, vpc, name):
        """
        Find security group in a vpc by its name.

        @param vpc:
        @param name:
        @return:
        """

        filters = {"Filters": [
            {"Name": "vpc-id", "Values": [vpc.id]},
            {"Name": "group-name", "Values": [name]},
        ]}
        security_groups = self.ec2_client.get_region_security_groups(
            vpc.region, filters=filters
        )
        if len(security_groups) != 1:
            raise RuntimeError(f"Can not find security group {name} in vpc {vpc.id}")

        return security_groups[0]

    def get_subnet_by_vpc_and_name(self, vpc, name):
        """
        Find subnet in a vpc by its name tag.

        @param vpc:
        @param name:
        @return:
        """

        filters_req = {"Filters": [
            {"Name": "vpc-id", "Values": [vpc.id]},
            {"Name": "tag:Name", "Values": [name]},
        ]}

        subnets = self.ec2_client.get_region_subnets(vpc.region, filters_req=filters_req)
        if len(subnets) != 1:
            raise RuntimeError(f"Can not find subnet '{name}' in vpc {vpc.id}")

        return subnets[0]

    def provision_db_cluster_parameter_group(self, db_cluster_parameter_group):
        """
        Self explanatory.

        @param db_cluster_parameter_group:
        @return:
        """

        self.rds_client.provision_db_cluster_parameter_group(db_cluster_parameter_group)

    def provision_db_parameter_group(self, db_parameter_group):
        """
        Self explanatory.

        @param db_parameter_group:
        @return:
        """

        self.rds_client.provision_db_parameter_group(db_parameter_group)

    def provision_db_subnet_group(self, db_subnet_group):
        """
        Self explanatory.

        @param db_subnet_group:
        @return:
        """

        self.rds_client.provision_db_subnet_group(db_subnet_group)

    def provision_db_instance(self, db_instance):
        """
        Self explanatory.

        @param db_instance:
        @return:
        """

        self.rds_client.provision_db_instance(db_instance)

    def provision_elasticache_cahce_subnet_group(self, subnet_group):
        """
        Self explanatory.

        @param subnet_group:
        @return:
        """

        self.elasticache_client.provision_subnet_group(subnet_group)

    def provision_elaticache_cluster(self, cluster):
        """
        Self explanatory.

        @param cluster:
        @return:
        """

        self.elasticache_client.provision_cluster(cluster)

    def provision_elaticache_replication_group(self, replication_group):
        """
        Self explanatory.

        @param replication_group:
        @return:
        """

        self.elasticache_client.provision_replication_group(replication_group)

    def provision_s3_bucket(self, s3_bucket):
        """
        Self explanatory.

        @param s3_bucket:
        @return:
        """

        self.s3_client.provision_bucket(s3_bucket)

    def provision_cloudfront_distribution(self, cloudfront_distribution):
        """
        Self explanatory.

        @param cloudfront_distribution:
        @return:
        """

        self.cloudfront_client.provision_distribution(cloudfront_distribution)

    def provision_cloudfront_origin_access_identity(
            self, cloudfront_origin_access_identity
    ):
        """
        Self explanatory.

        @param cloudfront_origin_access_identity:
        @return:
        """

        self.cloudfront_client.provision_origin_access_identity(
            cloudfront_origin_access_identity
        )

    def find_cloudfront_distribution(self, alias=None):
        """
        Find cloudfront distribution by alias.

        @param alias:
        @return:
        """

        if alias is None:
            raise RuntimeError("Alias is None")

        if not self.cloudfront_distributions:
            self.init_cloudfront_distributions()

        for distribution in self.cloudfront_distributions:
            if alias in distribution.aliases["Items"]:
                return distribution

        return None

    def find_cloudfront_distributions(self, alias=None, tags=None):
        """
        Find cloudfront distributions.

        @param alias:
        @return:
        """

        if not self.cloudfront_distributions:
            self.init_cloudfront_distributions()

        if alias is not None:
            for distribution in self.cloudfront_distributions:
                if alias in distribution.aliases["Items"]:
                    return [distribution]
            return []

        ret = []
        if tags is not None:
            for distribution in self.cloudfront_distributions:
                if not distribution.tags:
                    continue
                for tag in tags:
                    for distribution_tag in distribution.tags:
                        if tag["Key"] == distribution_tag["Key"] and tag["Value"] == distribution_tag["Value"]:
                            break
                    else:
                        break
                else:
                    ret.append(distribution)

            return ret

        raise RuntimeError("Search parameters were not set")

    def wait_for_instances_provision_ending(self, instances):
        """
        After a new EC2 instance provisioned it takes some time for it to become available.

        @param instances:
        @return:
        """

        instance_ids = [instance.id for instance in instances]
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(minutes=15)
        time_to_sleep = 20

        while datetime.datetime.now() < end_time:
            region_ec2_instances = self.ec2_client.get_region_ec2_instances(
                instances[0].region
            )
            for region_ec2_instance in region_ec2_instances:
                if region_ec2_instance.id not in instance_ids:
                    continue
                if region_ec2_instance.get_state() == region_ec2_instance.State.RUNNING:
                    instance_ids.remove(region_ec2_instance.id)

            if len(instance_ids) == 0:
                break
            logger.info(
                f"Waiting for instances to be ready. Going to sleep for {time_to_sleep} seconds"
            )
            time.sleep(time_to_sleep)
        else:
            raise TimeoutError()

    def provision_ecr_repository(self, ecr_repo):
        """
        Self explanatory.

        @param ecr_repo:
        @return:
        """

        self.ecr_client.provision_repository(ecr_repo)

    def dispose_ecr_repository(self, ecr_repo):
        """
        Self explanatory.

        @param ecr_repo:
        @return:
        """

        self.ecr_client.dispose_repository(ecr_repo)

    def dispose_ecs_service(self, cluster, service):
        """
        Self explanatory.

        @param service:
        @param cluster:
        @return:
        """

        self.ecs_client.dispose_service(cluster, service)

    def dispose_ecs_cluster(self, cluster):
        """
        Self explanatory.

        @param cluster:
        @return:
        """

        self.ecs_client.dispose_cluster(cluster)

    def dispose_auto_scaling_group(self, auto_scaling_group):
        """
        Self explanatory.

        @param auto_scaling_group:
        @return:
        """

        self.autoscaling_client.dispose_auto_scaling_group(auto_scaling_group)

    def dispose_launch_template(self, launch_template):
        """
        Delete the EC2 launch template.

        @param launch_template:
        @return:
        """

        self.ec2_client.dispose_launch_template(launch_template)

    def attach_capacity_providers_to_ecs_cluster(
            self, ecs_cluster, capacity_provider_names, default_capacity_provider_strategy
    ):
        """
        Attach Capacity provider to ECS cluster.

        @param ecs_cluster:
        @param capacity_provider_names:
        @param default_capacity_provider_strategy:
        @return:
        """

        self.ecs_client.attach_capacity_providers_to_ecs_cluster(
            ecs_cluster, capacity_provider_names, default_capacity_provider_strategy
        )

    def provision_aws_lambda_from_filelist(self, aws_lambda, files_paths, force=None, update_code=False):
        """
        Provision AWS Lambda object with the listed files added to it.

        @param aws_lambda:
        @param files_paths:
        @param force: Deprecated.
        @param update_code:
        @return:
        """

        if force is not None:
            logger.warning("Deprecation: 'force' is going to be deprecated use update_code instead")
            update_code = force

        zip_file_name = f"{aws_lambda.name}.zip"
        with zipfile.ZipFile(zip_file_name, "w") as myzip:
            for file_path in files_paths:
                # zip_file_name = os.path.splitext(os.path.basename(file_path))[0] + ".zip"
                myzip.write(file_path, arcname=os.path.basename(file_path))
        with open(zip_file_name, "rb") as myzip:
            aws_lambda.code = {"ZipFile": myzip.read()}

        self.provision_aws_lambda(aws_lambda, update_code=update_code)

    def provision_aws_lambda(self, aws_lambda, force=None, update_code=False):
        """
        Provision aws lambda object.

        @param aws_lambda:
        @param force: Deprecated.
        @param update_code: If true, the code deployment is forced and the active version set to the new one.
        @return:
        """

        if force is not None:
            logger.warning("Deprecation: 'force' is going to be deprecated use update_code instead")
            update_code = force

        self.lambda_client.provision_lambda(aws_lambda, update_code=update_code)

    def provision_lambda_event_source_mapping(self, event_mapping):
        """
        Event source mapping - event source, which trigger Lambda.

        @param event_mapping:
        @return:
        """

        self.lambda_client.provision_event_source_mapping(event_mapping)

    def provision_iam_role(self, iam_role):
        """
        Provision IAM Role object.

        @param iam_role:
        @return:
        """

        self.iam_client.provision_role(iam_role)

    def provision_iam_policy(self, iam_policy):
        """
        Provision IAM policy object.

        @param iam_policy:
        @return:
        """

        self.iam_client.provision_policy(iam_policy)

    def provision_iam_instance_profile(self, instance_profile):
        """
        Provision EC2 instance profile

        @param instance_profile:
        @return:
        """

        self.iam_client.provision_instance_profile(instance_profile)

    def dispose_rds_db_cluster(self, rds_cluster):
        """
        Delete the cluster.

        @param rds_cluster:
        @return:
        """

        self.rds_client.dispose_db_cluster(rds_cluster)

    def get_latest_db_cluster_snapshot(self, db_cluster):
        """
        Get the last RDS db cluster snapshot.

        @param db_cluster:
        @return:
        """

        filters_req = {"DBClusterIdentifier": db_cluster.id}
        src_region_cluster_snapshots = self.rds_client.get_region_db_cluster_snapshots(
            db_cluster.region, full_information=False, custom_filters=filters_req
        )

        return src_region_cluster_snapshots[-1]

    def copy_latest_db_cluster_snapshot(
            self, db_cluster, desired_snapshot: RDSDBClusterSnapshot
    ):
        """
        Copy latest cluster snapshot according to the desired_snapshot params.

        @param db_cluster:
        @param desired_snapshot:
        @return:
        """

        src_snapshot = self.get_latest_db_cluster_snapshot(db_cluster)
        src_snapshot.region = db_cluster.region

        if desired_snapshot.kms_key_id is None:
            if db_cluster.kms_key_id is None:
                self.rds_client.update_db_cluster_information(db_cluster)
            src_region_keys = self.kms_client.get_region_keys(
                db_cluster.region, full_information=True
            )
            src_region_key = CommonUtils.find_objects_by_values(
                src_region_keys, {"arn": db_cluster.kms_key_id}, max_count=1
            )[0]

            desired_snapshot.kms_key_id = src_region_key.aliases[0]["AliasName"]

        if desired_snapshot.id is None:
            dst_id = src_snapshot.id
            dst_id = dst_id.replace(":", "-")

            dst_id += f"-from-{db_cluster.region.region_mark}"
            while "--" in dst_id:
                dst_id = dst_id.replace("--", "-")
            desired_snapshot.id = dst_id

            desired_snapshot.tags.append({"Key": "Name", "Value": dst_id})

        self.rds_client.copy_db_cluster_snapshot(
            src_snapshot, desired_snapshot, synchronous=True
        )

    def provision_events_rule(self, events_rule):
        """
        Provision events rule

        @param events_rule:
        @return:
        """
        self.events_client.provision_rule(events_rule)

    def get_vpcs_by_tags(self, key_values_map, region=None):
        """
        Find all VPCs by tag keys:values

        @param key_values_map:
        @param region:
        @return:
        """

        filters = [
            {"Name": f"tag:{tag_name}", "Values": tag_values}
            for tag_name, tag_values in key_values_map.items()
        ]

        return self.ec2_client.get_all_vpcs(region=region, filters=filters)

    def get_alive_ec2_instance_by_name(self, region, name):
        """
        Get instance by tag "name". Raise Exception if more then one

        :param region:
        :param name:
        :return:
        """
        instances = self.get_ec2_instances_by_name(region, name)

        if len(instances) != 1:
            raise RuntimeError(
                f"Found {len(instances)} RUNNING/PENDING instances in region {region.region_mark} with tag_name '{name}' while expected 1"
            )

        return instances[0]

    def get_ec2_instances_by_name(self, region, name, alive=True, include_terminated=True):
        """
        Find running ec2 instances by "name" tag

        @param region:
        @param name:
        @param alive:
        @param include_terminated:
        @return:
        """

        return self.get_ec2_instances_by_tags(region, {"Name": [name]}, alive=alive, include_terminated=include_terminated)

    def get_ec2_instances_by_tags(self, region, tags_values_by_name, alive=True, include_terminated=True):
        """
        Find running ec2 instances by "name" tag

        @param region:
        @param tags_values_by_name: dict {name: [value1, value2]}
        @param alive:
        @param include_terminated:
        @return:
        """

        filters = {"Filters": [{"Name": f"tag:{name}", "Values": values} for name, values in tags_values_by_name.items()]}
        ec2_instances = self.ec2_client.get_region_instances(region, filters=filters)

        if not include_terminated:
            ec2_instances = [ec2_instance for ec2_instance in ec2_instances if ec2_instance.get_state() !=
                ec2_instance.State.TERMINATED
            ]

        if not alive:
            return ec2_instances

        ret_instances = []
        for ec2_instance in ec2_instances:
            if ec2_instance.get_state() not in [
                ec2_instance.State.PENDING,
                ec2_instance.State.RUNNING,
                ec2_instance.State.STOPPING,
                ec2_instance.State.STOPPED,
            ]:
                continue

            ret_instances.append(ec2_instance)

        return ret_instances


    def provision_servicediscovery_namespace(self, namespace):
        """
        Provision Service discovery namespace

        @param namespace:
        @return:
        """
        self.servicediscovery_client.provision_namespace(namespace)

    def provision_servicediscovery_service(self, service):
        """
        Provision Service discovery service

        @param service:
        @return:
        """
        self.servicediscovery_client.provision_service(service)

    def provision_sqs_queue(self, sqs_queue, declarative=True):
        """
        Provision SQS queue

        @param sqs_queue:
        @return:
        """

        self.sqs_client.provision_queue(sqs_queue, declarative=declarative)

    def create_image(self, instance: EC2Instance, timeout=600):
        """
        Create EC2 instance ami.

        @param timeout:
        @param instance:
        @return:
        """
        return self.ec2_client.create_image(instance, timeout=timeout)

    def generate_security_reports(self, report_file_path):
        """
        Generate all erports
        @return:
        """
        h_tb = TextBlock("IAM security report")
        self.init_iam_policies(
            from_cache=True,
            cache_file=self.configuration.aws_api_iam_policies_cache_file,
        )
        # self.init_iam_roles()
        self.init_iam_users(
            from_cache=True, cache_file=self.configuration.aws_api_iam_users_cache_file
        )
        self.init_iam_groups(
            from_cache=True, cache_file=self.configuration.aws_api_iam_groups_cache_file
        )

        h_tb_users = self.generate_security_report_users()
        h_tb.blocks.append(h_tb_users)

        h_tb_policies = self.generate_security_report_policies()
        h_tb.blocks.append(h_tb_policies)

        h_tb_groups = self.generate_security_report_groups()
        h_tb.blocks.append(h_tb_groups)

        with open(report_file_path, "w", encoding="utf-8") as file_handler:
            file_handler.write(h_tb.format_pprint(multiline=True))

        logger.info(f"Generated security report at: {report_file_path}")
        return h_tb

    def generate_security_report_users(self):
        """
        Generate all users report.

        @return:
        """

        h_tb = TextBlock("AWS IAM Users:")
        for user in self.users:
            h_tb_user = TextBlock(f"UserName: '{user.name}'")
            h_tb_user.lines.append("#" * 20)

            if user.policies:
                policies_block = json.dumps(
                    [pol["Statement"] for pol in user.policies], indent=2
                )
                h_tb_user.lines.append(f"Inline Policies: {policies_block}")
            if user.attached_policies:
                h_tb_user.lines.append(
                    f"Attached Policies: {[pol['PolicyName'] for pol in user.attached_policies]}"
                )
            if user.groups:
                h_tb_user.lines.append(
                    f"Groups: {[group['GroupName'] for group in user.groups]}"
                )
            h_tb.blocks.append(h_tb_user)

        return h_tb

    def generate_security_report_policies(self):
        """
        Generate all users report.

        @return:
        """

        used_policies = []
        h_tb = TextBlock("AWS IAM Policies used by Users:")
        for user in self.users:
            if not user.attached_policies:
                continue
            used_policies += [
                pol["PolicyName"]
                for pol in user.attached_policies
                if pol["PolicyArn"].split(":")[4] != "aws"
            ]

        used_policies = list(set(used_policies))
        for policy_name in used_policies:
            policy = CommonUtils.find_objects_by_values(
                self.iam_policies, {"name": policy_name}, max_count=1
            )[0]
            h_tb_pol = TextBlock(f"PolicyName: '{policy.name}'")
            h_tb_pol.lines.append("#" * 20)

            policies_block = json.dumps(policy.document.dict_src["Statement"], indent=2)
            h_tb_pol.lines.append(policies_block)
            h_tb.blocks.append(h_tb_pol)

        return h_tb

    def generate_security_report_groups(self):
        """
        Generate all users groups report.

        @return:
        """

        used_grps = []
        h_tb = TextBlock("AWS IAM groups used by Users:")
        for user in self.users:
            if not user.groups:
                continue
            used_grps += [grp["GroupName"] for grp in user.groups]

        used_grps = list(set(used_grps))
        used_policies = []
        for group_name in used_grps:
            group = CommonUtils.find_objects_by_values(
                self.iam_groups, {"name": group_name}, max_count=1
            )[0]
            h_tb_grp = TextBlock(f"GroupName: '{group.name}'")
            h_tb_grp.lines.append("#" * 20)

            if group.policies:
                policies_block = json.dumps(list(group.policies), indent=2)
                h_tb_grp.lines.append(f"Inline Policies: {policies_block}")

            if group.attached_policies:
                attached_policies = [
                    pol["PolicyName"] for pol in group.attached_policies
                ]
                h_tb_grp.lines.append(f"Attached Policies: {attached_policies}")
                used_policies += attached_policies
            h_tb.blocks.append(h_tb_grp)

        used_policies = list(set(used_policies))
        h_tb_policies = TextBlock("Attached Policies used by Groups")
        for policy_name in used_policies:
            h_tb_pol = TextBlock(f"PolicyName: {policy_name}")
            policy = CommonUtils.find_objects_by_values(
                self.iam_policies, {"name": policy_name}, max_count=1
            )[0]
            policies_block = json.dumps(policy.document.dict_src["Statement"], indent=2)
            h_tb_pol.lines.append(policies_block)

            h_tb_pol.lines.append("#" * 20)
            h_tb_policies.blocks.append(h_tb_pol)

        h_tb.blocks.append(h_tb_policies)

        return h_tb

    def renew_ecs_cluster_container_instances(self, ecs_cluster):
        """
        Replace old instances with new.

        :param ecs_cluster:
        :return:
        """

        self.ecs_client.update_cluster_information(ecs_cluster)
        if not ecs_cluster.capacity_providers:
            return

        cap_prov = ECSCapacityProvider({})
        cap_prov.region = ecs_cluster.region
        cap_prov.name = ecs_cluster.capacity_providers[0]
        self.ecs_client.update_capacity_provider_information(cap_prov)

        auto_scaling_group = AutoScalingGroup({})
        auto_scaling_group.region = ecs_cluster.region
        auto_scaling_group.arn = cap_prov.auto_scaling_group_provider["autoScalingGroupArn"]
        self.autoscaling_client.update_auto_scaling_group_information(auto_scaling_group)

        current_container_instances = self.ecs_client.get_region_container_instances(ecs_cluster.region,
                                                                                     cluster_identifier=ecs_cluster.arn)

        # increase ASG capacity
        auto_scaling_group.desired_capacity *= 2
        if auto_scaling_group.max_size < auto_scaling_group.desired_capacity:
            initial_max_size = auto_scaling_group.max_size
            auto_scaling_group.max_size = auto_scaling_group.desired_capacity
        else:
            initial_max_size = None

        self.autoscaling_client.provision_auto_scaling_group(auto_scaling_group)

        # drain current_instances
        for current_container_instance in current_container_instances:
            current_container_instance.status = "DRAINING"
        self.ecs_client.update_container_instances_state(current_container_instances)

        # detach ec2 instance from ASG
        current_ec2_instance_ids = [container_instance.ec2_instance_id for container_instance in
                                    current_container_instances]
        self.autoscaling_client.detach_instances(auto_scaling_group, current_ec2_instance_ids, decrement=True)

        # revert ASG capacity change
        if initial_max_size is not None:
            auto_scaling_group.max_size = initial_max_size
            self.autoscaling_client.provision_auto_scaling_group(auto_scaling_group)

        # terminate old instances
        for container_instance in current_container_instances:
            ec2_instance = EC2Instance({})
            ec2_instance.region = ecs_cluster.region
            ec2_instance.id = container_instance.ec2_instance_id
            self.ec2_client.dispose_instance(ec2_instance)

    def decode_authorization_message(self, exception):
        """
        Read internal message. Make sure you have relevant permissions.

        :param exception:
        :return:
        """

        str_exception = str(exception)
        message_prefix = "Encoded authorization failure message: "
        if message_prefix not in str_exception:
            raise ValueError(f'"{message_prefix}" was not found in exception') from exception
        str_message = str_exception[str_exception.find(message_prefix)+len(message_prefix):]
        return json.dumps(json.loads(self.sts_client.decode_authorization_message(str_message)), indent=2)

    def get_price_list(self, region, service_code):
        """
        Get pricing list.

        :param region:
        :param service_code:
        :return:
        """
        filters_req = {"ServiceCode": service_code,
                             "EffectiveDate": datetime.datetime.now(),
                             "RegionCode": region.region_mark,
                             "CurrencyCode": "USD"}
        price_lists = list(self.pricing_client.yield_price_lists(region=region, filters_req=filters_req))
        return price_lists[0]

"""
Module to handle cross service interaction
"""
import json
import os
import datetime
import time

from collections import defaultdict
from horey.network.ip import IP
import pdb
from horey.aws_api.aws_clients.ec2_client import EC2Client
from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
from horey.aws_api.aws_services_entities.network_interface import NetworkInterface
from horey.aws_api.aws_services_entities.ec2_security_group import EC2SecurityGroup
from horey.aws_api.aws_services_entities.ec2_spot_fleet_request import EC2SpotFleetRequest
from horey.aws_api.aws_services_entities.ec2_launch_template import EC2LaunchTemplate


from horey.aws_api.aws_clients.ecs_client import ECSClient
from horey.aws_api.aws_clients.s3_client import S3Client
from horey.aws_api.aws_services_entities.s3_bucket import S3Bucket

from horey.aws_api.aws_clients.elbv2_client import ELBV2Client
from horey.aws_api.aws_services_entities.elbv2_load_balancer import LoadBalancer
from horey.aws_api.aws_services_entities.elbv2_target_group import ELBV2TargetGroup

from horey.aws_api.aws_services_entities.managed_prefix_list import ManagedPrefixList

from horey.aws_api.aws_clients.elb_client import ELBClient
from horey.aws_api.aws_services_entities.elb_load_balancer import ClassicLoadBalancer

from horey.aws_api.aws_clients.lambda_client import LambdaClient
from horey.aws_api.aws_services_entities.aws_lambda import AWSLambda

from horey.aws_api.aws_clients.route53_client import Route53Client
from horey.aws_api.aws_services_entities.route53_hosted_zone import HostedZone

from horey.aws_api.aws_clients.rds_client import RDSClient
from horey.aws_api.aws_services_entities.rds_db_instance import DBInstance

from horey.aws_api.aws_clients.iam_client import IamClient
from horey.aws_api.aws_services_entities.iam_policy import IamPolicy
from horey.aws_api.aws_services_entities.iam_user import IamUser
from horey.aws_api.aws_services_entities.iam_role import IamRole

from horey.aws_api.aws_clients.cloud_watch_logs_client import CloudWatchLogsClient
from horey.aws_api.aws_services_entities.cloud_watch_log_group import CloudWatchLogGroup
from horey.aws_api.aws_services_entities.cloud_watch_log_group_metric_filter import CloudWatchLogGroupMetricFilter

from horey.aws_api.aws_services_entities.cloud_watch_metric import CloudWatchMetric
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm

from horey.aws_api.aws_clients.cloud_watch_client import CloudWatchClient

from horey.aws_api.aws_clients.cloudfront_client import CloudfrontClient
from horey.aws_api.aws_services_entities.cloudfront_distribution import CloudfrontDistribution

from horey.aws_api.aws_clients.event_bridge_client import EventBridgeClient
from horey.aws_api.aws_services_entities.event_bridge_rule import EventBridgeRule

from horey.aws_api.aws_clients.secrets_manager_client import SecretsManagerClient
from horey.aws_api.aws_services_entities.secrets_manager_secret import SecretsManagerSecret

from horey.aws_api.aws_clients.servicediscovery_client import ServicediscoveryClient
from horey.aws_api.aws_services_entities.servicediscovery_service import ServicediscoveryService

from horey.aws_api.aws_clients.elasticsearch_client import ElasticsearchClient
from horey.aws_api.aws_services_entities.elasticsearch_domain import ElasticsearchDomain

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

from horey.common_utils.common_utils import CommonUtils
from horey.network.dns import DNS

from horey.h_logger import get_logger
from horey.common_utils.text_block import TextBlock

from horey.network.dns_map import DNSMap
from horey.network.service import ServiceTCP, Service
from horey.aws_api.base_entities.aws_account import AWSAccount

logger = get_logger()


# pylint: disable=R0904
class AWSAPI:
    """
    AWS access management and some small functionality to coordinate different services.
    """
    def __init__(self, configuration=None):
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
        self.cloudfront_client = CloudfrontClient()
        self.event_bridge_client = EventBridgeClient()
        self.secretsmanager_client = SecretsManagerClient()
        self.servicediscovery_client = ServicediscoveryClient()
        self.elasticsearch_client = ElasticsearchClient()

        self.network_interfaces = []
        self.iam_policies = []
        self.ec2_instances = []
        self.spot_fleet_requests = []
        self.s3_buckets = []
        self.load_balancers = []
        self.classic_load_balancers = []
        self.hosted_zones = []
        self.users = []
        self.databases = []
        self.security_groups = []
        self.target_groups = []
        self.ec2_launch_templates = []
        self.lambdas = []
        self.iam_roles = []
        self.cloud_watch_log_groups = []
        self.cloud_watch_log_groups_metric_filters = []
        self.cloud_watch_alarms = []
        self.cloudfront_distributions = []
        self.event_bridge_rules = []
        self.secrets_manager_secrets = []
        self.servicediscovery_services = []
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

        self.configuration = configuration
        self.init_configuration()

    def init_configuration(self):
        """
        Sets current active account from configuration
        """
        if self.configuration is None:
            return
        accounts = CommonUtils.load_object_from_module(self.configuration.accounts_file, "main")
        AWSAccount.set_aws_account(accounts[self.configuration.aws_api_account])

    def init_managed_prefix_lists(self, from_cache=False, cache_file=None):
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ManagedPrefixList)
        else:
            objects = self.ec2_client.get_all_managed_prefix_lists()

        self.managed_prefix_lists += objects
    
    def init_vpcs(self, from_cache=False, cache_file=None):
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, VPC)
        else:
            objects = self.ec2_client.get_all_vpcs()

        self.vpcs += objects
        
    def init_subnets(self, from_cache=False, cache_file=None):
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, Subnet)
        else:
            objects = self.ec2_client.get_all_subnets()

        self.subnets += objects
    
    def init_availability_zones(self, from_cache=False, cache_file=None):
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, AvailabilityZone)
        else:
            objects = self.ec2_client.get_all_availability_zones()

        self.availability_zones += objects
    
    def init_nat_gateways(self, from_cache=False, cache_file=None):
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, NatGateway)
        else:
            objects = self.ec2_client.get_all_nat_gateways()

        self.nat_gateways += objects

    def init_amis(self, from_cache=False, cache_file=None):
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, AMI)
        else:
            objects = self.ec2_client.get_all_amis()

        self.amis += objects

    def init_key_pairs(self, from_cache=False, cache_file=None):
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, KeyPair)
        else:
            objects = self.ec2_client.get_all_key_pairs()

        self.key_pairs += objects

    def init_internet_gateways(self, from_cache=False, cache_file=None):
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, InternetGateway)
        else:
            objects = self.ec2_client.get_all_internet_gateways()

        self.internet_gateways += objects

    def init_vpc_peerings(self, from_cache=False, cache_file=None):
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, VPCPeering)
        else:
            objects = self.ec2_client.get_all_vpc_peerings()

        self.vpc_peerings += objects

    def init_route_tables(self, from_cache=False, cache_file=None):
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, RouteTable)
        else:
            objects = self.ec2_client.get_all_route_tables()

        self.route_tables += objects

    def init_elastic_addresses(self, from_cache=False, cache_file=None):
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ElasticAddress)
        else:
            objects = self.ec2_client.get_all_elastic_addresses()

        self.elastic_addresses += objects

    def init_network_interfaces(self, from_cache=False, cache_file=None):
        """
        Init ec2 instances.

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, NetworkInterface)
        else:
            objects = self.ec2_client.get_all_interfaces()

        self.network_interfaces += objects

        return self.network_interfaces

    def init_ec2_instances(self, from_cache=False, cache_file=None):
        """
        Init ec2 instances.

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, EC2Instance)
        else:
            objects = self.ec2_client.get_all_instances()

        self.ec2_instances += objects

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

        self.spot_fleet_requests += objects

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

        self.ec2_launch_templates += objects

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

    def init_users(self, from_cache=False, cache_file=None):
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
            objects = self.iam_client.get_all_roles(policies=self.iam_policies)

        self.iam_roles += objects

    def cache_raw_cloud_watch_metrics(self, cache_dir):
        """
        Cache the cloudwatch metrics.

        @param cache_dir:
        @return:
        """

        metrics_generator = self.cloud_watch_client.yield_cloud_watch_metrics()
        self.cache_objects_from_generator(metrics_generator, cache_dir)

    def init_cloud_watch_alarms(self, from_cache=False, cache_file=None):
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, CloudWatchAlarm)
        else:
            objects = self.cloud_watch_client.get_cloud_watch_alarms()

        self.cloud_watch_alarms = objects

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

    def init_cloud_watch_log_groups_metric_filters(self, from_cache=False, cache_file=None):
        """
        Init the cloudwatch log groups.

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, CloudWatchLogGroupMetricFilter)
        else:
            objects = self.cloud_watch_logs_client.get_cloud_watch_log_group_metric_filters()

        self.cloud_watch_log_groups_metric_filters = objects

    def init_and_cache_raw_large_cloud_watch_log_groups(self, cloudwatch_log_groups_streams_cache_dir, log_group_names=None):
        """
        Because cloudwatch groups can grow very large I use the same mechanism like in S3.

        @param cloudwatch_log_groups_streams_cache_dir:
        @return:
        """
        log_groups = self.cloud_watch_logs_client.get_cloud_watch_log_groups(full_information=False)
        for log_group in log_groups:
            if log_group_names is not None:
                if log_group.name not in log_group_names:
                    continue
            sub_dir = os.path.join(cloudwatch_log_groups_streams_cache_dir, log_group.generate_dir_name())
            os.makedirs(sub_dir, exist_ok=True)
            logger.info(f"Begin collecting from stream: {sub_dir}")

            stream_generator = self.cloud_watch_logs_client.yield_log_group_streams(log_group)
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

            for i in range(int(len_bucket_objects/max_count) + 1):
                first_key_index = max_count * i
                last_key_index = (min(max_count * (i+1), len_bucket_objects)) - 1
                file_name = bucket_objects[last_key_index].key.replace("/", "_")
                file_path = os.path.join(bucket_dir, file_name)

                data_to_dump = [obj.convert_to_dict() for obj in bucket_objects[first_key_index: last_key_index]]

                with open(file_path, "w") as fd:
                    json.dump(data_to_dump, fd)

            print(f"{bucket.name}: {len(bucket_objects)}")

    def init_and_cache_all_s3_bucket_objects(self, buckets_objects_cache_dir, bucket_name=None):
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
                logger.warning(f"bucket {bucket.name} has no return string: {received_exception} ")
                continue

    def init_lambdas(self, from_cache=False, cache_file=None, full_information=True):
        """
        Init AWS lambdas
        @param from_cache:
        @param cache_file:
        @param full_information:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, AWSLambda)
        else:
            objects = self.lambda_client.get_all_lambdas(full_information=full_information)

        self.lambdas += objects

    def init_load_balancers(self, from_cache=False, cache_file=None):
        """
        Init elbs v2

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, LoadBalancer)
        else:
            objects = self.elbv2_client.get_all_load_balancers()

        self.load_balancers += objects

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

        self.classic_load_balancers += objects

    def init_hosted_zones(self, from_cache=False, cache_file=None, full_information=True):
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
            objects = self.route53_client.get_all_hosted_zones(full_information=full_information)

        self.hosted_zones = objects

    def init_cloudfront_distributions(self, from_cache=False, cache_file=None, full_information=True):
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
            objects = self.cloudfront_client.get_all_distributions(full_information=full_information)

        self.cloudfront_distributions = objects

    def init_event_bridge_rules(self, from_cache=False, cache_file=None, full_information=True):
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
            objects = self.event_bridge_client.get_all_distributions(full_information=full_information)

        self.event_bridge_rules = objects

    def init_servicediscovery_services(self, from_cache=False, cache_file=None, full_information=True):
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
            objects = self.servicediscovery_client.get_all_services(full_information=full_information)

        self.servicediscovery_services = objects

    def init_elasticsearch_domains(self, from_cache=False, cache_file=None, full_information=True):
        """
        Init elasticsearch serivces
        @param from_cache:
        @param cache_file:
        @param full_information:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ElasticsearchDomain)
        else:
            objects = self.elasticsearch_client.get_all_domains(full_information=full_information)

        self.elasticsearch_domains = objects
        
    def init_secrets_manager_secrets(self, from_cache=False, cache_file=None, full_information=True):
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
            objects = self.secretsmanager_client.get_all_secrets(full_information=full_information)

        self.secrets_manager_secrets = objects

    def init_databases(self, from_cache=False, cache_file=None):
        """
        Init RDSs

        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, DBInstance)
        else:
            objects = self.rds_client.get_all_databases()

        self.databases = objects

    def init_target_groups(self, from_cache=False, cache_file=None):
        """
        Init ELB target groups
        @param from_cache:
        @param cache_file:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, ELBV2TargetGroup)
        else:
            objects = self.elbv2_client.get_all_target_groups()

        self.target_groups = objects

    def init_security_groups(self, from_cache=False, cache_file=None, full_information=False):
        """
        Init security groups

        @param from_cache:
        @param cache_file:
        @param full_information:
        @return:
        """
        if from_cache:
            objects = self.load_objects_from_cache(cache_file, EC2SecurityGroup)
        else:
            objects = self.ec2_client.get_all_security_groups(full_information=full_information)
        self.security_groups += objects

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

            with open(file_path, "w") as fd:
                json.dump(buffer, fd)

            counter = 0
            buffer = []

        logger.info(f"Dir {sub_dir} total count of objects: {total_counter}")

        if total_counter == 0:
            return

        file_path = os.path.join(sub_dir, str(total_counter))

        with open(file_path, "w") as fd:
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
        for bucket_object in bucket_objects_iterator:
            counter += 1
            total_counter += 1
            buffer.append(bucket_object)

            if counter < max_count:
                continue

            logger.info(f"Bucket objects total_counter: {total_counter}")
            logger.info(f"Writing chunk of {max_count} objects for bucket {bucket.name}")
            counter = 0
            file_name = bucket_object.key.replace("/", "_")
            file_path = os.path.join(bucket_dir, file_name)

            data_to_dump = [obj.convert_to_dict() for obj in buffer]

            buffer = []

            with open(file_path, "w") as fd:
                json.dump(data_to_dump, fd)

        logger.info(f"Bucket {bucket.name} total count of objects: {total_counter}")

        if total_counter == 0:
            return

        file_name = bucket_object.key.replace("/", "_")
        file_path = os.path.join(bucket_dir, file_name)

        data_to_dump = [obj.convert_to_dict() for obj in buffer]

        with open(file_path, "w") as fd:
            json.dump(data_to_dump, fd)

    def load_objects_from_cache(self, file_name, class_type):
        """
        Load objects from cached file

        @param file_name:
        @param class_type:
        @return:
        """
        with open(file_name) as fil:
            return [class_type(dict_src, from_cache=True) for dict_src in json.load(fil)]

    def cache_objects(self, objects, file_name):
        """
        Prepare a cache file from objects.

        @param objects:
        @param file_name:
        @return:
        """
        objects_dicts = [obj.convert_to_dict() for obj in objects]

        if not os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name))

        with open(file_name, "w") as fil:
            fil.write(json.dumps(objects_dicts))

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

        for obj in self.databases:
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

    def cleanup_report_network_interfaces(self, output_file):
        tb_ret = TextBlock("Unused network interfaces")
        for interface in self.network_interfaces:
            if interface.attachment is None:
                tb_ret.lines.append(f"Name: {interface.name}, Private dns name: {interface.private_dns_name}, "
                                    f"availability_zone: {interface.availability_zone}, subnet: {interface.subnet_id}")

            if interface.status not in ["available", "in-use"]:
                raise NotImplementedError(interface.status)

        tb_ret.header += f" ({len(tb_ret.lines)})"
        tb_ret.write_to_file(output_file)
        return tb_ret

    def cleanup_report_lambdas(self, report_file_path, aws_api_cloudwatch_log_groups_streams_cache_dir):
        """
        Generated various lambdas' cleanup reports.

        @param report_file_path:
        @param aws_api_cloudwatch_log_groups_streams_cache_dir:
        @return:
        """
        tb_ret = TextBlock("AWS Lambdas cleanup")
        tb_ret.blocks.append(self.cleanup_report_lambdas_not_running(aws_api_cloudwatch_log_groups_streams_cache_dir))
        tb_ret.blocks.append(self.cleanup_report_lambdas_large_size())
        tb_ret.blocks.append(self.cleanup_report_lambdas_security_group())
        tb_ret.blocks.append(self.cleanup_report_lambdas_old_code())

        with open(report_file_path, "w+") as file_handler:
            file_handler.write(str(tb_ret))

        return tb_ret

    def cleanup_report_lambdas_security_group(self):
        """
        Lambda uses external resources, while can not be accessed from the outside itself.
        No need to keep an open port for that. If there is - misconfiguration might have occurred.

        :return:
        """

        tb_ret = TextBlock("Lambdas' security groups report")
        tb_ret_open_ingress = TextBlock("Lambdas with open ingress security groups - no need to open a port into lambda")
        tb_ret_nonexistent_security_groups = TextBlock("Security groups being assigned to lambdas, but were deleted.")

        for aws_lambda in self.lambdas:
            lst_str_sgs = aws_lambda.get_assinged_security_group_ids()
            for security_group_id in lst_str_sgs:
                lst_security_group = CommonUtils.find_objects_by_values(self.security_groups, {"id": security_group_id}, max_count=1)
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

    def cleanup_report_lambdas_large_size(self):
        """
        Large lambdas - over 100MiB size code.
        :return:
        """
        tb_ret = TextBlock("Large lambdas: Maximum size is 250 MiB")
        limit = 100 * 1024 * 1024
        lst_names_sizes = []
        for aws_lambda in self.lambdas:
            if aws_lambda.code_size >= limit:
                lst_names_sizes.append([aws_lambda.name, aws_lambda.code_size])

        if len(lst_names_sizes) > 0:
            lst_names_sizes = sorted(lst_names_sizes, key=lambda x: x[1], reverse=True)
            tb_ret.lines = [f"Lambda '{name}' size:{CommonUtils.bytes_to_str(code_size)}" for name, code_size in lst_names_sizes]
        else:
            tb_ret.lines = [f"No lambdas found with size over {CommonUtils.bytes_to_str(limit)}"]
        return tb_ret

    def cleanup_report_lambdas_not_running(self, aws_api_cloudwatch_log_groups_streams_cache_dir):
        """
        Lambda report checking if lambdas write logs:
        * No log group
        * Log group is empty
        * To old streams

        @param aws_api_cloudwatch_log_groups_streams_cache_dir:
        @return:
        """
        tb_ret = TextBlock("Not functioning lambdas- either the last run was to much time ago or it never run")
        for aws_lambda in self.lambdas:
            log_groups = \
                CommonUtils.find_objects_by_values(self.cloud_watch_log_groups, {"name": f"/aws/lambda/{aws_lambda.name}"}, max_count=1)
            if len(log_groups) == 0:
                tb_ret.lines.append(f"{aws_lambda.name}- never run [Log group does not exist]")
                continue

            log_group = log_groups[0]
            if log_group.stored_bytes == 0:
                tb_ret.lines.append(f"{aws_lambda.name}- never run [No logs in log group]")
                continue

            if CommonUtils.timestamp_to_datetime(log_group.creation_time/1000) > datetime.datetime.now() - datetime.timedelta(days=31):
                continue

            lines = self.cleanup_report_lambdas_not_running_stream_analysis(log_group, aws_api_cloudwatch_log_groups_streams_cache_dir)
            tb_ret.lines += lines

        return tb_ret

    def cleanup_report_lambdas_not_running_stream_analysis(self, log_group, aws_api_cloudwatch_log_groups_streams_cache_dir):
        """
        Lambda report checking if the last log stream is to old
        @param log_group:
        @param aws_api_cloudwatch_log_groups_streams_cache_dir:
        @return:
        """
        lines = []
        file_names = os.listdir(os.path.join(aws_api_cloudwatch_log_groups_streams_cache_dir, log_group.generate_dir_name()))

        last_file = str(max([int(file_name) for file_name in file_names]))
        with open(os.path.join(aws_api_cloudwatch_log_groups_streams_cache_dir, log_group.generate_dir_name(), last_file)) as file_handler:
            last_stream = json.load(file_handler)[-1]
        if CommonUtils.timestamp_to_datetime(last_stream["lastIngestionTime"]/1000) < datetime.datetime.now() - datetime.timedelta(days=365):
            lines.append(f"Cloudwatch log group '{log_group.name}' last event was more then year ago: {CommonUtils.timestamp_to_datetime(last_stream['lastIngestionTime']/1000)}")
        elif CommonUtils.timestamp_to_datetime(last_stream["lastIngestionTime"]/1000) < datetime.datetime.now() - datetime.timedelta(days=62):
            lines.append(f"Cloudwatch log group '{log_group.name}' last event was more then 2 months ago: {CommonUtils.timestamp_to_datetime(last_stream['lastIngestionTime']/1000)}")
        return lines

    def cleanup_report_lambdas_old_code(self):
        """
        Find all lambdas, which code wasn't updated for a year or more.
        :return:
        """
        days_limit = 365
        tb_ret = TextBlock(f"Lambdas with code older than {days_limit} days")
        time_limit = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=days_limit)
        lst_names_dates = []
        for aws_lambda in self.lambdas:
            if aws_lambda.last_modified < time_limit:
                lst_names_dates.append([aws_lambda.name, aws_lambda.last_modified])

        lst_names_dates = sorted(lst_names_dates, key=lambda x: x[1])
        tb_ret.lines = [f"Lambda {name} was last update: {update_date.strftime('%Y-%m-%d %H:%M')}" for name, update_date in lst_names_dates]
        return tb_ret

    def cleanup_report_s3_buckets_objects(self, summarised_data_file, output_file):
        """
        Generating S3 cleanup report from the previously generated summarized data file.
        @param summarised_data_file:
        @param output_file:
        @return:
        """
        with open(summarised_data_file) as fh:
            all_buckets = json.load(fh)

        by_bucket_sorted_data = dict()

        for bucket_name, bucket_data in all_buckets.items():
            by_bucket_sorted_data[bucket_name] = {"total_size": 0, "total_keys": 0, "years": {}}
            logger.info(f"Init bucket '{bucket_name}'")

            for year, year_data in sorted(bucket_data.items(), key=lambda x: x[0]):
                year_dict = {"total_size": 0, "total_keys": 0, "months": {}}
                by_bucket_sorted_data[bucket_name]["years"][year] = year_dict

                for month, month_data in sorted(year_data.items(), key=lambda x: int(x[0])):
                    year_dict["months"][month] = {"total_size": 0, "total_keys": 0}
                    for day, day_data in month_data.items():
                        year_dict["months"][month]["total_size"] += day_data["size"]
                        year_dict["months"][month]["total_keys"] += day_data["keys"]
                    year_dict["total_size"] += year_dict["months"][month]["total_size"]
                    year_dict["total_keys"] += year_dict["months"][month]["total_keys"]

                by_bucket_sorted_data[bucket_name]["total_size"] += year_dict["total_size"]
                by_bucket_sorted_data[bucket_name]["total_keys"] += year_dict["total_keys"]

        tb_ret = TextBlock("Buckets sizes report per years")
        for bucket_name, bucket_data in sorted(by_bucket_sorted_data.items(), reverse=True, key=lambda x: x[1]["total_size"]):
            tb_bucket = TextBlock(f"Bucket_Name: '{bucket_name}' size: {CommonUtils.bytes_to_str(bucket_data['total_size'])}, keys: {CommonUtils.int_to_str(bucket_data['total_keys'])}")

            for year, year_data in bucket_data["years"].items():
                tb_year = TextBlock(
                        f"{year} size: {CommonUtils.bytes_to_str(year_data['total_size'])}, keys: {CommonUtils.int_to_str(year_data['total_keys'])}")

                for month, month_data in year_data["months"].items():
                    line = f"Month: {month}, Size: {CommonUtils.bytes_to_str(month_data['total_size'])}, keys: {CommonUtils.int_to_str(month_data['total_keys'])}"
                    tb_year.lines.append(line)

                tb_bucket.blocks.append(tb_year)

            tb_ret.blocks.append(tb_bucket)

        with open(output_file, "w") as fh:
            fh.write(tb_ret.format_pprint())

        return tb_ret

    def generate_summarised_s3_cleanup_data(self, buckets_dir_path, summarised_data_file):
        """
        Because the amount of data can be very large I use data summarization before generating report.
        The data is being written to a file.

        @param buckets_dir_path:
        @param summarised_data_file:
        @return:
        """
        all_buckets = dict()
        for bucket_dir in os.listdir(buckets_dir_path):
            by_date_split = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {"keys": 0, "size": 0})))
            logger.info(f"Init bucket in dir '{bucket_dir}'")

            bucket_dir_path = os.path.join(buckets_dir_path, bucket_dir)
            for objects_buffer_file in os.listdir(bucket_dir_path):
                logger.info(f"Init objects chunk in dir {bucket_dir}/{objects_buffer_file}")
                objects_buffer_file_path = os.path.join(bucket_dir_path, objects_buffer_file)

                with open(objects_buffer_file_path) as fh:
                    lst_objects = json.load(fh)

                for dict_object in lst_objects:
                    bucket_object = S3Bucket.BucketObject(dict_object, from_cache=True)
                    by_date_split[bucket_object.last_modified.year][bucket_object.last_modified.month][bucket_object.last_modified.day]["keys"] += 1
                    by_date_split[bucket_object.last_modified.year][bucket_object.last_modified.month][bucket_object.last_modified.day]["size"] += bucket_object.size
            all_buckets[bucket_dir] = by_date_split
        with open(summarised_data_file, "w") as fh:
            json.dump(all_buckets, fh)

    def cleanup_report_s3_buckets_objects_large(self, all_buckets):
        """
        Generate cleanup report for s3 large buckets- buckets, with a metadata to large for RAM.
        @param all_buckets:
        @return:
        """
        tb_ret = TextBlock(header="Large buckets")
        lst_buckets_total = []
        for bucket_name, by_year_split in all_buckets:
            bucket_total = sum([per_year_data["size"] for per_year_data in by_year_split.values()])
            lst_buckets_total.append((bucket_name, bucket_total))

        lst_buckets_total_sorted = sorted(lst_buckets_total, reverse=True, key=lambda x: x[1])
        for name, size in lst_buckets_total_sorted[:20]:
            tb_ret.lines.append(f"{name}: {CommonUtils.bytes_to_str(size)}")
        #raise NotImplementedError("Replacement of pdb.set_trace")
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
        account_id = account_id[:account_id.find(":")]
        if not account_id.isdigit():
            raise ValueError(arn)
        return account_id

    def cleanup_report_iam_roles(self, output_file):
        time_limit = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=30)
        tb_ret = TextBlock("Unused IAM roles. Last use time > 30 days")

        for role in self.iam_roles:
            if role.role_last_used_time is None:
                tb_ret.lines.append(f"Role: '{role.name}' last used: Never")
                continue
            if role.role_last_used_time < time_limit:
                tb_ret.lines.append(f"Role: '{role.name}' last used: {role.role_last_used_time}")

        with open(output_file, "w+") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        return tb_ret

    def cleanup_report_cloud_watch_metrics(self, metrics_dir, output_file):
        """
        800 150 130 +50

        @param metrics_dir:
        @param output_file:
        @return:
        """
        tb_ret = TextBlock("Cloudwatch metrics report")
        chunk_files = os.listdir(metrics_dir)
        for i in range(len(chunk_files)):
            chunk_file_name = chunk_files[i]
            chunk_file_path = os.path.join(metrics_dir, chunk_file_name)
            with open(chunk_file_path) as file_handler:
                metrics_dicts = json.load(file_handler)

            metrics = [CloudWatchMetric(metric) for metric in metrics_dicts]

        namespaces = defaultdict(list)
        for metric in metrics:
            namespaces[metric.namespace].append(metric)

        for namespace, metrics in sorted(namespaces.items(), reverse=True, key=lambda namespace_metrics: len(namespace_metrics[1])):
            tb_namespace = TextBlock(f"Namespace: '{namespace}', metrics count: '{len(metrics)}'")
            metrics_per_name = defaultdict(list)
            for metric in metrics:
                metrics_per_name[metric.name].append(metric)
            tb_namespace.lines = [f"Metric name: '{metric_name}': Different Dimensions: {len(metrics_per_name[metric_name])}" for metric_name in metrics_per_name]
            tb_ret.blocks.append(tb_namespace)

        with open(output_file, "w+") as file_handler:
            file_handler.write(tb_ret.format_pprint())
        return tb_ret

    def cleanup_report_cloud_watch_log_groups(self, streams_dir, output_file, top_streams_count=100):
        """
        Generate cleanup report for cloudwatch log groups - too big, too old etc.

        @param streams_dir: Full path to the streams' cache dir
        @param output_file:
        @param top_streams_count: Top most streams count to show in the report.
        @return:
        """
        dict_total = {"size": 0, "streams_count": 0, "data": []}
        log_group_subdirs = os.listdir(streams_dir)
        for i in range(len(log_group_subdirs)):
            log_group_subdir = log_group_subdirs[i]
            logger.info(f"Log group sub directory {i}/{len(log_group_subdirs)}")
            dict_log_group = {"name": log_group_subdir, "size": 0, "streams_count": 0, "data": {"streams_by_date": []}}
            log_group_full_path = os.path.join(streams_dir, log_group_subdir)

            log_group_chunk_files = os.listdir(log_group_full_path)
            for j in range(len(log_group_chunk_files)):
                chunk_file = log_group_chunk_files[j]
                logger.info(f"Chunk files in log group dir {j}/{len(log_group_chunk_files)}")

                with open(os.path.join(log_group_full_path, chunk_file)) as fh:
                    streams = json.load(fh)
                log_group_name = streams[0]["arn"].split(":")[6]
                log_group = CommonUtils.find_objects_by_values(self.cloud_watch_log_groups, {"name": log_group_name}, max_count=1)[0]
                dict_log_group["size"] = log_group.stored_bytes
                for stream in streams:
                    dict_log_group["streams_count"] += 1
                    self.cleanup_report_cloud_watch_log_groups_handle_sorted_streams(top_streams_count, dict_log_group, stream)

            dict_total["size"] += dict_log_group["size"]
            dict_total["streams_count"] += dict_log_group["streams_count"]
            dict_total["data"].append(dict_log_group)
        dict_total["data"] = sorted(dict_total["data"], key=lambda x: x["size"], reverse=True)
        tb_ret = self.cleanup_report_cloud_watch_log_groups_prepare_tb(dict_total, top_streams_count)
        with open(output_file, "w+") as file_handler:
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
        for i in range(len(items)):
            if item_to_insert_weight < get_item_weight(items[i]):
                logger.info(f"Found new item to insert with weight {item_to_insert_weight} at place {i} where current weight is {get_item_weight(items[i])}")
                break

        while i > -1:
            item_to_insert_tmp = items[i]
            items[i] = item_to_insert
            item_to_insert = item_to_insert_tmp
            i -= 1

    def cleanup_report_cloud_watch_log_groups_handle_sorted_streams(self, top_streams_count, dict_log_group, stream):
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
            dict_log_group["data"]["streams_by_date"] = sorted(dict_log_group["data"]["streams_by_date"],
                                                               key=lambda x: -(
                                                               x["lastIngestionTime"] if "lastIngestionTime" in x else
                                                               x["creationTime"]))
            return

        self.enter_n_sorted(dict_log_group["data"]["streams_by_date"],
                        lambda x: -(x["lastIngestionTime"] if "lastIngestionTime" in x else x["creationTime"]), stream)

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
                f"{dict_log_group['name']} size: {CommonUtils.bytes_to_str(dict_log_group['size'])}, streams: {CommonUtils.int_to_str(dict_log_group['streams_count'])}")
            logger.info(dict_log_group['name'])

            if dict_log_group['streams_count'] > top_streams_count:
                lines = []
                for stream in dict_log_group["data"]["streams_by_date"]:
                    logger.info(stream["logStreamName"])
                    name = stream["logStreamName"]
                    last_accessed = stream["lastIngestionTime"] if "lastIngestionTime" in stream else stream["creationTime"]
                    last_accessed = CommonUtils.timestamp_to_datetime(last_accessed / 1000.0)
                    lines.append(f"{name} last_accessed: {last_accessed}")

                tb_streams_by_date = TextBlock(
                    f"{top_streams_count} ancient streams")
                tb_streams_by_date.lines = lines
                tb_log_group.blocks.append(tb_streams_by_date)

            tb_ret.blocks.append(tb_log_group)
        return tb_ret

    def cleanup_load_balancers(self, output_file):
        """
        Generate load balancers' cleanup report.
        @param output_file:
        @return:
        """
        tb_ret = TextBlock("Load Balancers Cleanup")
        tb_ret_tmp = self.cleanup_classic_load_balancers()
        if tb_ret_tmp is not None:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.cleanup_alb_load_balancers()
        if tb_ret_tmp is not None:
            tb_ret.blocks.append(tb_ret_tmp)

        tb_ret_tmp = self.cleanup_target_groups()
        if tb_ret_tmp.lines or tb_ret_tmp.blocks:
            tb_ret.blocks.append(tb_ret_tmp)

        with open(output_file, "w+") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        return tb_ret

    def cleanup_classic_load_balancers(self):
        """
        Generate cleanup report for classic load balancers.

        @return:
        """
        tb_ret = TextBlock("Cleanup report classic load balancers")
        tb_ret_no_instances = TextBlock("No instances associated with these load balancers")
        tb_ret_no_listeners = TextBlock("No listeners associated with these load balancers")
        for load_balancer in self.classic_load_balancers:
            if not load_balancer.listeners:
                tb_ret_no_listeners.lines.append(load_balancer.name)

            if not load_balancer.instances:
                tb_ret_no_instances.lines.append(load_balancer.name)

        if len(tb_ret_no_instances.lines) > 0:
            tb_ret.blocks.append(tb_ret_no_instances)

        if len(tb_ret_no_listeners.lines) > 0:
            tb_ret.blocks.append(tb_ret_no_listeners)

        return tb_ret if len(tb_ret.blocks) > 0 else None

    def cleanup_alb_load_balancers(self):
        """
        Generate cleanup report for alb load balancers.

        @return:
        """
        tb_ret = TextBlock("Cleanup report ALBs")
        tb_ret_no_tgs = TextBlock("No target groups associated with these load balancers")
        tb_ret_no_listeners = TextBlock("No listeners associated with these load balancers")

        lbs_using_tg = set()
        for target_group in self.target_groups:
            lbs_using_tg.update(target_group.load_balancer_arns)

        for load_balancer in self.load_balancers:
            if not load_balancer.listeners:
                tb_ret_no_listeners.lines.append(load_balancer.name)

            if load_balancer.arn not in lbs_using_tg:
                tb_ret_no_tgs.lines.append(load_balancer.name)

        if len(tb_ret_no_tgs.lines) > 0:
            tb_ret.blocks.append(tb_ret_no_tgs)

        if len(tb_ret_no_listeners.lines) > 0:
            tb_ret.blocks.append(tb_ret_no_listeners)

        return tb_ret if len(tb_ret.blocks) > 0 else None

    def cleanup_target_groups(self):
        """
        Cleanup report find unhealthy target groups
        @return:
        """
        tb_ret = TextBlock("Following target groups have a bad health")
        for target_group in self.target_groups:
            if not target_group.target_health:
                tb_ret.lines.append(target_group.name)
        return tb_ret if len(tb_ret.lines) > 0 else None

    def cleanup_report_security_groups(self, report_file_path):
        """
        Generating security group cleanup reports.

        @param report_file_path:
        @return:
        """
        tb_ret = TextBlock("EC2 security groups cleanup")
        tb_ret.blocks.append(self.cleanup_report_wrong_port_lbs_security_groups())
        tb_ret.blocks.append(self.cleanup_report_unused_security_groups())
        tb_ret.blocks.append(self.cleanup_report_dangerous_security_groups())

        with open(report_file_path, "w+") as file_handler:
            file_handler.write(str(tb_ret))

        return tb_ret

    def cleanup_report_wrong_port_lbs_security_groups(self):
        """
        Checks load balancers' ports to security groups' internal ports.

        @return:
        """
        tb_ret = TextBlock("Wrong load balancer listeners ports")
        for load_balancer in self.load_balancers + self.classic_load_balancers:
            lines = self.cleanup_report_wrong_port_lb_security_groups(load_balancer)
            tb_ret.lines += lines

        return tb_ret

    def cleanup_report_unused_security_groups(self):
        tb_ret = TextBlock("Unused security groups")
        used_security_group_ids = []
        for interface in self.network_interfaces:
            sg_ids = interface.get_used_security_group_ids()
            used_security_group_ids += sg_ids
        used_security_group_ids = list(set(used_security_group_ids))
        all_security_groups_dict = {sg.id: sg.name for sg in self.security_groups}
        tb_ret.lines = [f"{sg_id} [{all_security_groups_dict[sg_id]}]" for sg_id in all_security_groups_dict if sg_id not in used_security_group_ids]
        return tb_ret

    def cleanup_report_dangerous_security_groups(self):
        tb_ret = TextBlock("Dangerously open security groups")
        for security_group in self.security_groups:
            pairs = security_group.get_ingress_pairs()
            if len(pairs) == 0:
                tb_ret.lines.append(f"No ingress rules in group {security_group.id} [{security_group.name}]")
                continue
            for ip, service in pairs:
                if ip is IP.any():
                    tb_ret.lines.append(f"Dangerously wide range of addresses {security_group.id} [{security_group.name}] - {ip}")

                if service is Service.any():
                    tb_ret.lines.append(f"Dangerously wide range of services {security_group.id} [{security_group.name}] - {service}")

        return tb_ret

    def cleanup_report_wrong_port_lb_security_groups(self, load_balancer):
        """
        Checks single load balancer's ports to security groups' internal ports.

        @param load_balancer:
        @return:
        """

        lines = []
        if load_balancer.network_security_groups is None:
            return lines

        listeners_ports = [listener.port for listener in load_balancer.listeners]
        listeners_ports = set(listeners_ports)

        listeners_services = []
        for port in listeners_ports:
            service = ServiceTCP()
            service.start = port
            service.end = port
            listeners_services.append(service)

        for security_group_id in load_balancer.network_security_groups:
            security_group = \
            CommonUtils.find_objects_by_values(self.security_groups, {"id": security_group_id}, max_count=1)[0]
            security_group_dst_pairs = security_group.get_ingress_pairs()

            for _, sg_service in security_group_dst_pairs:
                for listener_service in listeners_services:
                    if listener_service.intersect(sg_service) is not None:
                        break
                else:
                    lines.append(
                        f"Security group '{security_group.name}' has and open service '{str(sg_service)}' but no LB '{load_balancer.name}' listener on this port")

            for listener_service in listeners_services:
                for _, sg_service in security_group_dst_pairs:
                    if listener_service.intersect(sg_service) is not None:
                        break
                else:
                    lines.append(
                        f"There is LB '{load_balancer.name}' listener service '{listener_service}' but no security group permits a traffic to it")
        return lines

    def find_loadbalnacers_target_groups(self, load_balancer):
        return [target_group for target_group in self.target_groups if load_balancer.arn in target_group.load_balancer_arns]

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
            tb_zone.lines = [f"{record.name} -> {[resource_record['Value'] for resource_record in record.resource_records]}" for record in records]
            tb_ret.blocks.append(tb_zone)

        with open(output_file, "w+") as file_handler:
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

        with open(output_file, "w+") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        return tb_ret

    def cleanup_report_iam_unused_policies(self):
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
            lst_ret += [policy["_name"] for policy in role.policies]
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
            lines = self.cleanup_report_iam_policy_statements_optimize_not_statement(statement)
            if len(lines) > 0:
                tb_ret.lines += lines

        # todo: test and remove
        lines = self.cleanup_report_iam_policy_statements_intersecting_statements(policy)
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
                lines.append(f"Potential risk in too permissive not_action. Effect: 'Allow', not_action: '{statement.not_action}'")
            if statement.not_resource is not None:
                lines.append(f"Potential risk in too permissive not_resource. Effect: 'Allow', not_resource: '{statement.not_resource}'")
        return lines

    def cleanup_report_iam_policy_statements_intersecting_statements(self, policy):
        """
        Generating report of intersecting policies.
        @param policy:
        @return:
        """

        statements = policy.document.statements

        lines = []

        for i in range(len(statements)):
            statement_1 = statements[i]

            for j in range(i+1, len(statements)):
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
                lines.append(f"Policy: '{policy.name}' Common Action: {common_action} Common resource {common_resource}")
                lines.append(str(statement_1.dict_src))
                lines.append(str(statement_2.dict_src))
        return lines

    def get_secret_value(self, secret_name):
        return self.secretsmanager_client.raw_get_secret_string(secret_name)

    def put_secret_value(self, secret_name, value):
        return self.secretsmanager_client.raw_put_secret_string(secret_name, value)

    def put_secret_file(self, secret_name, file_path):
        with open(file_path) as file_handler:
            contents = file_handler.read()
        self.put_secret_value(secret_name, contents)

    def get_secret_file(self, secret_name, dir_path: str):
        if dir_path.endswith(secret_name):
            dir_path = os.path.dirname(dir_path)

        os.makedirs(dir_path, exist_ok=True)
        contents = self.get_secret_value(secret_name)

        with open(os.path.join(dir_path, secret_name), "w+") as file_handler:
            file_handler.write(contents)

    def copy_secrets_manager_secret_to_region(self, secret_name, region_src, region_dst):
        secret = self.secretsmanager_client.get_secret(secret_name, region_name=region_src)
        self.secretsmanager_client.put_secret(secret, region_name=region_dst)

    def add_ingress_to_security_group(self, security_group_name):
        self.init_security_groups()
        pdb.set_trace()

        security_group = CommonUtils.find_objects_by_values(self.security_groups, {"name": security_group_name}, max_count=1)[0]

        for ip_permission in security_group.ip_permissions:
            pass

    def provision_managed_prefix_list(self, managed_prefix_list):
        if managed_prefix_list.id is None:
            self.ec2_client.provision_managed_prefix_list(managed_prefix_list)
        live_managed_prefix_list = self.ec2_client.get_managed_prefix_list(managed_prefix_list.region.region_mark, managed_prefix_list.id)
        request = live_managed_prefix_list.get_entries_add_request(managed_prefix_list)

        if request is None:
            return True

        return self.ec2_client.raw_modify_managed_prefix_list(request)

    def provision_hosted_zone(self, hosted_zone):
        self.route53_client.create_hosted_zone(hosted_zone)

        for vpc_association in hosted_zone.vpc_associations[1:]:
            associate_request = {"HostedZoneId": hosted_zone.id,
            "VPC": vpc_association
            }

            self.route53_client.raw_associate_vpc_with_hosted_zone(associate_request)

        changes = []
        for record in hosted_zone.records:
            change = {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': record.name,
                    'Type': record.type,
                    'TTL': record.ttl,
                    'ResourceRecords': record.resource_records
                }
            }
            changes.append(change)
        request = {"HostedZoneId": hosted_zone.id, "ChangeBatch": {"Changes": changes}}
        return self.route53_client.raw_change_resource_record_sets(request)

    def add_elasticsearch_access_policy_raw_statements(self, elasticsearch_domain, raw_statements):
        access_policies = json.loads(elasticsearch_domain.access_policies)
        access_policies["Statement"] += raw_statements
        access_policies_str = json.dumps(access_policies)

        request = {"DomainName": elasticsearch_domain.name, "AccessPolicies": access_policies_str}
        self.elasticsearch_client.raw_update_elasticsearch_domain_config(request)

    def provision_vpc(self, vpc):
        self.ec2_client.provision_vpc(vpc)

    def provision_subnets(self, subnets):
        self.ec2_client.provision_subnets(subnets)

    def provision_security_group(self, security_group):
        self.ec2_client.provision_security_group(security_group)

    def provision_internet_gateway(self, internet_gateway):
        self.ec2_client.provision_internet_gateway(internet_gateway)

    def provision_vpc_peering(self, vpc_peering):
        self.ec2_client.provision_vpc_peering(vpc_peering)

    def provision_nat_gateways(self, nat_gateways):
        for nat_gateway in nat_gateways:
            self.provision_nat_gateway(nat_gateway)

        nat_gateways_tmp = [ngw for ngw in nat_gateways]
        while len(nat_gateways_tmp) > 0:
            to_del = []
            for nat_gateway_tmp in nat_gateways_tmp:
                for region_gateway in self.ec2_client.get_region_nat_gateways(nat_gateways_tmp[0].region):
                    if region_gateway.get_state() not in [region_gateway.State.PENDING, region_gateway.State.AVAILABLE]:
                        continue

                    if region_gateway.id == nat_gateway_tmp.id:
                        if region_gateway.get_state() == region_gateway.State.AVAILABLE:
                            to_del.append(nat_gateway_tmp)
                            break
                        break
                else:
                    raise RuntimeError(f"Can not find nat_gateway '{nat_gateway_tmp.get_tagname()}' in region nat_gateways")

            for ngw in to_del:
                nat_gateways_tmp.remove(ngw)

            if nat_gateways_tmp:
                time.sleep(10)

    def provision_nat_gateway(self, nat_gateway):
        self.ec2_client.provision_nat_gateway(nat_gateway)

    def provision_elastic_address(self, elastic_address):
        self.ec2_client.provision_elastic_address(elastic_address)

    def provision_route_table(self, route_table):
        self.ec2_client.provision_route_table(route_table)

    def provision_ec2_instance(self, ec2_instance):
        self.ec2_client.provision_ec2_instance(ec2_instance)

    def provision_key_pair(self, key_pair, save_to_secrets_manager=None, private_key_region=None):
        logger.info(f"provisioning ssh key pair {key_pair.name}")
        response = self.ec2_client.provision_key_pair(key_pair)
        if response is None:
            return

        if save_to_secrets_manager:
            AWSAccount.set_aws_region(private_key_region)
            self.put_secret_value(key_pair.name + ".key", response["KeyMaterial"])
        else:
            return response


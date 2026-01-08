# pylint: disable = too-many-lines
"""
Standard environment maintainer.

"""
import json
import os
from pathlib import Path
# pylint: disable= no-name-in-module
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.aws_api.aws_services_entities.vpc import VPC
from horey.aws_api.aws_services_entities.subnet import Subnet
from horey.aws_api.aws_services_entities.ec2_security_group import EC2SecurityGroup
from horey.aws_api.aws_services_entities.ec2_launch_template import EC2LaunchTemplate
from horey.aws_api.aws_services_entities.auto_scaling_group import AutoScalingGroup
from horey.aws_api.aws_services_entities.iam_instance_profile import IamInstanceProfile
from horey.aws_api.aws_services_entities.iam_policy import IamPolicy
from horey.aws_api.aws_services_entities.iam_role import IamRole
from horey.aws_api.aws_services_entities.key_pair import KeyPair
from horey.aws_api.aws_services_entities.ecs_cluster import ECSCluster
from horey.aws_api.aws_services_entities.internet_gateway import InternetGateway
from horey.aws_api.aws_services_entities.route_table import RouteTable
from horey.aws_api.aws_services_entities.elastic_address import ElasticAddress
from horey.aws_api.aws_services_entities.nat_gateway import NatGateway
from horey.aws_api.aws_services_entities.s3_bucket import S3Bucket
from horey.aws_api.aws_services_entities.cloudfront_origin_access_identity import CloudfrontOriginAccessIdentity
from horey.aws_api.aws_services_entities.acm_certificate import ACMCertificate
from horey.aws_api.aws_services_entities.cloudfront_response_headers_policy import CloudfrontResponseHeadersPolicy
from horey.aws_api.aws_services_entities.cloudfront_distribution import CloudfrontDistribution
from horey.aws_api.aws_services_entities.route53_hosted_zone import HostedZone
from horey.aws_api.aws_services_entities.wafv2_ip_set import WAFV2IPSet
from horey.aws_api.aws_services_entities.wafv2_web_acl import WAFV2WebACL
from horey.aws_api.aws_services_entities.ecs_task_definition import ECSTaskDefinition
from horey.aws_api.aws_services_entities.ecs_service import ECSService
from horey.aws_api.aws_services_entities.sns_topic import SNSTopic
from horey.aws_api.aws_services_entities.sns_subscription import SNSSubscription
from horey.aws_api.aws_services_entities.dynamodb_table import DynamoDBTable
from horey.aws_api.aws_services_entities.aws_lambda import AWSLambda
from horey.aws_api.aws_services_entities.cloud_watch_log_group import CloudWatchLogGroup
from horey.aws_api.aws_services_entities.cloud_watch_log_group_metric_filter import CloudWatchLogGroupMetricFilter
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm
from horey.aws_api.aws_services_entities.event_bridge_rule import EventBridgeRule
from horey.aws_api.aws_services_entities.event_bridge_target import EventBridgeTarget
from horey.aws_api.aws_services_entities.ses_identity import SESIdentity
from horey.aws_cleaner.aws_cleaner import AWSCleaner, ReportActionCloudwatchAlarm, ReportActionCloudwatchLogGroupMetric, \
    ReportActionECSCapacityProvider
from horey.aws_cleaner.aws_cleaner_configuration_policy import AWSCleanerConfigurationPolicy
from horey.aws_api.aws_services_entities.elbv2_load_balancer import LoadBalancer
from horey.aws_api.aws_services_entities.sesv2_configuration_set import SESV2ConfigurationSet
from horey.aws_api.aws_services_entities.ecs_capacity_provider import ECSCapacityProvider
from horey.docker_api.docker_api import DockerAPI

from horey.network.ip import IP
from horey.h_logger import get_logger

logger = get_logger()


class EnvironmentAPI:
    """
    AWS VPC environment

    """

    def __init__(self, configuration: EnvironmentAPIConfigurationPolicy, aws_api: AWSAPI, git_api=None):
        self.configuration = configuration
        if AWSAccount.get_aws_account() is None:
            default_account = AWSAccount()
            default_account.name = default_account.id = "environment_api_default"
            default_account.connection_steps = [AWSAccount.ConnectionStep({"role": "current",
                                                                           "region_mark": self.configuration.region})]
            AWSAccount.set_aws_account(default_account)
            AWSAccount.set_aws_default_region(self.region)

        self.aws_api = aws_api
        self.git_api = git_api
        self._docker_api = None

        cache_dir = Path(self.configuration.data_directory_path, "cache")
        if not cache_dir.exists():
            os.makedirs(cache_dir)

        self.aws_api.sts_client.main_cache_dir_path = str(cache_dir)
        if self.aws_api.configuration:
            self.aws_api.configuration.aws_api_cache_dir = self.aws_api.sts_client.main_cache_dir_path

        self._vpc = None
        self._subnets = None
        self.jenkins_api = None
        self._public_subnets = None
        self._private_subnets = None

    @property
    def docker_api(self):
        """
        Object getter

        :return:
        """
        if self._docker_api is None:
            self._docker_api = DockerAPI()
        return self._docker_api

    @property
    def region(self):
        """
        Object getter

        :return:
        """

        return Region.get_region(self.configuration.region)

    @property
    def vpc(self):
        """
        Object getter

        :return:
        """
        if self._vpc is None:
            filters = [{
                "Name": "tag:Name",
                "Values": [
                    self.configuration.vpc_name
                ]
            }]

            vpcs = self.aws_api.ec2_client.get_region_vpcs(self.region, filters=filters)
            if len(vpcs) > 1:
                raise RuntimeError(f"Found more then 1 vpc by filters {filters}")

            if len(vpcs) == 1:
                self._vpc = vpcs[0]
            else:
                raise RuntimeError(f"Can not find VPC: {filters}")

        return self._vpc

    @vpc.setter
    def vpc(self, value):
        """
        Object getter

        :return:
        """

        self._vpc = value

    @property
    def subnets(self):
        """
        Object getter

        :return:
        """

        if self._subnets is None:
            filters_req = {"Filters": [
                {"Name": "vpc-id", "Values": [self.vpc.id]},
            ]}
            self._subnets = []
            for subnet in self.aws_api.ec2_client.yield_subnets(region=self.region, filters_req=filters_req,
                                                                update_info=True):
                # if subnet.get_tag("Owner") != "Horey":
                #    raise self.OwnerError(f"{subnet.id}")
                self._subnets.append(subnet)

        return self._subnets

    @subnets.setter
    def subnets(self, value):
        """
        Object getter

        :return:
        """

        self._subnets = value

    def get_all_public_subnets(self):
        """
        Get all

        :return:
        """

        subnets = []
        for subnet in self.subnets:
            if self.configuration.public_subnets:
                if subnet.id in self.configuration.public_subnets:
                    subnets.append(subnet)
                continue
            if "public" in subnet.get_tagname("Name"):
                generated_name = self.configuration.subnet_name_template.format(type="public",
                                                                                id=subnet.availability_zone_id)
                if subnet.get_tagname("Name") != generated_name:
                    raise ValueError(
                        f"Subnet {subnet.id} tag Name expected: {generated_name}, configured {subnet.get_tagname('Name')}")
                subnets.append(subnet)
        return subnets

    def get_all_private_subnets(self):
        """
        Get all

        :return:
        """
        subnets = []
        for subnet in self.subnets:
            if self.configuration.private_subnets:
                if subnet.id in self.configuration.private_subnets:
                    subnets.append(subnet)
                continue

            if "private" in subnet.get_tagname("Name"):
                generated_name = self.configuration.subnet_name_template.format(type="private",
                                                                                id=subnet.availability_zone_id)
                if subnet.get_tagname("Name") != generated_name:
                    raise ValueError(
                        f"Subnet {subnet.id} tag Name expected: {generated_name}, configured {subnet.get_tagname('Name')}")
                subnets.append(subnet)
        return subnets

    def init_private_and_public_subnets(self):
        """
        Find matching.

        :return:
        """

        all_public_subnets = self.get_all_public_subnets()
        all_private_subnets = self.get_all_private_subnets()
        public_subnets = {subnet.availability_zone_id: subnet for subnet in all_public_subnets}
        private_subnets = {subnet.availability_zone_id: subnet for subnet in all_private_subnets}
        intersection_set = set(public_subnets).intersection(set(private_subnets))
        if len(intersection_set) < self.configuration.availability_zones_count:
            raise RuntimeError(f"Subnet intersection. Private {[sub.id for sub in all_private_subnets]}, Public {[sub.id for sub in all_public_subnets]}, {intersection_set=}")

        az_ids = list(intersection_set)[:self.configuration.availability_zones_count:]
        self._private_subnets = [private_subnets[az_id] for az_id in az_ids]
        self._public_subnets = [public_subnets[az_id] for az_id in az_ids]

    @property
    def public_subnets(self):
        """
        Get the public subnets.

        :return:
        """

        if self._public_subnets is None:
            if self._private_subnets is not None:
                raise NotImplementedError("_public_subnets and _private_subnets should be initialized together")

            self.init_private_and_public_subnets()
        return self._public_subnets

    @property
    def private_subnets(self):
        """
        Get the public subnets.

        :return:
        """
        if self._private_subnets is None:
            if self._public_subnets is not None:
                raise NotImplementedError("_public_subnets and _private_subnets should be initialized together")
            self.init_private_and_public_subnets()
        return self._private_subnets

    def provision(self):
        """
        Provision all environment components.

        :return:
        """

        self.provision_vpc()

    def provision_vpc(self):
        """
        Provision VPC

        :return:
        """

        self.vpc = VPC({})
        self.vpc.region = self.region
        self.vpc.cidr_block = self.configuration.vpc_primary_subnet

        self.vpc.tags = self.get_tags_with_name(self.configuration.vpc_name)

        self.aws_api.provision_vpc(self.vpc)
        return self.vpc

    def provision_subnets(self):
        """
        Provision VPC subnets.

        :return:
        """

        all_zones = self.aws_api.ec2_client.get_all_availability_zones(region=self.region)
        valid_availability_zones = [zone for zone in all_zones if zone.zone_type == "availability-zone"]
        if len(valid_availability_zones) < self.configuration.availability_zones_count:
            raise ValueError(
                f"Not enough availability zones: needs {self.configuration.availability_zones_count} found only {len(valid_availability_zones)}")

        vpc_cidr_address = IP(self.configuration.vpc_primary_subnet)
        vpc_subnets = vpc_cidr_address.split(self.configuration.subnet_mask_length)
        availability_zones = valid_availability_zones[:self.configuration.availability_zones_count]

        if len(vpc_subnets) < self.configuration.availability_zones_count * 2:
            raise RuntimeError(
                "Available VPC subnets do not cover the required for private and public subnets")

        public_subnet_index = len(vpc_subnets) // 2

        subnets = []
        for az_counter, availability_zone in enumerate(availability_zones):
            private_subnet_az_cidr = vpc_subnets[az_counter].str_address_slash_short_mask()
            public_subnet_az_cidr = vpc_subnets[public_subnet_index + az_counter].str_address_slash_short_mask()

            # private
            private_subnet_az = Subnet({})
            private_subnet_az.cidr_block = private_subnet_az_cidr
            private_subnet_az.vpc_id = self.vpc.id
            private_subnet_az.availability_zone_id = availability_zone.id
            private_subnet_az.region = Region.get_region(self.configuration.region)

            private_subnet_az.tags = self.get_tags_with_name(self.configuration.subnet_name_template.format(type="private",
                                                                        id=private_subnet_az.availability_zone_id))
            subnets.append(private_subnet_az)

            # public
            public_subnet_az = Subnet({})
            public_subnet_az.cidr_block = public_subnet_az_cidr
            public_subnet_az.vpc_id = self.vpc.id
            public_subnet_az.availability_zone_id = availability_zone.id
            public_subnet_az.region = Region.get_region(self.configuration.region)

            public_subnet_az.tags = self.get_tags_with_name(self.configuration.subnet_name_template.format(type="public",
                                                                        id=public_subnet_az.availability_zone_id))
            subnets.append(public_subnet_az)

        self.aws_api.provision_subnets(subnets)
        return subnets

    def provision_bastion(self):
        """
        Create/update bastion server.

        :return:
        """

    def provision_routing(self):
        """
        Provision routing tables and gateways.

        :return:
        """

        internet_gateway = self.provision_internet_gateway()
        self.provision_public_route_tables(internet_gateway)

        elastic_addresses = self.provision_elastic_addresses()
        nat_gateways = self.provision_nat_gateways(elastic_addresses)
        self.provision_private_route_tables(nat_gateways)
        return True

    def provision_internet_gateway(self):
        """
        Provision the main public router - gateway to the internet.

        :return:
        """

        inet_gateway = InternetGateway({})
        inet_gateway.attachments = [{"VpcId": self.vpc.id}]
        inet_gateway.region = self.region
        inet_gateway.tags = self.get_tags_with_name(self.configuration.internet_gateway_name)

        self.aws_api.provision_internet_gateway(inet_gateway)

        return inet_gateway

    def provision_public_route_tables(self, internet_gateway):
        """
        Public subnets route tables.

        :param internet_gateway:
        :return:
        """

        route_tables = []
        for public_subnet in self.public_subnets:
            route_table = RouteTable({})
            route_table.region = self.region
            route_table.vpc_id = self.vpc.id
            route_table.associations = [{
                "SubnetId": public_subnet.id
            }]

            route_table.routes = [{
                "DestinationCidrBlock": "0.0.0.0/0",
                "GatewayId": internet_gateway.id
            }]

            route_table.tags = self.get_tags_with_name(self.configuration.route_table_name_template.format(subnet=public_subnet.get_tagname()))

            self.aws_api.provision_route_table(route_table)
            route_tables.append(route_table)

        return route_tables

    def provision_elastic_addresses(self):
        """
        Provision the public ip addresses to be used in the VPC.

        :return:
        """

        elastic_addresses = []
        for counter in range(self.configuration.nat_gateways_count):
            elastic_address = ElasticAddress({})
            elastic_address.region = self.region
            elastic_address.tags = self.get_tags_with_name(self.configuration.nat_gateway_elastic_address_name_template.format(id=counter))

            elastic_addresses.append(elastic_address)

            self.aws_api.provision_elastic_address(elastic_address)

        return elastic_addresses

    def provision_nat_gateways(self, elastic_addresses):
        """
        Must occur after public route tables, because of the error:
        Network vpc-xxxx has no Internet gateway attached

        :param elastic_addresses
        :return:
        """

        nat_gateways = []
        elastic_addresses_names = [self.configuration.nat_gateway_elastic_address_name_template.format(id=counter) for
                                   counter in range(self.configuration.nat_gateways_count)]

        nat_elastic_addresses = [elastic_address for elastic_address in elastic_addresses if
                                 elastic_address.get_tagname() in elastic_addresses_names]

        for counter, subnet in enumerate(self.public_subnets[:self.configuration.nat_gateways_count]):
            nat_gateway = NatGateway({})
            nat_gateway.subnet_id = subnet.id
            nat_gateway.region = self.region
            nat_gateway.connectivity_type = "public"
            nat_gateway.allocation_id = nat_elastic_addresses[counter].id
            nat_gateway.tags = self.get_tags_with_name(self.configuration.nat_gateway_name_template.format(subnet=subnet.get_tagname()))
            nat_gateways.append(nat_gateway)

        self.aws_api.provision_nat_gateways(nat_gateways)
        return nat_gateways

    def provision_private_route_tables(self, nat_gateways):
        """
        Public subnets route tables.

        :param nat_gateways:
        :return:
        """

        nat_gateways_count = len(nat_gateways)
        for i, private_subnet in enumerate(self.private_subnets):
            route_table = RouteTable({})
            route_table.region = self.region
            route_table.vpc_id = self.vpc.id
            route_table.associations = [{
                "SubnetId": private_subnet.id
            }]

            route_table.routes = [{
                "DestinationCidrBlock": "0.0.0.0/0",
                "NatGatewayId": nat_gateways[i // nat_gateways_count].id
            }]

            route_table.tags = self.get_tags_with_name(self.configuration.route_table_name_template.format(subnet=private_subnet.get_tagname()))

            self.aws_api.provision_route_table(route_table)
        return True

    def dispose_nat_gateways(self):
        """
        Delete all nat gateways.

        :return:
        """

        filters_req = {"Filters": [{
            "Name": "tag:Owner",
            "Values": [
                "Horey"
            ]
        },
            {"Name": "vpc-id", "Values": [self.vpc.id]}]}

        for nat_gateway in self.aws_api.ec2_client.get_region_nat_gateways(self.region, filters_req=filters_req):
            self.aws_api.ec2_client.dispose_nat_gateway(nat_gateway)
        return True

    def dispose_elastic_addresses(self):
        """
        Delete all elastic addresses.

        :return:
        """

        filters_req = {"Filters": [{
            "Name": "tag:Owner",
            "Values": [
                "Horey"
            ]
        }]}

        for elastic_address in self.aws_api.ec2_client.get_region_elastic_addresses(self.region,
                                                                                    filters_req=filters_req):
            if elastic_address.association_id is None:
                self.aws_api.ec2_client.dispose_elastic_addresses(elastic_address)
            else:
                raise ValueError(f"Unexpected elastic address association: {elastic_address.association_id}")

    def dispose_bastion(self):
        """
        Create/update bastion server.

        :return:
        """

    def dispose_route_tables(self):
        """
        Delete all route tables

        :return:
        """

        filters_req = {"Filters": [
            {"Name": "vpc-id", "Values": [self.vpc.id]},
        ]}
        route_tables = list(
            self.aws_api.ec2_client.yield_route_tables(region=self.region, update_info=True, filters_req=filters_req))
        objects = []
        for obj in route_tables:
            try:
                if obj.vpc_id != self.vpc.id:
                    raise RuntimeError(f"{obj.vpc_id} != {self.vpc.id=}")
            except RuntimeError as error_inst:
                if "Can not find VPC" not in repr(error_inst):
                    raise
                return True

            if len(obj.associations) > 1:
                raise ValueError(f"{obj.associations=}")
            if obj.associations and obj.associations[0].get("Main"):
                continue
            objects.append(obj)

        self.aws_api.ec2_client.dispose_route_tables(objects)
        return True

    def dispose_internet_gateway(self):
        """
        Delete i-gwy

        :return:
        """
        filters_req = {"Filters": [
            {"Name": "attachment.vpc-id", "Values": [self.vpc.id]},
        ]}

        igws = list(self.aws_api.ec2_client.get_region_internet_gateways(self.region, full_information=True,
                                                                         filters_req=filters_req))

        if not igws:
            return True

        if len(igws) > 1:
            raise ValueError(f"Found > 1 Internet gateways: {filters_req}")

        if igws[0].get_tagname() != self.configuration.internet_gateway_name:
            raise ValueError(f"{igws[0].get_tagname()=} != {self.configuration.internet_gateway_name=}")

        self.aws_api.ec2_client.dispose_internet_gateway(igws[0])
        return True

    def dispose_subnets(self):
        """
        Delete all VPC subnets.

        :return:
        """

        self.aws_api.ec2_client.dispose_subnets(self.subnets)
        return True

    def dispose_vpc(self):
        """
        Delete VPC

        :return:
        """

        self.aws_api.ec2_client.dispose_vpc(self.vpc)
        return True

    def provision_ecs_infra(self):
        """
        AWS infra.

        :return:
        """

        self.provision_container_instance_security_group()
        self.provision_container_instance_ssh_key()
        launch_template = self.provision_container_instance_launch_template()
        ecs_cluster = self.provision_ecs_cluster()
        auto_scaling_group = self.provision_container_instance_auto_scaling_group(launch_template)
        self.provision_ecs_capacity_provider(auto_scaling_group)
        self.attach_capacity_provider_to_ecs_cluster(ecs_cluster)
        return True

    def provision_container_instance_security_group(self):
        """
        Provision the container instance security group.

        :return:
        """

        return self.provision_security_group(self.configuration.container_instance_security_group_name)

    def provision_security_group(self, name, ip_permissions=None, description=None):
        """
        Provision security group.

        :param description:
        :param ip_permissions:
        :param name:
        :return:
        """

        security_group = EC2SecurityGroup({})
        security_group.vpc_id = self.vpc.id
        security_group.name = name
        security_group.description = description or name
        security_group.region = self.region
        security_group.tags = self.get_tags_with_name(security_group.name)

        if ip_permissions is not None:
            security_group.ip_permissions = ip_permissions

        self.aws_api.provision_security_group(security_group, provision_rules=bool(ip_permissions))

        return security_group

    def provision_container_instance_ssh_key(self):
        """
        Standard.

        :return:
        """

        return self.provision_ssh_key(self.configuration.container_instance_ssh_key_pair_name)

    def provision_ssh_key(self, name):
        """
        Standard.

        :return:
        """

        key_pair = KeyPair({})
        key_pair.name = name
        key_pair.key_type = "ed25519"
        key_pair.region = self.region
        key_pair.tags = self.get_tags_with_name(key_pair.name)

        self.aws_api.provision_key_pair(key_pair, save_to_secrets_manager=True,
                                        secrets_manager_region=Region.get_region(
                                            self.configuration.secrets_manager_region))

        return key_pair

    def provision_container_instance_launch_template(self):
        """
        Provision container instance launch template.

        :return:
        """

        security_group = self.aws_api.get_security_group_by_vpc_and_name(self.vpc,
                                                                         self.configuration.container_instance_security_group_name)

        param = self.aws_api.ssm_client.get_region_parameter(self.region,
                                                             "/aws/service/ecs/optimized-ami/amazon-linux-2/recommended")

        filter_request = {"ImageIds": [json.loads(param.value)["image_id"]]}
        amis = self.aws_api.ec2_client.get_region_amis(self.region, custom_filters=filter_request)
        if len(amis) > 1:
            raise RuntimeError(f"Can not find single AMI using filter: {filter_request['Filters']}")

        ami = amis[0]
        user_data = self.generate_hagent_user_data()

        launch_template = EC2LaunchTemplate({})
        launch_template.name = self.configuration.container_instance_launch_template_name
        launch_template.region = self.region
        launch_template.tags = self.get_tags_with_name(launch_template.name)

        launch_template.launch_template_data = {"EbsOptimized": False,
                                                "IamInstanceProfile": {
                                                    "Arn": self.provision_container_instance_iam_profile().arn
                                                },
                                                "BlockDeviceMappings": [
                                                    {
                                                        "DeviceName": "/dev/xvda",
                                                        "Ebs": {
                                                            "VolumeSize": 30,
                                                            "VolumeType": "gp3"
                                                        }
                                                    }
                                                ],
                                                "ImageId": ami.id,
                                                "InstanceType": "c5.large",
                                                "KeyName": self.configuration.container_instance_ssh_key_pair_name,
                                                "Monitoring": {
                                                    "Enabled": False
                                                },
                                                "NetworkInterfaces": [
                                                    {
                                                        "AssociatePublicIpAddress": False,
                                                        "DeleteOnTermination": True,
                                                        "DeviceIndex": 0,
                                                        "Groups": [
                                                            security_group.id,
                                                        ]
                                                    },
                                                ],
                                                "UserData": user_data
                                                }
        self.aws_api.provision_launch_template(launch_template)
        return launch_template

    def generate_hagent_user_data(self):
        """
        EC2 container instance user data to run on ec2 start.

        :return:
        """

        str_user_data = "#!/bin/bash\n" + \
                        f'echo "ECS_CLUSTER={self.configuration.ecs_cluster_name}" >> /etc/ecs/ecs.config'

        user_data = self.aws_api.ec2_client.generate_user_data(str_user_data)
        return user_data

    def provision_container_instance_iam_profile(self):
        """
        Standard.

        :return:
        """
        self.provision_instance_profile(self.configuration.container_instance_role_name,
                                        self.configuration.container_instance_profile_name)

    def provision_instance_profile(self, role_name, profile_name):
        """
        Provision EC2 instance role and profile.

        :param role_name:
        :param profile_name:
        :return:
        """

        assume_role_policy = """{
                "Version": "2012-10-17",
                "Statement": [
                {
                "Effect": "Allow",
                "Principal": {
                "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
                }
                ]
                }"""

        iam_role = IamRole({})
        iam_role.name = role_name
        iam_role.assume_role_policy_document = assume_role_policy
        iam_role.description = iam_role.name
        iam_role.max_session_duration = 3600
        iam_role.tags = self.get_tags_with_name(iam_role.name)

        iam_role.path = self.configuration.iam_path
        iam_role.managed_policies_arns = ["arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"]
        self.aws_api.iam_client.provision_role(iam_role)

        iam_instance_profile = IamInstanceProfile({})
        iam_instance_profile.name = profile_name
        iam_instance_profile.path = self.configuration.iam_path
        iam_instance_profile.tags = self.get_tags_with_name(iam_instance_profile.name)
        iam_instance_profile.roles = [{"RoleName": iam_role.name}]
        self.aws_api.iam_client.provision_instance_profile(iam_instance_profile)
        return iam_instance_profile

    def provision_ecs_cluster(self):
        """
        Provision the ECS cluster for this env.

        :return:
        """

        cluster = ECSCluster({})
        cluster.settings = [
            {
                "name": "containerInsights",
                "value": "enabled"
            }
        ]
        cluster.name = self.configuration.ecs_cluster_name
        cluster.region = self.region
        cluster.tags = [{key.lower(): value for key, value in dict_tag.items()} for dict_tag in self.get_tags_with_name(cluster.name)]
        cluster.configuration = {}

        self.aws_api.provision_ecs_cluster(cluster)
        return cluster

    def provision_container_instance_auto_scaling_group(self, launch_template):
        """
        Provision the container instance auto-scaling group.

        :param launch_template:
        :return:
        """

        as_group = AutoScalingGroup({})
        as_group.name = self.configuration.container_instance_auto_scaling_group_name
        as_group.region = self.region
        region_objects = self.aws_api.autoscaling_client.get_region_auto_scaling_groups(as_group.region,
                                                                                        names=[as_group.name])

        if len(region_objects) > 1:
            raise RuntimeError(f"more there one as_group '{as_group.name}'")

        if region_objects and region_objects[0].get_status() == region_objects[0].Status.ACTIVE:
            as_group.desired_capacity = 1
            as_group.min_size = 1
        else:
            # was 0
            as_group.min_size = self.configuration.container_instance_auto_scaling_group_min_size
            as_group.desired_capacity = self.configuration.container_instance_auto_scaling_group_min_size

        as_group.tags = self.get_tags_with_name(as_group.name)
        as_group.launch_template = {
            "LaunchTemplateId": launch_template.id,
            "Version": "$Default"
        }
        as_group.max_size = self.configuration.container_instance_auto_scaling_group_max_size
        as_group.default_cooldown = 300

        as_group.health_check_type = "EC2"
        as_group.health_check_grace_period = 300
        as_group.vpc_zone_identifier = ",".join([subnet.id for subnet in self.private_subnets])
        as_group.termination_policies = [
            "Default"
        ]
        as_group.new_instances_protected_from_scale_in = False
        as_group.service_linked_role_arn = f"arn:aws:iam::{self.aws_api.ec2_client.account_id}:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling"
        self.aws_api.provision_auto_scaling_group(as_group)
        return as_group

    def provision_ecs_capacity_provider(self, auto_scaling_group):
        """
        Create capacity provider from provision instances.

        :param auto_scaling_group:
        :return:
        """
        capacity_provider = ECSCapacityProvider({})
        capacity_provider.name = self.configuration.container_instance_capacity_provider_name
        capacity_provider.tags = [{key.lower(): value for key, value in dict_tag.items()} for dict_tag in
                                  self.get_tags_with_name(capacity_provider.name)]
        capacity_provider.region = self.region

        capacity_provider.auto_scaling_group_provider = {
            "autoScalingGroupArn": auto_scaling_group.arn,
            "managedScaling": {
                "status": "DISABLED",
                "targetCapacity": 70,
                "minimumScalingStepSize": 1,
                "maximumScalingStepSize": 10000,
                "instanceWarmupPeriod": 300
            },
            "managedTerminationProtection": "DISABLED"
        }

        self.aws_api.provision_ecs_capacity_provider(capacity_provider)

        return capacity_provider

    def attach_capacity_provider_to_ecs_cluster(self, ecs_cluster):
        """
        Attach provisioned instances to this cluster.

        :param ecs_cluster:
        :return:
        """

        default_capacity_provider_strategy = [
            {
                "capacityProvider": self.configuration.container_instance_capacity_provider_name,
                "weight": 1,
                "base": 0
            }
        ]
        self.aws_api.attach_capacity_providers_to_ecs_cluster(ecs_cluster, [
            self.configuration.container_instance_capacity_provider_name], default_capacity_provider_strategy)

        return True

    def dispose_ecs_cluster_capacity_provider(self):
        """
        Dispose capacitu
        :return:
        """
        capacity_provider = ECSCapacityProvider({})
        capacity_provider.region = self.region
        capacity_provider.name = self.configuration.container_instance_capacity_provider_name
        self.aws_api.ecs_client.dispose_capacity_provider(capacity_provider)
        return True

    def dispose_container_instance_auto_scaling_group(self):
        """
        Dispose auto scaling group.

        :return:
        """

        as_group = AutoScalingGroup({})
        as_group.name = self.configuration.container_instance_auto_scaling_group_name
        as_group.region = self.region
        if not self.aws_api.autoscaling_client.update_auto_scaling_group_information(as_group):
            return True
        self.aws_api.autoscaling_client.dispose_auto_scaling_group(as_group)

        return True

    def dispose_ecs_cluster(self):
        """
        Dispose the ecs cluster.

        :return:
        """

        cluster = ECSCluster({"name": self.configuration.ecs_cluster_name})
        cluster.region = self.region
        if not self.aws_api.ecs_client.update_cluster_information(cluster):
            return True

        self.aws_api.ecs_client.dispose_cluster(cluster)
        return True

    def dispose_container_instance_launch_template(self):
        """
        Delete launch template

        :return:
        """

        custom_filters = {"LaunchTemplateNames": [self.configuration.container_instance_launch_template_name]}
        lts = self.aws_api.ec2_client.get_region_launch_templates(self.region, custom_filters=custom_filters)
        if not lts:
            return True

        if len(lts) > 1:
            raise ValueError(
                f"More then 1 Launch Template was not found: {self.configuration.container_instance_launch_template_name}")

        self.aws_api.ec2_client.dispose_launch_template(lts[0])
        return True

    def dispose_container_instance_security_group(self):
        """
        Delete security group.

        :return:
        """

        security_group = self.aws_api.get_security_group_by_vpc_and_name(self.vpc,
                                                                         self.configuration.container_instance_security_group_name)
        self.aws_api.ec2_client.dispose_security_groups([security_group])
        return True

    def dispose_container_instance_ssh_key(self):
        """
        After deleting you must change the key name as it is marked for deletion and can not be reused in secrets
        manager.

        :return:
        """
        self.dispose_ssh_key(self.configuration.container_instance_ssh_key_pair_name)

    def dispose_ssh_key(self, name):
        """
        Dispose the key and its private keys.

        :param name:
        :return:
        """

        key_pair = KeyPair({})
        key_pair.name = name
        key_pair.region = self.region
        if not self.aws_api.ec2_client.update_key_pair_information(key_pair):
            return True

        self.aws_api.ec2_client.dispose_key_pairs([key_pair])
        self.aws_api.secretsmanager_client.dispose_secret(f"{name}.key",
                                                          Region.get_region(self.configuration.secrets_manager_region))

        return key_pair

    def get_ubuntu22_image(self):
        """
        Get latest Ubuntu22 image in this region.

        :return:
        """

        param = self.aws_api.ssm_client.get_region_parameter(self.region,
                                                             "/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id")

        filter_request = {"ImageIds": [param.value]}
        amis = self.aws_api.ec2_client.get_region_amis(self.region, custom_filters=filter_request)
        if len(amis) != 1:
            raise RuntimeError(f"Can not find single AMI using filter: {filter_request['Filters']}")

        return amis[0]

    class OwnerError(RuntimeError):
        """
        Raised when resource owner is not Horey.

        """

    def provision_s3_bucket(self, bucket_name, statements: list):
        """
        Provision bucket.

        "s3:CreateBucket",
        "s3:PutBucketAcl",
        "s3:GetBucketWebsite",
        "s3:GetBucketPolicy",
        "s3:HeadBucket",
        "s3:ListBucket"
        "s3:PutBucketPolicy"
        "s3:GetBucketAcl"


        :return:
        """

        if self.configuration.s3_bucket_policy_statements:
            statements.extend(self.configuration.s3_bucket_policy_statements)

        s3_bucket = S3Bucket({})
        s3_bucket.region = self.region
        s3_bucket.name = bucket_name

        # s3_bucket.acl = "private" AccessControlListNotSupported
        self.aws_api.provision_s3_bucket(s3_bucket)

        if s3_bucket.upsert_statements(statements):
            self.aws_api.provision_s3_bucket(s3_bucket)

        return s3_bucket

    def provision_cloudfront_origin_access_identity(self, origin_access_identity_name):
        """
        Used to authenticate cloud-front with S3 bucket.

        "cloudfront:CreateCloudFrontOriginAccessIdentity"

        :return:
        """

        cloudfront_origin_access_identity = CloudfrontOriginAccessIdentity({})
        cloudfront_origin_access_identity.comment = origin_access_identity_name
        self.aws_api.provision_cloudfront_origin_access_identity(cloudfront_origin_access_identity)
        return cloudfront_origin_access_identity

    def provision_acm_certificate(self):
        """
        Provision certificate.

        :return:
        """

        cert = ACMCertificate({})
        cert.region = self.region
        cert.domain_name = f"*.{self.configuration.public_hosted_zone_domain_name}"
        cert.validation_method = "DNS"
        cert.tags = self.get_tags_with_name(cert.domain_name.replace("*", "star"))

        hosted_zone_name = self.configuration.public_hosted_zone_domain_name
        self.aws_api.provision_acm_certificate(cert, hosted_zone_name)
        return cert

    def provision_response_headers_policy(self):
        """
        Create headers policy.
        cloudfront:CreateResponseHeadersPolicy

        :return:
        """

        policy_config = {"Comment": "Response headers policy",
                         "Name": "",
                         "SecurityHeadersConfig": {
                             "XSSProtection": {
                                 "Override": True,
                                 "Protection": True,
                                 "ModeBlock": True,
                             },
                             "FrameOptions": {
                                 "Override": True,
                                 "FrameOption": "DENY"
                             },
                             "ReferrerPolicy": {
                                 "Override": True,
                                 "ReferrerPolicy": "same-origin"
                             },
                             "ContentTypeOptions": {
                                 "Override": True
                             },
                             "StrictTransportSecurity": {
                                 "Override": True,
                                 "IncludeSubdomains": True,
                                 "Preload": False,
                                 "AccessControlMaxAgeSec": 31536000
                             }
                         },
                         "ServerTimingHeadersConfig": {
                             "Enabled": False,
                         },
                         "RemoveHeadersConfig": {
                             "Quantity": 0,
                             "Items": []
                         }
                         }

        policy = CloudfrontResponseHeadersPolicy({})
        policy.name = self.configuration.response_headers_policy_name
        policy_config["Name"] = policy.name
        policy.response_headers_policy_config = policy_config
        self.aws_api.cloudfront_client.provision_response_headers_policy(policy)
        return policy

    # pylint: disable = (too-many-arguments
    # pylint: disable = too-many-positional-arguments
    def provision_cloudfront_distribution(self, name, aliases, cloudfront_origin_access_identity,
                                          cloudfront_certificate,
                                          s3_bucket, response_headers_policy, origin_path, web_acl=None):
        """
        Distribution with compiled NPM packages.

        "wafv2:GetWebACL",
        "wafv2:GetWebACLForResource",
        "wafv2:AssociateWebACL"

        :param name:
        :param origin_path:
        :param aliases:
        :param cloudfront_origin_access_identity:
        :param cloudfront_certificate:
        :param s3_bucket:
        :param response_headers_policy:
        :return:
        """

        comment = name
        cloudfront_distribution = CloudfrontDistribution({})
        cloudfront_distribution.comment = comment
        cloudfront_distribution.tags = self.get_tags_with_name(name)

        s3_bucket_origin_id = f"s3-bucket-{s3_bucket.name}"
        cloudfront_distribution.distribution_config = {
            "Aliases": {
                "Quantity": 1,
                "Items": aliases
            },
            "DefaultRootObject": "",
            "Origins": {
                "Quantity": 1,
                "Items": [
                    {
                        "Id": s3_bucket_origin_id,
                        "DomainName": f"{s3_bucket.name}.s3.amazonaws.com",
                        "OriginPath": origin_path,
                        "S3OriginConfig": {
                            "OriginAccessIdentity": f"origin-access-identity/cloudfront/{cloudfront_origin_access_identity.id}"
                        },
                        'CustomHeaders': {'Quantity': 0},
                        "ConnectionAttempts": 3,
                        "ConnectionTimeout": 10,
                        "OriginShield": {
                            "Enabled": False
                        }
                    }
                ]
            },
            "DefaultCacheBehavior": {
                "TargetOriginId": s3_bucket_origin_id,
                "TrustedSigners": {
                    "Enabled": False,
                    "Quantity": 0
                },
                "TrustedKeyGroups": {
                    "Enabled": False,
                    "Quantity": 0
                },
                "ViewerProtocolPolicy": "redirect-to-https",
                "AllowedMethods": {
                    "Quantity": 3,
                    "Items": [
                        "HEAD",
                        "GET",
                        "OPTIONS"
                    ],
                    "CachedMethods": {
                        "Quantity": 3,
                        "Items": [
                            "HEAD",
                            "GET",
                            "OPTIONS"
                        ]
                    }
                },
                "SmoothStreaming": False,
                "Compress": True,
                "LambdaFunctionAssociations": {
                    "Quantity": 0,
                },
                "FunctionAssociations": {
                    "Quantity": 0
                },
                "FieldLevelEncryptionId": "",
                "ResponseHeadersPolicyId": response_headers_policy.id,
                "ForwardedValues": {
                    "QueryString": False,
                    "Cookies": {
                        "Forward": "none"
                    },
                    "Headers": {
                        "Quantity": 0
                    },
                    "QueryStringCacheKeys": {
                        "Quantity": 0
                    }
                },
                "MinTTL": 0,
                "DefaultTTL": 86400,
                "MaxTTL": 31536000
            },
            "CacheBehaviors": {
                "Quantity": 0
            },
            "CustomErrorResponses": {
                "Quantity": 2,
                "Items": [
                    {
                        "ErrorCode": 403,
                        "ResponsePagePath": f"{origin_path}index.html",
                        "ResponseCode": "200",
                        "ErrorCachingMinTTL": 300
                    },
                    {
                        "ErrorCode": 404,
                        "ResponsePagePath": f"{origin_path}index.html",
                        "ResponseCode": "200",
                        "ErrorCachingMinTTL": 300
                    }
                ]
            },
            "Comment": f"{cloudfront_distribution.comment}",
            "Logging": {
                "Enabled": False,
                "IncludeCookies": False,
                "Bucket": "",
                "Prefix": ""
            },
            "PriceClass": "PriceClass_All",
            "Enabled": True,
            "ViewerCertificate": {
                "ACMCertificateArn": cloudfront_certificate.arn,
                "SSLSupportMethod": "sni-only",
                "MinimumProtocolVersion": "TLSv1.2_2021",
                "Certificate": cloudfront_certificate.arn,
                "CertificateSource": "acm"
            },
            "Restrictions": {
                "GeoRestriction": {
                    "RestrictionType": "none",
                    "Quantity": 0
                }
            },
            "WebACLId": web_acl.arn if web_acl else None,
            "HttpVersion": "http2",
            "IsIPV6Enabled": True,
        }

        self.aws_api.provision_cloudfront_distribution(cloudfront_distribution)
        return cloudfront_distribution

    def provision_public_dns_address(self, dns_address, record_address):
        """
        Provision record.

        :param dns_address:
        :param record_address:
        :return:
        """

        hosted_zone = HostedZone({})
        hosted_zone.name = self.configuration.public_hosted_zone_domain_name

        dict_record = {
            "Name": dns_address,
            "Type": "CNAME",
            "TTL": 300,
            "ResourceRecords": [
                {
                    "Value": record_address
                }
            ]}

        record = HostedZone.Record(dict_record)
        hosted_zone.records.append(record)

        self.aws_api.route53_client.provision_hosted_zone(hosted_zone, declarative=False)
        return hosted_zone

    def provision_wafv2_web_acl(self, ip_set_name, permitted_addresses, web_acl_name):
        """
        Provision ip set and WAFv2 web acl
        :return:
        """

        ip_set = WAFV2IPSet({"Name": ip_set_name,
                             "Scope": "CLOUDFRONT",
                             "Description": ip_set_name,
                             "IPAddressVersion": "IPV4",
                             "Addresses": permitted_addresses})
        ip_set.region = self.region
        ip_set.tags = self.get_tags_with_name(ip_set.name)
        self.aws_api.wafv2_client.provision_ip_set(ip_set)

        web_acl = WAFV2WebACL({"Name": web_acl_name,
                               "Scope": "CLOUDFRONT",
                               "Description": web_acl_name,
                               "DefaultAction": {'Block': {}},
                               "Rules": [{'Name': 'test', 'Priority': 0, 'Statement': {'IPSetReferenceStatement': {
                                   'ARN': ip_set.arn}},
                                          'Action': {'Allow': {}},
                                          'VisibilityConfig': {'SampledRequestsEnabled': True,
                                                               'CloudWatchMetricsEnabled': True,
                                                               'MetricName': 'test'}}],
                               "VisibilityConfig": {'SampledRequestsEnabled': True,
                                                    'CloudWatchMetricsEnabled': True,
                                                    'MetricName': web_acl_name},
                               })
        web_acl.region = self.region
        web_acl.tags = self.get_tags_with_name(web_acl.name)
        self.aws_api.wafv2_client.provision_web_acl(web_acl)
        return web_acl

    def get_prefix_list(self, pl_name):
        """
        Find managed prefix list in this environment by name.

        :param pl_name:
        :return:
        """

        return self.aws_api.ec2_client.get_managed_prefix_list(self.region, name=pl_name)

    # pylint: disable = (too-many-arguments
    # pylint: disable = too-many-positional-arguments
    def upload_to_s3(self, directory_path, bucket_name, key_path, tag_objects=True, keep_src_object_name=True):
        """
        Upload to S3.

        :param directory_path:
        :param bucket_name:
        :param tag_objects:
        :param keep_src_object_name:
        :return:
        """

        def metadata_callback_func(file_path):
            """
            Add metadata according to file name.

            :param file_path:
            :return:
            """

            extensions_mapping = {"js": {"ContentType": "application/javascript"},
                                  "json": {"ContentType": "application/json"},
                                  "svg": {"ContentType": "image/svg+xml"},
                                  "woff": {"ContentType": "font/woff"},
                                  "woff2": {"ContentType": "font/woff2"},
                                  "ttf": {"ContentType": "font/ttf"},
                                  "html": {"ContentType": "text/html"},
                                  "ico": {"ContentType": "image/vnd.microsoft.icon"},
                                  "css": {"ContentType": "text/css"},
                                  "eot": {"ContentType": "application/vnd.ms-fontobject"},
                                  "png": {"ContentType": "image/png"},
                                  "txt": {"ContentType": "text/plain"},
                                  "exe": {"ContentType": "application/x-msdownload"}
                                  }

            _, extension_string = os.path.splitext(file_path)

            try:
                return extensions_mapping[extension_string.strip(".")]
            except KeyError:
                return {"ContentType": "text/plain"}

        extra_args = {"CacheControl": "no-cache, no-store, must-revalidate",
                      "Expires": "0"
                      }
        if tag_objects:
            extra_args["Tagging"] = self.generate_artifact_tags()

        return self.aws_api.s3_client.upload(bucket_name, directory_path, key_path,
                                             keep_src_object_name=keep_src_object_name, extra_args=extra_args,
                                             metadata_callback=metadata_callback_func)

    def generate_artifact_tags(self):
        """
        Generate artifact tags.

        :return:
        """

        return "&".join(
            f'{tag["Key"]}={tag["Value"]}' for tag in self.configuration.tags) + f"&build={self.configuration.build_id}"

    def create_invalidation(self, distribution_name, paths):
        """
        Create distribution invalidations.

        :param distribution_name:
        :param paths:
        :return:
        """

        distribution = CloudfrontDistribution({})
        distribution.comment = distribution_name
        distribution.region = self.region
        distribution.tags = self.get_tags_with_name(distribution_name)

        if not self.aws_api.cloudfront_client.update_distribution_information(distribution):
            raise ValueError(f"Was not able to find distribution by comment: {distribution_name}")

        return self.aws_api.cloudfront_client.create_invalidation(distribution, paths)

    def clear_cache(self):
        """
        Clear all cache.

        :return:
        """

        self.aws_api.ec2_client.clear_cache(None, all_cache=True)

    # pylint: disable=too-many-locals
    # pylint: disable = too-many-positional-arguments
    def provision_ecs_fargate_task_definition(self, task_definition_family=None,
                                              contaner_name=None,
                                              ecr_image_id=None,
                                              port_mappings=None,
                                              cloudwatch_log_group_name=None,
                                              entry_point=None,
                                              environ_values=None,
                                              requires_compatibilities=None,
                                              network_mode=None,
                                              volumes=None,
                                              mount_points=None,
                                              ecs_task_definition_cpu_reservation=None,
                                              ecs_task_definition_memory_reservation=None,
                                              ecs_task_role_name=None,
                                              ecs_task_execution_role_name=None,
                                              task_definition_cpu_architecture=None
                                              ):
        """
        Provision task definition.

        Example 1:
        An error occurred (ClientException) when calling the RegisterTaskDefinition operation: Actual length: '514430'. Max allowed length is '65536' bytes.
        len(str(request)) = 535118
        535118 - 514430 = 20688

        Example 2 (different env vars)
        len(str(request)) = 635118
        Actual length: '614430'
        635118 - 614430 = 20688

        Need to check if other params considered in the difference and the 20688 is constant for all requests.

        :return:
        """

        if port_mappings is None:
            port_mappings = []

        ecs_task_definition = ECSTaskDefinition({})
        ecs_task_definition.region = self.region
        ecs_task_definition.family = task_definition_family

        # Why? Because AWS! `Unknown parameter in tags[0]: "Key", must be one of: key, value`
        ecs_task_definition.tags = [{key.lower(): value for key, value in dict_tag.items()} for dict_tag in
                                    self.get_tags_with_name(ecs_task_definition.family)]

        ecs_task_definition.container_definitions = [{
            "name": contaner_name,
            "portMappings": port_mappings,
            "essential": True,
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": cloudwatch_log_group_name,
                    "awslogs-region": self.configuration.region,
                    "awslogs-stream-prefix": "ecs"
                }
            }

        }
        ]

        if mount_points is not None:
            ecs_task_definition.container_definitions[0]["mountPoints"] = mount_points

        ecs_task_definition.container_definitions[0]["cpu"] = ecs_task_definition_cpu_reservation

        ecs_task_definition.container_definitions[0][
            "memoryReservation"] = ecs_task_definition_memory_reservation

        if volumes is not None:
            ecs_task_definition.volumes = volumes

        ecs_task_definition.requires_compatibilities = requires_compatibilities

        ecs_task_definition.network_mode = network_mode

        if entry_point is not None:
            ecs_task_definition.container_definitions[0]["entryPoint"] = entry_point

        ecs_task_definition.task_role_arn = self.get_iam_role(ecs_task_role_name).arn
        ecs_task_definition.execution_role_arn = self.get_iam_role(ecs_task_execution_role_name).arn

        ecs_task_definition.cpu = str(ecs_task_definition_cpu_reservation)

        ecs_task_definition.memory = str(ecs_task_definition_memory_reservation)

        ecs_task_definition.container_definitions[0]["environment"] = environ_values
        ecs_task_definition.container_definitions[0]["image"] = ecr_image_id

        ecs_task_definition.runtime_platform = {
            "cpuArchitecture": task_definition_cpu_architecture,
            "operatingSystemFamily": "LINUX"
        }

        request = ecs_task_definition.generate_create_request()
        if len(str(request)) > 65536:
            raise ValueError(f"Task definition request length {len(str(request))} while expected less then 65536")

        self.aws_api.provision_ecs_task_definition(ecs_task_definition)

        return ecs_task_definition

    def get_iam_role(self, ecs_task_role_name):
        """
        Find role by name and path.

        :param ecs_task_role_name:
        :return:
        """

        ecs_task_role = IamRole({})
        ecs_task_role.name = ecs_task_role_name
        ecs_task_role.path = f"/{self.configuration.iam_path}/"
        if not self.aws_api.iam_client.update_role_information(ecs_task_role):
            raise ValueError(f"Was not able to find role: {ecs_task_role_name} with path {self.configuration.iam_path}")
        return ecs_task_role

    # pylint: disable=too-many-locals
    # pylint: disable = too-many-positional-arguments
    def provision_ecs_service(self, cluster_name, ecs_task_definition, service_registry_dicts=None,
                              service_target_group_arn=None,
                              load_balancer_container_port=None,
                              role_arn=None, td_desired_count=1,
                              service_name=None,
                              container_name=None,
                              launch_type="EC2",
                              network_configuration=None,
                              deployment_maximum_percent=200,
                              wait_timeout=20 * 60,
                              kill_old_containers=False,
                              load_blanacer_dicts=None):
        """
        Provision component's ECS service.

        :param load_balancer_container_port:
        :param ecs_task_definition:
        :param service_registry_dicts:
        :param service_target_group_arn:
        :param role_arn:
        :param td_desired_count:
        :return:
        """
        old_tasks = self.get_ecs_service_tasks(cluster_name, ecs_task_definition) if kill_old_containers else []

        ecs_cluster = self.find_ecs_cluster(cluster_name)

        ecs_service = ECSService({})
        ecs_service.name = service_name
        ecs_service.region = self.region

        ecs_service.network_configuration = network_configuration

        ecs_service.tags = [{key.lower(): value for key, value in dict_tag.items()} for dict_tag in
                            self.get_tags_with_name(ecs_service.name)]

        ecs_service.cluster_arn = ecs_cluster.arn
        ecs_service.task_definition = ecs_task_definition.arn

        if service_target_group_arn is not None:
            if load_balancer_container_port is None:
                raise ValueError("load_balancer_container_port was not set while using service_target_group_arn")

            ecs_service.load_balancers = [{
                "targetGroupArn": service_target_group_arn,
                "containerName": container_name,
                "containerPort": load_balancer_container_port
            }]

        if service_registry_dicts is not None:
            ecs_service.service_registries = service_registry_dicts

        ecs_service.desired_count = td_desired_count

        ecs_service.launch_type = launch_type

        if role_arn is not None:
            ecs_service.role_arn = role_arn

        ecs_service.deployment_configuration = {
            "deploymentCircuitBreaker": {
                "enable": False,
                "rollback": False
            },
            "maximumPercent": deployment_maximum_percent,
            "minimumHealthyPercent": 100
        }
        if launch_type != "FARGATE":
            ecs_service.placement_strategy = [
                {
                    "type": "spread",
                    "field": "attribute:ecs.availability-zone"
                },
                {
                    "type": "spread",
                    "field": "instanceId"
                }
            ]
        ecs_service.health_check_grace_period_seconds = 10
        ecs_service.scheduling_strategy = "REPLICA"
        ecs_service.enable_ecs_managed_tags = False
        ecs_service.enable_execute_command = True
        ecs_service.load_balancers = load_blanacer_dicts
        self.aws_api.provision_ecs_service(ecs_service, wait_timeout=wait_timeout)

        if kill_old_containers:
            self.kill_old_task(cluster_name, old_tasks)
        return ecs_service

    def find_ecs_cluster(self, cluster_name):
        """
        Standard.

        :param cluster_name:
        :return:
        """

        clusters = self.aws_api.ecs_client.get_region_clusters(self.region, cluster_identifiers=[
            cluster_name])
        if len(clusters) != 1:
            raise RuntimeError(f"Can not find ecs cluster "
                               f"{cluster_name} "
                               f"found: {len(clusters)}")
        return clusters[0]

    def get_ecs_service_tasks(self, cluster_name, task_definition):
        """
        Get ECS service currently running tasks.

        :return:
        """
        custom_list_filters = {"family": task_definition.family}
        return self.aws_api.ecs_client.get_region_tasks(self.region,
                                                        cluster_name=cluster_name,
                                                        custom_list_filters=custom_list_filters)

    def kill_old_task(self, cluster_name, tasks):
        """
        Brutally kill the old task running in ECS Service.

        :return:
        """
        if len(tasks) == 0:
            return

        print("Brutally killing old tasks!")
        self.aws_api.ecs_client.dispose_tasks(tasks, cluster_name)

    def get_security_groups(self, security_group_names, single=False):
        """
        Get security groups by names.

        :param single:
        :param security_group_names:
        :return:
        """

        lst_ret = []
        for security_group_name in security_group_names:
            lst_ret.append(self.aws_api.get_security_group_by_vpc_and_name(self.vpc, security_group_name))

        if single:
            if len(lst_ret) > 1:
                raise RuntimeError(f"Expected single security group, found: {len(lst_ret)}")
            return lst_ret[0] if lst_ret else None

        return lst_ret

    def provision_sns_topic(self, sns_topic_name=None):
        """
        Provision the SNS topic

        @return:
        """

        topic = SNSTopic({})
        topic.region = self.region
        topic.name = sns_topic_name
        topic.attributes = {"DisplayName": topic.name}
        topic.tags = self.get_tags_with_name(topic.name)

        self.aws_api.provision_sns_topic(topic)

    def provision_dynamodb(self, dynamodb_table_name=None, attribute_definitions=None, key_schema=None):
        """
        :return:
        """

        table = DynamoDBTable({})
        table.name = dynamodb_table_name
        table.region = self.region
        table.billing_mode = "PAY_PER_REQUEST"
        table.attribute_definitions = attribute_definitions

        table.key_schema = key_schema

        table.tags = self.get_tags_with_name(table.name)
        self.aws_api.dynamodb_client.provision_table(table)

    def provision_sns_subscription(self, sns_topic_name=None, subscription_name=None, lambda_name=None):
        """
        Subscribe the receiving lambda to the SNS topic.

        @return:
        """

        topic = SNSTopic({})
        topic.name = sns_topic_name
        topic.region = self.region
        if not self.aws_api.sns_client.update_topic_information(topic, full_information=False):
            raise RuntimeError("Could not update topic information")

        aws_lambda = AWSLambda({})
        aws_lambda.name = lambda_name
        aws_lambda.region = self.region

        if not self.aws_api.lambda_client.update_lambda_information(
                aws_lambda, full_information=False
        ):
            raise RuntimeError("Could not update aws_lambda information")

        subscription = SNSSubscription({})
        subscription.region = self.region
        subscription.name = subscription_name
        subscription.protocol = "lambda"
        subscription.topic_arn = topic.arn
        subscription.endpoint = aws_lambda.arn
        self.aws_api.provision_sns_subscription(subscription)

    def provision_event_bridge_rule(self, aws_lambda=None, event_bridge_rule_name=None, description=None):
        """
        Event bridge rule - the trigger used to trigger the lambda each minute.

        :return:
        """

        rule = EventBridgeRule({})
        rule.name = event_bridge_rule_name
        rule.description = description
        rule.region = self.region
        rule.schedule_expression = "rate(1 minute)"
        rule.event_bus_name = "default"
        rule.state = "ENABLED"
        rule.tags = self.get_tags_with_name(rule.name)

        if aws_lambda is not None:
            target = EventBridgeTarget({})
            target.id = f"target-{aws_lambda.name}"
            target.arn = aws_lambda.arn
            rule.targets.append(target)

        self.aws_api.provision_events_rule(rule)
        return rule

    def provision_log_group(self, log_group_name=None):
        """
        Provision log group

        @return:
        """

        log_group = CloudWatchLogGroup({})
        log_group.region = self.region
        log_group.name = log_group_name
        log_group.tags = {tag["Key"]: tag["Value"] for tag in self.get_tags_with_name(log_group.name)}
        self.aws_api.provision_cloudwatch_log_group(log_group)

    # pylint: disable = too-many-positional-arguments
    def deploy_lambda(self, lambda_name=None, handler=None, timeout=None, memory_size=None, policy=None, role_name=None,
                      zip_file_path=None):
        """
        Deploy the lambda object into AWS service.

        @return:
        """

        role = self.get_iam_role(role_name)

        aws_lambda = AWSLambda({})
        aws_lambda.region = self.region
        aws_lambda.name = lambda_name
        aws_lambda.handler = handler
        aws_lambda.runtime = "python3.12"

        aws_lambda.role = role.arn
        aws_lambda.timeout = timeout
        aws_lambda.memory_size = memory_size
        aws_lambda.tags = {tag["Key"]: tag["Value"] for tag in self.get_tags_with_name(aws_lambda.name)}

        aws_lambda.policy = policy

        with open(zip_file_path, "rb") as myzip:
            aws_lambda.code = {"ZipFile": myzip.read()}
        self.aws_api.provision_aws_lambda(aws_lambda, update_code=True)

        return aws_lambda

    def get_rds_cluster(self, cluster_id):
        """
        Provision log group

        @return:
        """

        for cluster in self.aws_api.rds_client.yield_db_clusters(self.region,
                                                                 full_information=True,
                                                                 filters_req={"DBClusterIdentifier": cluster_id}):
            return cluster

        raise RuntimeError(f"Could not find cluster '{cluster_id}' in region: '{self.configuration.region}'")

    def get_cloudwatch_log_group(self, log_group_name=None):
        """
        Provision log group

        @return:
        """

        log_group = CloudWatchLogGroup({})
        log_group.region = self.region
        log_group.name = log_group_name
        if not self.aws_api.cloud_watch_logs_client.update_log_group_information(log_group):
            raise RuntimeError(f"Could not update log group information '{log_group_name}' in region '{self.configuration.region}'")
        return log_group

    def get_event_bridge_rule(self, name):
        """
        Find event bridge rule.

        :param name:
        :return:
        """
        events_rule = EventBridgeRule({})
        events_rule.name = name
        events_rule.region = self.region

        if not self.aws_api.events_client.update_rule_information(events_rule):
            raise RuntimeError("Could not update event bridge rule information")

        return events_rule

    def get_sns_topic(self, name):
        """
        Find sns topic

        :param name:
        :return:
        """

        topic = SNSTopic({})
        topic.name = name
        topic.region = self.region

        if not self.aws_api.sns_client.update_topic_information(topic, full_information=False):
            raise RuntimeError(f"Could not update topic '{name}' information")
        return topic

    # pylint: disable = too-many-positional-arguments
    def provision_iam_role(self, name=None,
                           description=None,
                           assume_role_policy_document=None,
                           managed_policies_arns=None,
                           inline_policies=None):
        """
        Provision the IAM Role.

        @return:
        """

        iam_role = IamRole({})
        iam_role.description = description
        iam_role.name = name
        iam_role.path = self.configuration.iam_path
        iam_role.max_session_duration = 12 * 60 * 60
        iam_role.assume_role_policy_document = assume_role_policy_document
        if managed_policies_arns:
            iam_role.managed_policies_arns = managed_policies_arns
        if inline_policies:
            iam_role.inline_policies = inline_policies
        iam_role.tags = self.get_tags_with_name(iam_role.name)
        self.aws_api.provision_iam_role(iam_role)
        return iam_role

    def get_dynamodb(self, name):
        """
        Get dynamodb table.

        :return:
        """

        table = DynamoDBTable({})
        table.name = name
        table.region = self.region
        if not self.aws_api.dynamodb_client.update_table_information(table):
            raise RuntimeError("Could not update DynamoDBTable information")
        return table

    def get_ses_configuration_set(self, name):
        """
        Get ses config set

        :return:
        """

        config_set = SESV2ConfigurationSet({})
        config_set.name = name
        config_set.region = self.region

        if not self.aws_api.sesv2_client.update_email_configuration_set_information(config_set):
            raise RuntimeError("Could not update ses config set information")

        return config_set

    def get_load_balancer(self, name, full_information=False):
        """
        Get ses config set

        :return:
        """

        load_balancer = LoadBalancer({})
        load_balancer.name = name
        load_balancer.region = self.region

        if not self.aws_api.elbv2_client.update_load_balancer_information(load_balancer):
            raise RuntimeError("Could not update load balancer information")
        if full_information:
            self.aws_api.elbv2_client.get_load_balancer_full_information(load_balancer)

        return load_balancer

    def get_load_balancers_target_groups(self, load_balancer_name, full_information=False):
        """
        Get ses config set

        :return:
        """

        load_balancer = self.get_load_balancer(load_balancer_name)
        target_groups = self.aws_api.elbv2_client.get_region_target_groups(self.region,
                                                                           load_balancer_arn=load_balancer.arn)
        if full_information:
            for target_group in target_groups:
                self.aws_api.elbv2_client.get_target_group_full_information(target_group)
        return target_groups

    def get_cloudwatch_metrics(self):
        """
        Get all metrics

        :return:
        """

        return list(self.aws_api.cloud_watch_client.yield_client_metrics(self.region))

    def generate_inline_policy(self, name=None, description=None, statements=None):
        """
        Generate iam inline policy.

        :param name:
        :param description:
        :param statements:
        :return:
        """

        policy = IamPolicy({})
        policy.document = {
            "Version": "2012-10-17",
            "Statement": statements
        }
        policy.name = name
        policy.description = description
        policy.tags = self.get_tags_with_name(policy.name)
        return policy

    # pylint: disable = too-many-arguments
    # pylint: disable = too-many-positional-arguments
    def provision_cloudwatch_alarm(self, name=None,
                                   insufficient_data_actions=None,
                                   metric_name=None,
                                   namespace=None,
                                   statistic=None,
                                   dimensions=None,
                                   period=None,
                                   evaluation_periods=None,
                                   datapoints_to_alarm=None,
                                   threshold=None,
                                   comparison_operator=None,
                                   treat_missing_data=None,
                                   alarm_description=None,
                                   alarm_actions=None,
                                   ok_actions=None
                                   ):
        """
        Provision cloudwatch metric Lambda errors.
        Lambda service metric shows the count of failed Lambda executions.

        :param name:
        :param insufficient_data_actions:
        :param metric_name:
        :param namespace:
        :param statistic:
        :param dimensions:
        :param period:
        :param evaluation_periods:
        :param datapoints_to_alarm:
        :param threshold:
        :param comparison_operator:
        :param treat_missing_data:
        :param alarm_description:
        :param alarm_actions:
        :param ok_actions:
        :return:
        """

        alarm = CloudWatchAlarm({})
        alarm.name = name
        alarm.actions_enabled = True
        alarm.insufficient_data_actions = insufficient_data_actions
        alarm.metric_name = metric_name
        alarm.namespace = namespace
        alarm.statistic = statistic
        alarm.dimensions = dimensions
        alarm.period = period
        alarm.evaluation_periods = evaluation_periods
        alarm.datapoints_to_alarm = datapoints_to_alarm
        alarm.threshold = threshold
        alarm.comparison_operator = comparison_operator
        alarm.treat_missing_data = treat_missing_data
        alarm.alarm_description = alarm_description
        alarm.ok_actions = ok_actions
        alarm.alarm_actions = alarm_actions
        return self.provision_cloudwatch_alarm_object(alarm)

    def provision_cloudwatch_alarm_object(self, alarm):
        """
        Provision the AWS object.

        :param alarm:
        :return:
        """

        alarm.region = self.region
        self.aws_api.cloud_watch_client.set_cloudwatch_alarm(alarm)
        return alarm

    def dispose_alarm_objects(self, alarms):
        """
        Provision the AWS object.

        :param alarms:
        :return:
        """

        for alarm in alarms:
            alarm.region = self.region

        self.aws_api.cloud_watch_client.dispose_alarms(alarms)
        return alarms

    def provision_log_group_metric_filter(self, name=None, log_group_name=None, filter_text=None):
        """
        Create/Update filter

        :param filter_text:
        :param log_group_name:
        :param name:
        :return:
        """

        metric_filter = CloudWatchLogGroupMetricFilter({})
        metric_filter.log_group_name = log_group_name
        metric_filter.name = name
        metric_filter.filter_pattern = filter_text
        metric_filter.metric_transformations = [
            {
                "metricName": metric_filter.name,
                "metricNamespace": log_group_name,
                "metricValue": "1",
            }
        ]
        metric_filter.region = self.region
        self.aws_api.cloud_watch_logs_client.provision_metric_filter(metric_filter)
        return metric_filter

    def put_cloudwatch_log_lines(self, log_group_name, lines):
        """
        Make sure the group exist and put the log lines in it.

        :param log_group_name:
        :param lines:
        :return:
        """

        log_group = self.get_cloudwatch_log_group(log_group_name)

        return self.aws_api.cloud_watch_logs_client.put_log_lines(log_group, lines)

    def trigger_cloudwatch_alarm(self, alarm, reason):
        """
        These are built in metrics. So we can not change the metric itself and must move
        one step further - set alarm state manually.

        :return:
        """

        dict_request = {"AlarmName": alarm.name,
                        "StateValue": "ALARM",
                        "StateReason": reason}
        return self.aws_api.cloud_watch_client.set_alarm_state_raw(self.region, dict_request)

    def get_cloudwatch_alarms(self):
        """
        Get all alarms in the environemnt.

        :return:
        """

        return self.aws_api.cloud_watch_client.get_all_alarms(region=self.region)

    def provision_ses_domain_email_identity(self, name=None, hosted_zone_name=None, configuration_set_name=None):
        """
        Provision and validate the identity to send emails from.

        :return:
        """

        email_identity = SESIdentity({})
        email_identity.name = name
        email_identity.region = self.region
        email_identity.configuration_set_name = configuration_set_name
        email_identity.tags = self.get_tags_with_name(email_identity.name)
        configuration_set = self.get_ses_configuration_set(configuration_set_name)

        if len(configuration_set.event_destinations) > 1:
            raise NotImplementedError(f"Can not handle multiple destinations: {configuration_set.event_destinations}")
        for event_destination in configuration_set.event_destinations:
            if "BOUNCE" in event_destination["MatchingEventTypes"]:
                email_identity.bounce_topic = event_destination["SnsDestination"]["TopicArn"]
                email_identity.headers_in_bounce_notifications_enabled = True
            if "DELIVERY" in event_destination["MatchingEventTypes"]:
                email_identity.delivery_topic = event_destination["SnsDestination"]["TopicArn"]
                email_identity.headers_in_delivery_notifications_enabled = True
            if "COMPLAINT" in event_destination["MatchingEventTypes"]:
                email_identity.complaint_topic = event_destination["SnsDestination"]["TopicArn"]
                email_identity.headers_in_complaint_notifications_enabled = True

        self.aws_api.provision_ses_domain_email_identity(email_identity,
                                                         hosted_zone_name=hosted_zone_name)
        return True

    def generate_cleanup_report(self):
        """
        Generate cleanup report

        :return:
        """

        config = AWSCleanerConfigurationPolicy()
        config.cache_dir = os.path.join(self.configuration.data_directory_path, "cache")
        config.reports_dir = os.path.join(self.configuration.data_directory_path, "reports")
        aws_cleaner = AWSCleaner(config, aws_api=self.aws_api)
        aws_cleaner.cleanup_report_lambdas()

        # aws_cleaner.init_and_cache_all_s3_bucket_objects()
        # todo: danger! self.perform_backups_cleanup()
        aws_cleaner.cleanup_report_iam_users()
        aws_cleaner.cleanup_report_ecr_images()

        aws_cleaner.cleanup_report_ecs()
        # todo: aws_cleaner.cleanup_report_elasticache()

        aws_cleaner.cleanup_report_sns()
        aws_cleaner.cleanup_report_ec2_pricing([self.region])
        # todo: aws_cleaner.cleanup_report_lambda_pricing([self.region])
        aws_cleaner.cleanup_report_ses()
        aws_cleaner.cleanup_report_security_groups()
        aws_cleaner.cleanup_report_load_balancers()
        aws_cleaner.cleanup_report_sqs()
        aws_cleaner.cleanup_report_rds()
        aws_cleaner.cleanup_report_dynamodb()
        aws_cleaner.cleanup_report_ec2_instances()
        aws_cleaner.cleanup_report_network_interfaces()
        aws_cleaner.cleanup_report_acm_certificate()
        aws_cleaner.cleanup_report_route_53_service()
        aws_cleaner.cleanup_report_ebs_volumes()
        return aws_cleaner.cleanup_report_cloudwatch()

    def perform_backups_cleanup(self):
        """
        Delete  backups

        :return:
        """
        # todo: restrict by time.
        ret = list(self.aws_api.backup_client.yield_recovery_points_raw(self.region, filters_req={"BackupVaultName": "Default"}))
        for rec_point in ret:
            self.aws_api.backup_client.delete_recovery_point_raw(self.region, {"BackupVaultName": rec_point["BackupVaultName"],
                                                                                                  "RecoveryPointArn": rec_point["RecoveryPointArn"]})

    def perform_ecs_cleanup(self, aws_cleaner):
        """
        Do the cleanup.

        :param aws_cleaner:
        :return:
        """

        report = aws_cleaner.cleanup_report_ecs()

        if report.sub_reports:
            raise NotImplementedError(report.sub_reports)

        delete_capacity_providers = []
        for action in report.actions:
            if isinstance(action, ReportActionECSCapacityProvider):
                # cap_provider = self.get_ecs_capacity_provider(action.path["name"])
                # arn = cap_provider.auto_scaling_group_provider["autoScalingGroupArn"]
                # auto_scaling_group = self.get_auto_scaling_group(arn=arn)

                if action.unused_capacity_provider:
                    raise NotImplementedError("""
                    self.aws_api.ecs_client.dispose_capacity_provider(cap_provider)
                    self.aws_api.autoscaling_client.dispose_auto_scaling_group(auto_scaling_group)
                    delete_capacity_providers.append(cap_provider)
                    continue
                    """)

                if action.unused_container_instances:
                    raise NotImplementedError("""
                    if len(auto_scaling_group.instances) - len(action.unused_container_instances) < auto_scaling_group.min_size:
                        auto_scaling_group.min_size = len(auto_scaling_group.instances) - len(action.unused_container_instances)
                        self.aws_api.autoscaling_client.provision_auto_scaling_group(auto_scaling_group)
                    self.aws_api.autoscaling_client.detach_instances(auto_scaling_group,
                                                                     action.unused_container_instances,
                                                                     decrement=True)
                    """)
            else:
                raise NotImplementedError(action.__class__.__name__)

        logger.info(f"Deleted {len(delete_capacity_providers)} capacity providers")

    def perform_cleanup(self, aws_cleaner):
        """
        Do the cleanup.

        :param aws_cleaner:
        :return:
        """

        report = aws_cleaner.cleanup_report_cloudwatch()
        for sub_report in report.sub_reports:
            if sub_report.service == "logs":
                self.perform_logs_cleanup(sub_report)
            elif sub_report.service == "cloudwatch":
                self.perform_cloudwatch_cleanup(sub_report)
            else:
                raise NotImplementedError(sub_report.service)

    def perform_cloudwatch_cleanup(self, report):
        """
        Log groups removal.

        :param report:
        :return:
        """
        delete_alarms = []

        if report.sub_reports:
            raise NotImplementedError(report.sub_reports)

        for action in report.actions:
            if isinstance(action, ReportActionCloudwatchLogGroupMetric):
                if action.no_log_group:
                    raise NotImplementedError("self.loadbalancer_dns_api_pairs")
                if action.disabled_actions_alarms:
                    raise NotImplementedError("self.loadbalancer_dns_api_pairs")
            elif isinstance(action, ReportActionCloudwatchAlarm):
                alarm = CloudWatchAlarm({})
                alarm.region = Region.get_region(action.path["arn"].split(":")[3])
                alarm.name = action.path["arn"].split(":")[-1]
                if action.no_active_actions:
                    self.aws_api.cloud_watch_client.dispose_alarms([alarm])
                if action.dimension_balckholes:
                    self.aws_api.cloud_watch_client.dispose_alarms([alarm])
            else:
                raise NotImplementedError(action.__class__.__name__)

        logger.info(f"Deleted {len(delete_alarms)} cloudwatch alarms")

    # pylint: disable = too-many-nested-blocks
    def perform_logs_cleanup(self, report):
        """
        Log groups removal.

        :param report:
        :return:
        """

        delete_log_groups = []
        for action in report.actions:
            log_group = CloudWatchLogGroup({})
            log_group.region = Region.get_region(action.path["region"])
            log_group.name = action.path["name"]
            if action.idle:
                logger.info(f"Deleting log group: {action.path}, {action.reason}")
                delete_log_groups.append(log_group)
                continue

            if action.size:
                log_group.retention_in_days = 7
                self.aws_api.cloud_watch_logs_client.provision_log_group(log_group)

            if action.no_retention:
                log_group.retention_in_days = 30
                self.aws_api.cloud_watch_logs_client.provision_log_group(log_group)

            if action.redundant_metric_filters:
                for values in action.redundant_metric_filters.values():
                    has2_values = list(filter(lambda x: "has2" in x, values))
                    if len(has2_values) > 1:
                        for value in has2_values:
                            if "errors" in value:
                                self.dispose_cloudwatch_metric_filters(log_group, [value])
                    elif len(has2_values) == 1:
                        self.dispose_cloudwatch_metric_filters(log_group,
                                                               list(filter(lambda x: "has2" not in x, values)))
                    else:
                        logger.info(f"Choose manually: {values}")

        for log_group in delete_log_groups:
            self.aws_api.cloud_watch_logs_client.dispose_log_group(log_group)
        logger.info(f"Deleted {len(delete_log_groups)} old log groups")

    def dispose_cloudwatch_metric_filters(self, log_group, filter_names):
        """
        Delete filters.

        :param log_group:
        :param filter_names:
        :return:
        """
        for name in filter_names:
            metric_filter = CloudWatchLogGroupMetricFilter({})
            metric_filter.log_group_name = log_group.name
            metric_filter.name = name
            metric_filter.region = log_group.region
            self.aws_api.cloud_watch_logs_client.dispose_metric_filter(metric_filter)

    def build_and_upload_ecr_image(self, dir_path, tags, nocache, buildargs=None):
        """
        Build and upload.

        :param buildargs:
        :param dir_path:
        :param tags:
        :param nocache:
        :return:
        """

        image = self.build_ecr_image(dir_path, tags, nocache, buildargs=buildargs)
        self.upload_ecr_image(tags)
        return image

    def upload_ecr_image(self, tags):
        """
        Standard.

        :param tags:
        :return:
        """

        try:
            self.docker_api.upload_images(tags)
        except Exception as inst_error:
            repr_inst_err = repr(inst_error)
            if "no basic auth credentials" in repr_inst_err or \
                    "Your authorization token has expired. Reauthenticate and try again" in repr_inst_err:
                ecr_repository_region = tags[0].split(".")[3]
                registry, _, _ = self.login_to_ecr_repository(Region.get_region(ecr_repository_region))
                self.docker_api.logout(registry)
                self.login_to_ecr_repository(Region.get_region(ecr_repository_region))
                self.docker_api.upload_images(tags)
            else:
                raise

    def build_ecr_image(self, dir_path, tags, nocache, buildargs=None):
        """
        Image building fails for different reasons, this function aggregates the reasons and handles them.

        :param buildargs:
        :param dir_path:
        :param tags:
        :param nocache:
        :return:
        """

        for _ in range(120):
            try:
                return self.docker_api.build(str(dir_path), tags, nocache=nocache, buildargs=buildargs, platform="linux/amd64")
            except Exception as error_inst:
                repr_error_inst = repr(error_inst)
                if "authorization token has expired" not in repr_error_inst:
                    raise

                ecr_repository_region = tags[0].split(".")[3]
                _, _, _ = self.login_to_ecr_repository(region=Region.get_region(ecr_repository_region), logout=True)
                return self.docker_api.build(str(dir_path), tags, nocache=nocache, buildargs=buildargs, platform="linux/amd64")

        raise TimeoutError("Was not able to build and image")

    def login_to_ecr_repository(self, region, logout=False):
        """
        Login or relogin

        :param region:
        :return:
        """

        logger.info(f"Login to AWS Docker Repo (ECR) in region: {region.region_mark}")
        credentials = self.aws_api.get_ecr_authorization_info(region=region)

        if len(credentials) != 1:
            raise ValueError("len(credentials) != 1")
        credentials = credentials[0]

        registry, username, password = credentials["proxy_host"], credentials["user_name"], credentials["decoded_token"]
        if logout:
            self.docker_api.logout(registry)
        self.docker_api.login(registry, username, password)
        return registry, username, password

    def download_ecr_image(self, repo, tags, copy_all_tags=False):
        """
        Build and upload.

        :param repo:
        :param tags:
        :return:
        """

        tag = tags[0]
        try:
            images = self.docker_api.pull_images(repo, tag=tag, all_tags=copy_all_tags)
        except Exception as error_inst:
            repr_error_inst = repr(error_inst)
            if "authorization token has expired" not in repr_error_inst and \
                    "no basic auth credentials" not in str(error_inst):
                raise
            ecr_repository_region = repo.split(".")[3]
            _, _, _ = self.login_to_ecr_repository(region=Region.get_region(ecr_repository_region), logout=True)
            images = self.docker_api.pull_images(repo, tag=tag, all_tags=copy_all_tags)

        try:
            image = images[0]
        except IndexError:
            return None

        if len(images) > 1:
            raise RuntimeError(
                f"Expected <= 1 docker image-tags by tag: {tag}, found: {len(images)}"
            )

        return image

    def get_ecs_capacity_provider(self, name):
        """
        Standard.

        :param name:
        :return:
        """

        cap_provider = ECSCapacityProvider({})
        cap_provider.region = self.region
        cap_provider.name = name
        if not self.aws_api.ecs_client.update_capacity_provider_information(cap_provider):
            raise ValueError(
                f"Was not able to find capacity provider {cap_provider.name} in region {self.configuration.region}")
        return cap_provider

    def get_auto_scaling_group(self, arn=None):
        """
        Standard.

        :return:
        """

        auto_scaling_group = AutoScalingGroup({})
        auto_scaling_group.region = self.region
        auto_scaling_group.arn = arn
        if not self.aws_api.autoscaling_client.update_auto_scaling_group_information(auto_scaling_group):
            raise ValueError(f"Was not able to find Autoscaling group {auto_scaling_group.arn}")
        return auto_scaling_group

    def get_instance_profile(self, profile_name):
        """
        Standard.

        :param profile_name:
        :return:
        """

        iam_instance_profile = IamInstanceProfile({})
        iam_instance_profile.name = profile_name
        iam_instance_profile.path = self.configuration.iam_path
        if not self.aws_api.iam_client.update_instance_profile_information(iam_instance_profile):
            raise ValueError(
                f"Was not able to find instance profile {profile_name} in region {self.configuration.region}")
        return iam_instance_profile

    def get_tags_with_name(self, name):
        """
        Generate a copy of tags with tag Name created. Raise Exception if exists.

        :param name:
        :return:
        """

        tags = self.configuration.tags

        for tag in tags:
            if tag["Key"] != "Name":
                continue

            if tag["Value"] == name:
                return tags

            raise ValueError(f"Setting Tag:Name to {name} failed bacuse Tag:Name exists with value: {tag['Value']}")

        tags.append({
            "Key": "Name",
            "Value": name
        })

        return tags

    def get_ec2_instance(self, update_info=True, tags_dict=None):
        """
        Find and return the EC2 instance.

        :param tags_dict:
        :param update_info:
        :return:
        """

        ec2_instances = self.get_ec2_instances(update_info=update_info, tags_dict=tags_dict)
        if len(ec2_instances) != 1:
            raise RuntimeError(f"Expected to find single instance, found: {len(ec2_instances)}")
        return ec2_instances[0]

    def get_ec2_instances(self, update_info=True, tags_dict=None):
        """
        Find and return EC2 instances.

        :param update_info:
        :param tags_dict:
        :return:
        """

        if tags_dict is None:
            raise ValueError("tags_dict is None")

        for tag_name, tag_value in tags_dict.items():
            if not isinstance(tag_value, list):
                raise ValueError(f"Tag '{tag_name}' value is not list: '{tag_value}'")

        filters = {"Filters": [{"Name": f"tag:{name}", "Values": values} for name, values in tags_dict.items()] +
                              [{"Name": "vpc-id", "Values": [self.vpc.id]}]
                   }
        ec2_instances = self.aws_api.ec2_client.get_region_instances(self.region, filters=filters, update_info=update_info)

        return ec2_instances

    class ResourceNotFoundError(RuntimeError):
        """
        Raised by APIs.

        """

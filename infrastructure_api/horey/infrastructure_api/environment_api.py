# pylint: disable = too-many-lines
"""
Standard environment maintainer.

"""
import json

from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.base_entities.region import Region
from horey.aws_api.aws_services_entities.vpc import VPC
from horey.aws_api.aws_services_entities.subnet import Subnet
from horey.aws_api.aws_services_entities.ec2_security_group import EC2SecurityGroup
from horey.aws_api.aws_services_entities.ec2_launch_template import EC2LaunchTemplate
from horey.aws_api.aws_services_entities.auto_scaling_group import AutoScalingGroup
from horey.aws_api.aws_services_entities.ecs_capacity_provider import ECSCapacityProvider
from horey.aws_api.aws_services_entities.iam_instance_profile import IamInstanceProfile
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

from horey.network.ip import IP
from horey.jenkins_api.jenkins_api import JenkinsAPI
from horey.jenkins_api.jenkins_api_configuration_policy import JenkinsAPIConfigurationPolicy


class EnvironmentAPI:
    """
    AWS VPC environment

    """

    def __init__(self, configuration: EnvironmentAPIConfigurationPolicy, aws_api: AWSAPI):
        self.aws_api = aws_api
        self.configuration = configuration
        self._vpc = None
        self._subnets = None
        self.jenkins_api = None

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
                if subnet.get_tag("Owner") != "Horey":
                    raise self.OwnerError(f"{subnet.id}")
                self._subnets.append(subnet)

        return self._subnets

    @subnets.setter
    def subnets(self, value):
        """
        Object getter

        :return:
        """

        self._subnets = value

    @property
    def public_subnets(self):
        """
        Get the public subnets.

        :return:
        """

        subnets = []

        for subnet in self.subnets:
            if "public" in subnet.get_tagname("Name"):
                generated_name = self.configuration.subnet_name_template.format(type="public",
                                                                                id=subnet.availability_zone_id)
                if subnet.get_tagname("Name") != generated_name:
                    raise ValueError(
                        f"Subnet {subnet.id} tag Name expected: {generated_name}, configured {subnet.get_tagname('Name')}")
                subnets.append(subnet)
        if len(subnets) != self.configuration.availability_zones_count:
            raise RuntimeError(
                f"Expected to find {self.configuration.availability_zones_count=} subnets, found: {len(subnets)}")

        return subnets

    @property
    def private_subnets(self):
        """
        Get the public subnets.

        :return:
        """

        subnets = []

        for subnet in self.subnets:
            if "private" in subnet.get_tagname("Name"):
                generated_name = self.configuration.subnet_name_template.format(type="private",
                                                                                id=subnet.availability_zone_id)
                if subnet.get_tagname("Name") != generated_name:
                    raise ValueError(
                        f"Subnet {subnet.id} tag Name expected: {generated_name}, configured {subnet.get_tagname('Name')}")
                subnets.append(subnet)
        if len(subnets) != self.configuration.availability_zones_count:
            raise RuntimeError(
                f"Expected to find {self.configuration.availability_zones_count=} subnets, found: {len(subnets)}")

        return subnets

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

        self.vpc.tags = self.configuration.tags
        self.vpc.tags.append({
            "Key": "Name",
            "Value": self.configuration.vpc_name
        })
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

            private_subnet_az.tags = self.configuration.tags
            private_subnet_az.tags.append({
                "Key": "Name",
                "Value": self.configuration.subnet_name_template.format(type="private",
                                                                        id=private_subnet_az.availability_zone_id)
            })
            subnets.append(private_subnet_az)

            # public
            public_subnet_az = Subnet({})
            public_subnet_az.cidr_block = public_subnet_az_cidr
            public_subnet_az.vpc_id = self.vpc.id
            public_subnet_az.availability_zone_id = availability_zone.id
            public_subnet_az.region = Region.get_region(self.configuration.region)

            public_subnet_az.tags = self.configuration.tags
            public_subnet_az.tags.append({
                "Key": "Name",
                "Value": self.configuration.subnet_name_template.format(type="public",
                                                                        id=public_subnet_az.availability_zone_id)
            })
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
        inet_gateway.tags = self.configuration.tags
        inet_gateway.tags.append({
            "Key": "Name",
            "Value": self.configuration.internet_gateway_name
        })

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

            route_table.tags = self.configuration.tags
            route_table.tags.append({
                "Key": "Name",
                "Value": self.configuration.route_table_name_template.format(subnet=public_subnet.get_tagname())
            })

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
            elastic_address.tags = self.configuration.tags
            elastic_address.tags.append({
                "Key": "Name",
                "Value": self.configuration.nat_gateway_elastic_address_name_template.format(id=counter)
            })

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
            nat_gateway.tags = self.configuration.tags
            nat_gateway.tags.append({
                "Key": "Name",
                "Value": self.configuration.nat_gateway_name_template.format(subnet=subnet.get_tagname())
            })
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

            route_table.tags = self.configuration.tags
            route_table.tags.append({
                "Key": "Name",
                "Value": self.configuration.route_table_name_template.format(subnet=private_subnet.get_tagname())
            })

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

    def provision_security_group(self, name, ip_permissions=None):
        """
        Provision security group.

        :param ip_permissions:
        :param name:
        :return:
        """

        security_group = EC2SecurityGroup({})
        security_group.vpc_id = self.vpc.id
        security_group.name = name
        security_group.description = name
        security_group.region = self.region
        security_group.tags = self.configuration.tags
        security_group.tags.append({
            "Key": "Name",
            "Value": security_group.name
        })

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
        key_pair.tags = self.configuration.tags
        key_pair.tags.append({
            "Key": "Name",
            "Value": key_pair.name
        })

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
        launch_template.tags = self.configuration.tags
        launch_template.tags.append({
            "Key": "Name",
            "Value": launch_template.name
        })
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
        iam_role.tags = [{
            "Key": "Name",
            "Value": iam_role.name
        }]

        iam_role.path = self.configuration.iam_path
        iam_role.managed_policies_arns = ["arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"]
        self.aws_api.iam_client.provision_role(iam_role)

        iam_instance_profile = IamInstanceProfile({})
        iam_instance_profile.name = profile_name
        iam_instance_profile.path = self.configuration.iam_path
        iam_instance_profile.tags = [{
            "Key": "Name",
            "Value": iam_instance_profile.name
        }]
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
        cluster.tags = [{key.lower(): value for key, value in dict_tag.items()} for dict_tag in self.configuration.tags]
        cluster.tags.append({
            "key": "Name",
            "value": cluster.name
        })
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

        as_group.tags = self.configuration.tags
        as_group.tags.append({
            "Key": "Name",
            "Value": as_group.name
        })
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
                                  self.configuration.tags]
        capacity_provider.region = self.region
        capacity_provider.tags.append({
            "key": "Name",
            "value": capacity_provider.name
        })

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

    def provision_jenkins_api(self):
        """
        Provision Jenkins AO
        :return:
        """

        self.provision_jenkins_api_infrastructure()
        configuration = JenkinsAPIConfigurationPolicy()

        self.jenkins_api = JenkinsAPI(configuration)
        jenkins_build_directory_path = self.jenkins_api.prepare_master_build_directory(self.configuration.data_directory_path)

        self.provision_fargate_service("jenkins", jenkins_build_directory_path, service_port=8080, load_balancer_port=8080)

    def provision_fargate_service(self, service_name, build_dir, service_port=None, load_balancer_port=None):
        """
        Service provision.

        :param service_name:
        :param build_dir:
        :param service_port:
        :param load_balancer_port:
        :return:
        """
        self.docker_api.build(jenkins_master_deployment_dir, [tag], nocache=False)
        self.login_to_ecr_repository(self.region)
        self.docker_api.upload_images([tag])

    def provision_jenkins_api_infrastructure(self):
        self.provision_jenkins_load_balancer_components()

        self.configuration.generate_configuration_file(os.path.join(jenkins_master_deployment_dir, "jenkins_manager_configuration.json"))
        self.provision_cloudwatch_log_group()
        self.provision_ecs_task_execution_role()
        self.provision_ecs_task_role()
        self.provision_ecr_repository("master")
        self.provision_ecr_repository("hagent")
        sg_jenkins_lb = self.provision_security_group(f"sg_public_jenkins_load_balancer_{1}", ip_permissions=["self.address->8080"])
        self.provision_security_group(f"sg_jenkins_service_{1}", ip_permissions=["sg_jenkins_lb.id->8080"])

        self.provision_efs()

        ecs_task_definition = self.provision_ecs_task_definition(tag)
        ecs_cluster = self.provision_ecs_cluster()


    def provision_jenkins_load_balancer_components(self):

        self.provision_alb_target_group(self.configuration.load_balancer_target_group_name)

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

        s3_bucket = S3Bucket({})
        s3_bucket.region = self.region
        s3_bucket.name = bucket_name
        # s3_bucket.acl = "private"
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
        cert.tags = self.configuration.tags
        cert.tags.append({
            "Key": "name",
            "Value": cert.domain_name.replace("*", "star")
        })

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

    def provision_cloudfront_distribution(self, aliases, cloudfront_origin_access_identity,
                                          cloudfront_certificate,
                                          s3_bucket, response_headers_policy, origin_path):
        """
        Distribution with compiled NPM packages.

        "wafv2:GetWebACL",
        "wafv2:GetWebACLForResource",
        "wafv2:AssociateWebACL"

        :param origin_path:
        :param aliases:
        :param cloudfront_origin_access_identity:
        :param cloudfront_certificate:
        :param s3_bucket:
        :param response_headers_policy:
        :return:
        """

        comment = ", ".join(aliases)
        cloudfront_distribution = CloudfrontDistribution({})
        cloudfront_distribution.comment = comment
        cloudfront_distribution.tags = self.configuration.tags
        cloudfront_distribution.tags.append({
            "Key": "Name",
            "Value": aliases[0]
        })
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
            "WebACLId": "",
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

        breakpoint()
        self.aws_api.route53_client.provision_hosted_zone(hosted_zone, declarative=False)
        return hosted_zone

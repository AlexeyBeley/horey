"""
Standard environment maintainer.

"""
from horey.aws_api.solutions.environment_configuration_policy import EnvironmentConfigurationPolicy
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.base_entities.region import Region
from horey.aws_api.base_entities.aws_account import AWSAccount
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

from horey.network.ip import IP


class Environment:
    def __init__(self, configuration: EnvironmentConfigurationPolicy, aws_api: AWSAPI):
        self.aws_api = aws_api
        self.configuration = configuration
        self._vpc = None
        self._subnets = None

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
            for subnet in self.aws_api.ec2_client.yield_subnets(region=self.region, filters_req=filters_req, update_info=True):
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
                generated_name = self.configuration.subnet_name_template.format(type="public", id=subnet.availability_zone_id)
                if subnet.get_tagname("Name") != generated_name:
                    raise ValueError(f"Subnet {subnet.id} tag Name expected: {generated_name}, configured {subnet.get_tagname('Name')}")
                subnets.append(subnet)
        if len(subnets) != self.configuration.availability_zones_count:
            raise RuntimeError(f"Expected to find {self.configuration.availability_zones_count=} subnets, found: {len(subnets)}")

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
                "Value": self.configuration.subnet_name_template.format(type="private", id=private_subnet_az.availability_zone_id)
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
                "Value": self.configuration.subnet_name_template.format(type="public", id=public_subnet_az.availability_zone_id)
            })
            subnets.append(public_subnet_az)

        self.aws_api.provision_subnets(subnets)
        return subnets

    def provision_routing(self):
        """
        Provision routing tables and gateways.

        :return:
        """

        internet_gateway = self.provision_internet_gateway()

        self.provision_public_route_tables(internet_gateway)
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

    def dispose_route_tables(self):
        """
        Delete all route tables

        :return:
        """

        filters_req = {"Filters": [
            {"Name": "vpc-id", "Values": [self.vpc.id]},
        ]}
        route_tables = list(self.aws_api.ec2_client.yield_route_tables(region=self.region, update_info=True, filters_req=filters_req))
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

        igws = list(self.aws_api.ec2_client.get_region_internet_gateways(self.region, full_information=True, filters_req=filters_req))

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

    class OwnerError(RuntimeError):
        """
        Raised when resource owner is not Horey.

        """

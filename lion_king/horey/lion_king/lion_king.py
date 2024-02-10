"""
Async orchestrator

"""
import copy

from horey.h_logger import get_logger
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.aws_api.aws_services_entities.vpc import VPC
from horey.aws_api.aws_services_entities.subnet import Subnet
from horey.aws_api.base_entities.region import Region
from horey.network.ip import IP

logger = get_logger()


class LionKing:
    """
    Main class.

    """

    def __init__(self, configuration):
        self.configuration = configuration
        self._aws_api = None
        self._region = None
        self._vpc = None
        self.tags  = [{ "Key": "environment_name",
                      "Value": self.configuration.environment_name},
                      {"Key": "environment_level",
                       "Value": self.configuration.environment_level},
                      {"Key": "project_name",
                       "Value": self.configuration.project_name},
                      ]

    @property
    def aws_api(self):
        """
        AWS API used for the deployment.

        :return:
        """
        if self._aws_api is None:
            aws_api_configuration = AWSAPIConfigurationPolicy()
            aws_api_configuration.configuration_file_full_path = self.configuration.aws_api_configuration_file_full_path
            aws_api_configuration.init_from_file()
            self._aws_api = AWSAPI(aws_api_configuration)

        return self._aws_api

    @property
    def region(self):
        """
        Deployment region.

        :return:
        """

        if self._region is None:
            self._region = Region.get_region(self.configuration.region)

        return self._region

    @property
    def aws_account(self):
        """
        AWS account id.

        :return:
        """

        return self.aws_api.sts_client.get_account()

    @property
    def vpc(self):
        """
        Init vpc

        :return:
        """

        if self._vpc is None:
            filters = [{
                "Name": "tag:environment_name",
                "Values": [
                    self.configuration.environment_name
                ]
            }]

            vpcs = self.aws_api.ec2_client.get_region_vpcs(self.region, filters=filters)
            for vpc in vpcs:
                if vpc.get_tag("project_name") == self.configuration.project_name:
                    break
            else:
                raise RuntimeError(f"Can not find VPC '{self.configuration.environment_name=}' "
                                   f"'{self.configuration.project_name=}'")
            self._vpc = vpc

        return self._vpc

    def provision_vpc(self):
        """
        Provision VPC.

        :return:
        """

        vpc = VPC({})
        vpc.region = self.region
        vpc.cidr_block = self.configuration.vpc_cidr_block

        vpc.tags = copy.deepcopy(self.tags)
        vpc.tags.append({
            "Key": "Name",
            "Value": self.configuration.vpc_name
        })
        self.aws_api.provision_vpc(vpc)
        self._vpc = vpc
        return vpc

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

        vpc_cidr_address = IP(self.configuration.vpc_cidr_block)
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

            private_subnet_az.tags = copy.deepcopy(self.tags)
            private_subnet_az.tags.append({
                "Key": "Name",
                "Value": self.configuration.private_subnet_name_template.format(private_subnet_az.availability_zone_id)
            })
            subnets.append(private_subnet_az)

            # public
            public_subnet_az = Subnet({})
            public_subnet_az.cidr_block = public_subnet_az_cidr
            public_subnet_az.vpc_id = self.vpc.id
            public_subnet_az.availability_zone_id = availability_zone.id
            public_subnet_az.region = Region.get_region(self.configuration.region)

            public_subnet_az.tags = copy.deepcopy(self.tags)
            public_subnet_az.tags.append({
                "Key": "Name",
                "Value": self.configuration.public_subnet_name_template.format(public_subnet_az.availability_zone_id)
            })
            subnets.append(public_subnet_az)

        self.aws_api.provision_subnets(subnets)
        return subnets


    def dispose(self):
        """
        Dispose the project.

        :return:
        """


        all_subnets = self.aws_api.ec2_client.get_region_subnets(region=self.region)
        subnets = [subnet for subnet in all_subnets if \
                   subnet.get_tag("environment_name", ignore_missing_tag=True) == self.configuration.environment_name and \
                   subnet.get_tag("project_name", ignore_missing_tag=True) == self.configuration.project_name]

        if len(subnets) != self.configuration.availability_zones_count*2:
            raise RuntimeError(f"Disposing subnets: expected:{self.configuration.availability_zones_count*2:}, found: {len(subnets)}")

        self.aws_api.ec2_client.dispose_subnets(subnets)

        vpc = VPC({})
        vpc.region = self.region
        vpc.cidr_block = self.configuration.vpc_cidr_block
        vpc.tags = copy.deepcopy(self.tags)
        vpc.tags.append({
            "Key": "Name",
            "Value": self.configuration.vpc_name
        })
        self.aws_api.ec2_client.dispose_vpc(vpc)
        return True

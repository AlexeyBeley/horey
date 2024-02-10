"""
Async orchestrator

"""
import copy

from horey.h_logger import get_logger
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.aws_api.aws_services_entities.vpc import VPC
from horey.aws_api.base_entities.region import Region

logger = get_logger()


class LionKing:
    """
    Main class.

    """

    def __init__(self, configuration):
        self.configuration = configuration
        self._aws_api = None
        self._region = None
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
        return vpc

    def dispose(self):
        """
        Dispose the project.

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
        self.aws_api.ec2_client.dispose_vpc(vpc)
        return True

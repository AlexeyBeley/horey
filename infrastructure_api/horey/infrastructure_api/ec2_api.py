"""
Standard EC2 maintainer.

"""

from horey.h_logger import get_logger
from horey.aws_api.aws_services_entities.ec2_security_group import EC2SecurityGroup
logger = get_logger()


class EC2API:
    """
    Manage ECS.

    """

    def __init__(self, configuration, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

    def provision(self):
        """
        Provision ECS infrastructure.

        :return:
        """

        self.provision_security_group()

    def provision_security_group(self):
        """
        Provision log group.

        :param name:
        :return:
        """

        security_group = EC2SecurityGroup({})
        security_group.vpc_id = self.environment_api.vpc.id
        security_group.name = self.configuration.name
        security_group.description = security_group.name
        security_group.region = self.environment_api.region
        security_group.tags = self.configuration.tags
        security_group.tags.append({
            "Key": "Name",
            "Value": security_group.name
        })

        if self.configuration.ip_permissions is not None:
            security_group.ip_permissions = self.configuration.ip_permissions

        self.environment_api.aws_api.provision_security_group(security_group, provision_rules=bool(self.configuration.ip_permissions))

        return security_group

    def update(self):
        """

        :return:
        """

        breakpoint()

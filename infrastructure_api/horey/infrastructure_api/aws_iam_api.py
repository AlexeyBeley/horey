"""
Standard AWS IAM maintainer.

"""
import copy
import json

from horey.h_logger import get_logger
from horey.aws_api.aws_services_entities.iam_role import IamRole
from horey.aws_api.aws_services_entities.iam_policy import IamPolicy
logger = get_logger()


class AWSIAMAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

    def provision(self, role_policies=None):
        """
        Provision ECS infrastructure.

        :return:
        """

        self.provision_role(policies=role_policies)

    def provision_role(self, policies=None):
        """
        Provision role

        :return:
        """
        policies = policies or []
        iam_role = IamRole({})
        iam_role.name = self.configuration.role_name
        iam_role.description = self.configuration.role_name
        iam_role.path = self.environment_api.configuration.iam_path
        iam_role.max_session_duration = 12 * 60 * 60
        iam_role.assume_role_policy_document = self.configuration.assume_role_policy_document

        iam_role.tags = copy.deepcopy(self.environment_api.configuration.tags)
        iam_role.tags.append({
            "Key": "name",
            "Value": iam_role.name
        })

        iam_role.inline_policies = policies
        self.environment_api.aws_api.provision_iam_role(iam_role)
        return iam_role

    def update(self):
        """

        :return:
        """

        breakpoint()

    def get_role(self):
        """
        Update roe info.

        :return:
        """

        iam_role.name = self.configuration.role_name
        iam_role.description = self.configuration.role_name
        iam_role.path = self.environment_api.configuration.iam_path

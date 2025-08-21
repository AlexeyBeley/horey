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

    def provision_role(self, policies=None, assume_role_policy=None, managed_policies_arns=None, role_name=None, description=None):
        """
        Provision role

        :return:
        """

        policies = policies or []
        managed_policies_arns = managed_policies_arns or []

        iam_role = IamRole({})
        iam_role.name = role_name or self.configuration.role_name
        iam_role.description = description or iam_role.name
        iam_role.path = self.environment_api.configuration.iam_path
        iam_role.max_session_duration = 12 * 60 * 60
        iam_role.assume_role_policy_document = assume_role_policy

        iam_role.tags = copy.deepcopy(self.environment_api.configuration.tags)
        iam_role.tags.append({
            "Key": "name",
            "Value": iam_role.name
        })

        iam_role.inline_policies = policies
        iam_role.managed_policies_arns = managed_policies_arns
        self.environment_api.aws_api.provision_iam_role(iam_role)
        return iam_role

    def update(self):
        """

        :return:
        """

        breakpoint()

    def get_role(self):
        """
        Update role info.

        :return:
        """

        iam_role = IamRole({})
        iam_role.name = self.configuration.role_name
        iam_role.path = self.environment_api.configuration.iam_path
        if not self.environment_api.aws_api.iam_client.update_role_information(iam_role):
            raise ValueError(f"Was not able to find role: {iam_role} with path {iam_role.path}")
        return iam_role

    def generate_inline_policy(self, name, resources, actions):
        """
        Generate role inline policy

        :param name:
        :param resources:
        :param actions:
        :return:
        """

        policy = IamPolicy({})
        policy.document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": actions,
                    "Resource": resources
                }
            ]
        }
        policy.name = name
        policy.description = name
        policy.tags = self.environment_api.configuration.tags
        policy.tags.append({
            "Key": "Name",
            "Value": policy.name
        })
        return policy

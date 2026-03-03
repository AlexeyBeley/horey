"""
Standard AWS IAM maintainer.

"""
import copy
import json

from horey.aws_api.aws_services_entities.iam_instance_profile import IamInstanceProfile
from horey.h_logger import get_logger
from horey.aws_api.aws_services_entities.iam_role import IamRole
from horey.aws_api.aws_services_entities.iam_policy import IamPolicy
from horey.infrastructure_api.aws_iam_api_configuration_policy import AWSIAMAPIConfigurationPolicy

logger = get_logger()


class AWSIAMAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration: AWSIAMAPIConfigurationPolicy, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

    def provision(self, role_policies=None):
        """
        Provision ECS infrastructure.

        :return:
        """

    def provision_role(self, policies=None, assume_role_policy=None, managed_policies_arns=None, role_name=None,
                       description=None):
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

    def generate_ecr_repository_policy(self, aws_lambda=None, ecs_task_execution_role=None):
        """
        Generate ECR repo resource policy.

        :param aws_lambda:
        :param ecs_task_execution_role:
        :return:
        """

        dict_policy = {"Version": "2008-10-17",
                       "Statement": [
                           {
                               "Sid": "Deployer",
                               "Effect": "Allow",
                               "Principal": "*",
                               "Action": [
                                   "ecr:CompleteLayerUpload",
                                   "ecr:GetAuthorizationToken",
                                   "ecr:UploadLayerPart",
                                   "ecr:InitiateLayerUpload",
                                   "ecr:BatchCheckLayerAvailability",
                                   "ecr:PutImage",
                                   "ecr:BatchGetImage",
                                   "ecr:GetDownloadUrlForLayer",
                                   "ecr:GetRepositoryPolicy"
                               ]
                           }
                       ]}

        if aws_lambda:
            dict_policy["Statement"].append({"Sid": "LambdaECRImageRetrievalPolicy",
                                             "Effect": "Allow",
                                             "Principal": {"Service": "lambda.amazonaws.com"},
                                             "Action": ["ecr:BatchGetImage",
                                                        "ecr:GetDownloadUrlForLayer",
                                                        "ecr:GetRepositoryPolicy"],
                                             "Condition": {"StringLike": {
                                                 "aws:sourceArn":
                                                     f"arn:aws:lambda:{self.environment_api.configuration.region}:{self.environment_api.aws_api.ecs_client.account_id}:function:{self.configuration.lambda_name}"}}
                                             })
        if ecs_task_execution_role:
            dict_policy["Statement"].append(
                        {
                            "Sid": "AllowECSTaskExecutionRolePull",
                            "Effect": "Allow",
                            "Principal": {
                                "AWS": ecs_task_execution_role.arn
                            },
                            "Action": [
                                "ecr:GetDownloadUrlForLayer",
                                "ecr:BatchGetImage",
                                "ecr:BatchCheckLayerAvailability"
                            ]
                        }
                )

        return json.dumps(dict_policy)

    def provision_instance_profile(self, profile_name, iam_role: IamRole):
        """
        Provision EC2 instance role and profile.

        :param iam_role:
        :param profile_name:
        :return:
        """

        iam_instance_profile = IamInstanceProfile({})
        iam_instance_profile.name = profile_name
        iam_instance_profile.path = self.environment_api.configuration.iam_path
        iam_instance_profile.tags = self.environment_api.get_tags_with_name(iam_instance_profile.name)
        iam_instance_profile.roles = [{"RoleName": iam_role.name}]
        self.environment_api.aws_api.iam_client.provision_instance_profile(iam_instance_profile)
        return iam_instance_profile

"""
Access manager
"""
import json

from horey.aws_api.aws_clients.iam_client import IamInstanceProfile, IamRole
from horey.infrastructure_api.access_manager_api_configuration_policy import AccessManagerAPIConfigurationPolicy


class AccessManagerAPI:
    """
    Manage Security access

    """

    def __init__(self, configuration, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

    def provision(self):
        """
        Provision frontend.

        :return:
        """

        self.provision_s3_bucket()

    def update(self):
        """

        :return:
        """

        breakpoint()

    def provision_s3_bucket(self):
        """
        Provision the bucket.

        :return:
        """

        statement = lambda x: [
            {
                "Sid": "CloudfrontAccess",
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity {cloudfront_origin_access_identity.id}"
                },
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{self.configuration.bucket_name}/*"
            }
        ]
        statement = []
        self.environment_api.provision_s3_bucket(self.configuration.bucket_name, statement)

    def provision_instance_profile(self, name, role):
        """
        Provision bastion IAM role and instance profile.

        :return:
        """

        iam_instance_profile = IamInstanceProfile({})
        iam_instance_profile.name = name
        iam_instance_profile.path = self.environment_api.configuration.iam_path
        iam_instance_profile.tags = self.environment_api.configuration.tags
        iam_instance_profile.tags.append({
            "Key": "Name",
            "Value": iam_instance_profile.name
        })

        iam_instance_profile.roles = [{"RoleName": role.name}]
        self.environment_api.aws_api.iam_client.provision_instance_profile(iam_instance_profile)
        return iam_instance_profile

    def provision_role(self, name, inline_policies=None, description=None, assume_role_policy=None):
        """
        Role

        :param name:
        :return:
        """

        iam_role = IamRole({})
        iam_role.name = name
        iam_role.assume_role_policy_document = assume_role_policy
        iam_role.description = description or name
        iam_role.max_session_duration = 3600
        iam_role.tags = self.environment_api.configuration.tags
        iam_role.tags.append({
            "Key": "name",
            "Value": iam_role.name
        })
        iam_role.path = self.environment_api.configuration.iam_path
        iam_role.inline_policies = inline_policies or []
        self.environment_api.aws_api.iam_client.provision_role(iam_role)
        return iam_role

    def get_service_assume_role_policy(self, service_name):
        """
        Generate assume role policy.

        :param service_name:
        :return:
        """

        if service_name not in ["ec2"]:
            raise NotImplementedError(service_name)

        return json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": f"{service_name}.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }, indent=4)

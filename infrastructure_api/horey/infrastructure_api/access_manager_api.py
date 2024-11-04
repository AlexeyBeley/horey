"""
Standard frontend maintainer.

"""
import os

from horey.infrastructure_api.environment_api import EnvironmentAPI
from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
from horey.aws_api.base_entities.region import Region
from horey.deployer.whatismyip import fetch_ip_from_google


class AccessManagerAPI:
    """
    Manage Frontend.

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


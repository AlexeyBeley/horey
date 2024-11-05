"""
Standard frontend maintainer.

"""
import os

from horey.infrastructure_api.environment_api import EnvironmentAPI
from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
from horey.aws_api.base_entities.region import Region
from horey.deployer.whatismyip import fetch_ip_from_google


class FrontendAPI:
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

        cloudfront_origin_access_identity = self.provision_cloudfront_origin_access_identity()
        s3_bucket = self.provision_s3_bucket(cloudfront_origin_access_identity)
        certificate = self.provision_cloudfront_acm_certificate()
        response_headers_policy = self.provision_response_headers_policy()
        cloudfront_distribution = self.provision_cloudfront_distribution(cloudfront_origin_access_identity,
                                                   certificate,
                                                   s3_bucket, response_headers_policy)

        self.environment_api.provision_public_dns_address(self.configuration.dns_address, cloudfront_distribution.domain_name)

    def update(self):
        """

        :return:
        """

        breakpoint()
        self.upload_to_s3(self.src_directory_path, self.configuration.bucket_name, self.root_key_path, self.configuration.tag_objects, self.configuration.keep_src_object_name)
        self.aws_api.cloudfront_client.create_invalidation(self.configuration.distribution_name, ["/" + self.configuration.root_key_path])

    def upload_to_s3(self, src_dir_path, bucket_name, key):
        """
        Upload the directory contents to bucket.

        :param src_dir_path:
        :param bucket:
        :param key:
        :return:
        """

        breakpoint()

    def provision_s3_bucket(self, cloudfront_origin_access_identity):
        """
        Provision the bucket.

        :return:
        """

        statements = [
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
        return self.environment_api.provision_s3_bucket(self.configuration.bucket_name, statements)

    def provision_cloudfront_origin_access_identity(self):
        """
        Used to authenticate cloud-front with S3 bucket.

        :return:
        """

        return self.environment_api.provision_cloudfront_origin_access_identity(self.configuration.cloudfront_distribution_name)

    def provision_cloudfront_acm_certificate(self):
        """
        All cloud front certificates must be created in us-east-1.

        :return:
        """

        return self.environment_api.provision_acm_certificate()

    def provision_response_headers_policy(self):
        """
        creates 2 security headers policies for:
        :return:
        """

        return self.environment_api.provision_response_headers_policy()

    def provision_cloudfront_distribution(self, cloudfront_origin_access_identity,
                                                   cloudfront_certificate,
                                                   s3_bucket, response_headers_policy):
        """
        Distribution with S3 origin.

        :param cloudfront_origin_access_identity:
        :param cloudfront_certificate:
        :param s3_bucket:
        :param response_headers_policy:
        :return:
        """

        aliases = [self.configuration.dns_address]
        return self.environment_api.provision_cloudfront_distribution(aliases, cloudfront_origin_access_identity,
                                                   cloudfront_certificate,
                                                   s3_bucket, response_headers_policy, "/public")

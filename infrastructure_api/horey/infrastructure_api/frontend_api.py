"""
Standard frontend maintainer.

"""
import os
from horey.aws_api.aws_services_entities.cloudfront_origin_access_identity import CloudfrontOriginAccessIdentity
from horey.aws_api.aws_services_entities.cloudfront_response_headers_policy import CloudfrontResponseHeadersPolicy
from horey.infrastructure_api.frontend_api_configuration_policy import FrontendAPIConfigurationPolicy


class FrontendAPI:
    """
    Manage Frontend.

    """
    def __init__(self, configuration:FrontendAPIConfigurationPolicy, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

    def provision_cloudfront(self, cloudfront_distribution_name, s3_bucket_name, dns_address):
        """
        Provision frontend.

        :return:
        """

        cloudfront_origin_access_identity = self.provision_cloudfront_origin_access_identity(cloudfront_distribution_name)
        breakpoint()
        certificate =  self.environment_api.provision_acm_certificate()


        response_headers_policy = self.provision_response_headers_policy()
        cloudfront_distribution = self.provision_cloudfront_distribution(cloudfront_origin_access_identity,
                                                   certificate,
                                                   s3_bucket, response_headers_policy)

        self.environment_api.provision_public_dns_address(self.configuration.dns_address, cloudfront_distribution.domain_name)
        return self.update()

    def update(self):
        """

        :return:
        """

        self.environment_api.upload_to_s3(self.configuration.build_directory_path, self.configuration.bucket_name, self.configuration.s3_key_path, tag_objects=True, keep_src_object_name=True)
        root_path = self.configuration.s3_key_path.rstrip("/")
        paths = [f"{root_path}/{os.path.basename(self.configuration.build_directory_path)}/*"]
        return self.environment_api.create_invalidation(self.configuration.dns_address, paths)

    def get_s3_bucket_policy(self):
        """
        Provision the bucket.

        :return:
        """

        cloudfront_origin_access_identity = ""
        self.environment_api.aws_api.cloudfront_client.update

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

    def provision_cloudfront_origin_access_identity(self, cloudfront_distribution_name):
        """
        Used to authenticate cloud-front with S3 bucket.

        :return:
        """

        cloudfront_origin_access_identity = CloudfrontOriginAccessIdentity({})
        cloudfront_origin_access_identity.comment = cloudfront_distribution_name
        self.environment_api.aws_api.cloudfront_client.provision_origin_access_identity(cloudfront_origin_access_identity)
        return cloudfront_origin_access_identity


    def provision_response_headers_policy(self):
        """
        Response security headers policy.

        :return:
        """

        policy_config = {"Comment": "Response headers policy",
                             "Name": "",
                             "SecurityHeadersConfig": {
                                 "XSSProtection": {
                                     "Override": True,
                                     "Protection": True,
                                     "ModeBlock": True,
                                 },
                                 "FrameOptions": {
                                     "Override": True,
                                     "FrameOption": "DENY"
                                 },
                                 "ReferrerPolicy": {
                                     "Override": True,
                                     "ReferrerPolicy": "same-origin"
                                 },
                                 "ContentTypeOptions": {
                                     "Override": True
                                 },
                                 "StrictTransportSecurity": {
                                     "Override": True,
                                     "IncludeSubdomains": True,
                                     "Preload": False,
                                     "AccessControlMaxAgeSec": 31536000
                                 }
                             },
                             "ServerTimingHeadersConfig": {
                                 "Enabled": False,
                             },
                             "RemoveHeadersConfig": {
                                 "Quantity": 0,
                                 "Items": []
                             }
                             }

        policy = CloudfrontResponseHeadersPolicy({})
        policy.name = self.generate_response_headers_policy_name()
        policy_config["Name"] = policy.name
        policy.response_headers_policy_config = policy_config
        self.environment_api.aws_api.cloudfront_client.provision_response_headers_policy(policy)
        return policy

    @staticmethod
    def generate_response_headers_policy_name():
        """
        Generate response headers policy name.

        :return:
        """

        return "response_headers_policy_security_base"

    def provision_wafv2_web_acl(self):
        """
        Provision WAFv2 Web ACL to restrict access to the frontend distribution.

        :return:
        """

        if not self.configuration.access_from_prefix_list:
            raise NotImplementedError("access_from_prefix_list is not set")
        prefix_list = self.environment_api.get_prefix_list(self.configuration.access_from_prefix_list)
        permitted_addresses = [entry.cidr for entry in prefix_list.entries]

        return self.environment_api.provision_wafv2_web_acl(self.configuration.ip_set_name, permitted_addresses, self.configuration.web_acl_name)

    # pylint: disable = (too-many-arguments
    def provision_cloudfront_distribution(self, cloudfront_origin_access_identity,
                                                   cloudfront_certificate,
                                                   s3_bucket, response_headers_policy,
                                          web_acl=None):
        """
        Distribution with S3 origin.

        :param web_acl:
        :param cloudfront_origin_access_identity:
        :param cloudfront_certificate:
        :param s3_bucket:
        :param response_headers_policy:
        :return:
        """

        aliases = [self.configuration.dns_address]
        return self.environment_api.provision_cloudfront_distribution(aliases[0], aliases, cloudfront_origin_access_identity,
                                                   cloudfront_certificate,
                                                   s3_bucket, response_headers_policy, "/public", web_acl=web_acl)

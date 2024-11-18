"""
Standard frontend maintainer.

"""
import os


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

        self.environment_api.clear_cache()
        self.provision_ses_identity()


        return self.environment_api.provision_public_dns_address(self.configuration.dns_address, cloudfront_distribution.domain_name)

    def update(self):
        """

        :return:
        """

        self.environment_api.upload_to_s3(self.configuration.build_directory_path, self.configuration.bucket_name, self.configuration.s3_key_path, tag_objects=True, keep_src_object_name=True)
        root_path = self.configuration.s3_key_path.rstrip("/")
        paths = [f"{root_path}/{os.path.basename(self.configuration.build_directory_path)}/*"]
        return self.environment_api.create_invalidation(self.configuration.dns_address, paths)

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
        Response security headers policy.

        :return:
        """

        return self.environment_api.provision_response_headers_policy()

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
                                          web_acl):
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

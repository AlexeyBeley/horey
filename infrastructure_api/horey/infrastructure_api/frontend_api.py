"""
Standard frontend maintainer.

"""
import os
from horey.aws_api.aws_services_entities.cloudfront_origin_access_identity import CloudfrontOriginAccessIdentity
from horey.aws_api.aws_services_entities.cloudfront_response_headers_policy import CloudfrontResponseHeadersPolicy
from horey.aws_api.aws_services_entities.s3_bucket import S3Bucket
from horey.aws_api.base_entities.region import Region
from horey.infrastructure_api.frontend_api_configuration_policy import FrontendAPIConfigurationPolicy
from horey.infrastructure_api.dns_api import DNSAPI, DNSAPIConfigurationPolicy
from horey.infrastructure_api.s3_api import S3API, S3APIConfigurationPolicy
from horey.aws_api.aws_services_entities.cloudfront_distribution import CloudfrontDistribution


class FrontendAPI:
    """
    Manage Frontend.

    """

    def __init__(self, configuration: FrontendAPIConfigurationPolicy, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

    @property
    def dns_api(self):
        configuration = DNSAPIConfigurationPolicy()
        return DNSAPI(configuration, self.environment_api)

    @property
    def s3_api(self):
        configuration = S3APIConfigurationPolicy()
        return S3API(configuration, self.environment_api)

    def provision_cloudfront(self, bucket_name, bucket_path, dns_address):
        """
        Provision frontend.

        :return:
        """

        cloudfront_distribution_name = dns_address

        cloudfront_origin_access_identity = self.provision_cloudfront_origin_access_identity(
            cloudfront_distribution_name)

        region = Region.get_region("us-east-1")
        certificate = self.environment_api.find_appropriate_certificate(dns_address, region=region)
        hosted_zone = self.dns_api.find_appropriate_hosted_zone(dns_address)
        if not certificate:
            certificate = self.environment_api.provision_acm_certificate(dns_address=dns_address,
                                                                         region=Region.get_region("us-east-1"),
                                                                         hosted_zone=hosted_zone)

        s3_bucket = self.s3_api.get_bucket(bucket_name)
        if s3_bucket is None:
            s3_bucket = S3Bucket({"Name": bucket_name})
            s3_bucket.acl = "private"
            s3_bucket.region = self.environment_api.region

            s3_bucket.policy = S3Bucket.Policy({})
            s3_bucket.policy.version = "2012-10-17"
            s3_bucket.policy.statement = [
                {
                    "Sid": "CloudfrontAccess",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": f"arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity {cloudfront_origin_access_identity.id}"
                    },
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{s3_bucket.name}/{bucket_path.strip('/')}/*"
                }
            ]
            self.s3_api.provision_bucket(s3_bucket)
        response_headers_policy = self.provision_response_headers_policy()
        cloudfront_distribution = self.provision_cloudfront_distribution([dns_address], cloudfront_origin_access_identity,
                                                                         certificate,
                                                                         s3_bucket, bucket_path, response_headers_policy)

        self.dns_api.provision_record(self.configuration.dns_address, cloudfront_distribution.domain_name, hosted_zone)
        return self.update()

    def update(self):
        """

        :return:
        """

        self.environment_api.upload_to_s3(self.configuration.build_directory_path, self.configuration.bucket_name,
                                          self.configuration.s3_key_path, tag_objects=True, keep_src_object_name=True)
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
        self.environment_api.aws_api.cloudfront_client.provision_origin_access_identity(
            cloudfront_origin_access_identity)
        return cloudfront_origin_access_identity

    def provision_response_headers_policy(self):
        """
        Response security headers policy.

        :return:
        """

        policy = CloudfrontResponseHeadersPolicy({})
        policy.name = self.generate_response_headers_policy_name()
        policy.response_headers_policy_config = {"Comment": "Response headers policy",
                                                 "Name": policy.name,
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
                                                 }, "ServerTimingHeadersConfig": {
                "Enabled": False,
            }, "RemoveHeadersConfig": {
                "Quantity": 0,
                "Items": []
            }}

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

        return self.environment_api.provision_wafv2_web_acl(self.configuration.ip_set_name, permitted_addresses,
                                                            self.configuration.web_acl_name)

    # pylint: disable = (too-many-arguments
    def provision_cloudfront_distribution(self, aliases, cloudfront_origin_access_identity,
                                          cloudfront_certificate,
                                          s3_bucket, origin_path, response_headers_policy,
                                          web_acl=None):
        """
        Distribution with S3 origin.

        :param aliases:
        :param origin_path:
        :param web_acl:
        :param cloudfront_origin_access_identity:
        :param cloudfront_certificate:
        :param s3_bucket:
        :param response_headers_policy:
        :return:
        """

        cloudfront_distribution = CloudfrontDistribution({})
        cloudfront_distribution.comment = aliases[0]
        cloudfront_distribution.tags = self.environment_api.get_tags_with_name(aliases[0])

        s3_bucket_origin_id = f"s3-bucket-{s3_bucket.name}"
        cloudfront_distribution.distribution_config = {
            "Aliases": {
                "Quantity": 1,
                "Items": aliases
            },
            "DefaultRootObject": "",
            "Origins": {
                "Quantity": 1,
                "Items": [
                    {
                        "Id": s3_bucket_origin_id,
                        "DomainName": f"{s3_bucket.name}.s3.amazonaws.com",
                        "OriginPath": origin_path,
                        "S3OriginConfig": {
                            "OriginAccessIdentity": f"origin-access-identity/cloudfront/{cloudfront_origin_access_identity.id}"
                        },
                        'CustomHeaders': {'Quantity': 0},
                        "ConnectionAttempts": 3,
                        "ConnectionTimeout": 10,
                        "OriginShield": {
                            "Enabled": False
                        }
                    }
                ]
            },
            "DefaultCacheBehavior": {
                "TargetOriginId": s3_bucket_origin_id,
                "TrustedSigners": {
                    "Enabled": False,
                    "Quantity": 0
                },
                "TrustedKeyGroups": {
                    "Enabled": False,
                    "Quantity": 0
                },
                "ViewerProtocolPolicy": "redirect-to-https",
                "AllowedMethods": {
                    "Quantity": 3,
                    "Items": [
                        "HEAD",
                        "GET",
                        "OPTIONS"
                    ],
                    "CachedMethods": {
                        "Quantity": 3,
                        "Items": [
                            "HEAD",
                            "GET",
                            "OPTIONS"
                        ]
                    }
                },
                "SmoothStreaming": False,
                "Compress": True,
                "LambdaFunctionAssociations": {
                    "Quantity": 0,
                },
                "FunctionAssociations": {
                    "Quantity": 0
                },
                "FieldLevelEncryptionId": "",
                "ResponseHeadersPolicyId": response_headers_policy.id,
                "ForwardedValues": {
                    "QueryString": False,
                    "Cookies": {
                        "Forward": "none"
                    },
                    "Headers": {
                        "Quantity": 0
                    },
                    "QueryStringCacheKeys": {
                        "Quantity": 0
                    }
                },
                "MinTTL": 0,
                "DefaultTTL": 86400,
                "MaxTTL": 31536000
            },
            "CacheBehaviors": {
                "Quantity": 0
            },
            "CustomErrorResponses": {
                "Quantity": 2,
                "Items": [
                    {
                        "ErrorCode": 403,
                        "ResponsePagePath": f"{origin_path}index.html",
                        "ResponseCode": "200",
                        "ErrorCachingMinTTL": 300
                    },
                    {
                        "ErrorCode": 404,
                        "ResponsePagePath": f"{origin_path}index.html",
                        "ResponseCode": "200",
                        "ErrorCachingMinTTL": 300
                    }
                ]
            },
            "Comment": f"{cloudfront_distribution.comment}",
            "Logging": {
                "Enabled": False,
                "IncludeCookies": False,
                "Bucket": "",
                "Prefix": ""
            },
            "PriceClass": "PriceClass_All",
            "Enabled": True,
            "ViewerCertificate": {
                "ACMCertificateArn": cloudfront_certificate.arn,
                "SSLSupportMethod": "sni-only",
                "MinimumProtocolVersion": "TLSv1.2_2021",
                "Certificate": cloudfront_certificate.arn,
                "CertificateSource": "acm"
            },
            "Restrictions": {
                "GeoRestriction": {
                    "RestrictionType": "none",
                    "Quantity": 0
                }
            },
            "HttpVersion": "http2",
            "IsIPV6Enabled": True,
        }
        if web_acl:
            cloudfront_distribution.distribution_config["WebACLId"] =  web_acl.arn
        self.environment_api.aws_api.provision_cloudfront_distribution(cloudfront_distribution)
        return cloudfront_distribution

    def create_invalidation(self, distribution_name, paths):
        """
        Create distribution invalidations.

        :param distribution_name:
        :param paths:
        :return:
        """

        distribution = CloudfrontDistribution({})
        distribution.comment = distribution_name
        distribution.region = self.environment_api.region
        distribution.tags = self.environment_api.get_tags_with_name(distribution_name)

        if not self.environment_api.aws_api.cloudfront_client.update_distribution_information(distribution):
            raise ValueError(f"Was not able to find distribution by comment: {distribution_name}")

        return self.environment_api.aws_api.cloudfront_client.create_invalidation(distribution, paths)


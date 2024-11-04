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

        self.provision_s3_bucket()
        cloudfront_origin_access_identity = self.provision_cloudfront_origin_access_identity("frontend")
        s3_bucket = self.provision_s3_bucket(cloudfront_origin_access_identity,
                                             bucket_name=self.configuration.frontend_bucket_name)

        sb_certificate = self.provision_cloudfront_us_east_1_acm_certificate()
        response_headers_policies = self.provision_response_headers_policies()
        aliases = [self.configuration.domain_name]
        self.provision_cloudfront_distribution(aliases, cloudfront_origin_access_identity,
                                                   cloudfront_certificate,
                                                   s3_bucket, response_headers_policy_id, origin_path="")

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

    def provision_cloudfront_origin_access_identity(self, origin_access_identity_name_prefix):
        """
        Used to authenticate cloud-front with S3 bucket.

        :return:
        """
        breakpoint()
        cloudfront_origin_access_identity = CloudfrontOriginAccessIdentity({})
        cloudfront_origin_access_identity.comment = f"{origin_access_identity_name_prefix}-{self.configuration.environment_name}-{self.configuration.region}"
        self.aws_api.provision_cloudfront_origin_access_identity(cloudfront_origin_access_identity)
        return cloudfront_origin_access_identity

    def provision_cloudfront_us_east_1_acm_certificate(self):
        """
        All cloud front certificates must be created in us-east-1.

        :return:
        """

        cert = ACMCertificate({})
        cert.region = Region.get_region("us-east-1")
        cert.domain_name = f"*.{self.configuration.public_hosted_zone_name}"
        cert.validation_method = "DNS"
        cert.tags = copy.deepcopy(self.tags)
        cert.tags.append({
            "Key": "name",
            "Value": cert.domain_name.replace("*", "star")
        })

        hosted_zone_name = self.configuration.public_hosted_zone_name
        self.aws_api.provision_acm_certificate(cert, hosted_zone_name)
        return cert

    def provision_response_headers_policies(self):
        """
        creates 2 security headers policies for:
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
        policy.name = self.configuration.response_headers_policy_name
        policy_config["Name"] = policy.name
        policy.response_headers_policy_config = policy_config
        self.aws_api.cloudfront_client.provision_response_headers_policy(policy)
        sb_response_headers_policy_id = policy.id

        return sb_response_headers_policy_id

    def provision_cloudfront_distribution(self, aliases, cloudfront_origin_access_identity,
                                                   cloudfront_certificate,
                                                   s3_bucket, response_headers_policy_id, origin_path=""):
        """
        Distribution with compiled NPM packages.

        :param origin_path:
        :param aliases:
        :param cloudfront_origin_access_identity:
        :param cloudfront_certificate:
        :param s3_bucket:
        :param response_headers_policy_id:
        :return:
        """

        comment = ", ".join(aliases)
        cloudfront_distribution = CloudfrontDistribution({})
        cloudfront_distribution.comment = comment
        cloudfront_distribution.tags = copy.deepcopy(self.tags)
        cloudfront_distribution.tags.append({
            "Key": "Name",
            "Value": aliases[0]
        })
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
                        "CustomHeaders": {
                            "Quantity": 1,
                            "Items": [
                                {
                                    "HeaderName": "X-SB-V",
                                    "HeaderValue": "1"
                                }
                            ]
                        },
                        "S3OriginConfig": {
                            "OriginAccessIdentity": f"origin-access-identity/cloudfront/{cloudfront_origin_access_identity.id}"
                        },
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
                "ResponseHeadersPolicyId": response_headers_policy_id,
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
                        "ResponsePagePath": "/index.html",
                        "ResponseCode": "200",
                        "ErrorCachingMinTTL": 300
                    },
                    {
                        "ErrorCode": 404,
                        "ResponsePagePath": "/index.html",
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
            "WebACLId": "",
            "HttpVersion": "http2",
            "IsIPV6Enabled": True,
        }
        self.aws_api.provision_cloudfront_distribution(cloudfront_distribution)
        return cloudfront_distribution

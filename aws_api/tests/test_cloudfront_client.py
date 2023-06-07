import os
import sys

from horey.aws_api.aws_clients.cloudfront_client import CloudfrontClient
from horey.aws_api.aws_services_entities.cloudfront_distribution import (
    CloudfrontDistribution,
)
from horey.aws_api.aws_services_entities.cloudfront_origin_access_identity import (
    CloudfrontOriginAccessIdentity,
)

import pdb
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.common_utils.common_utils import CommonUtils

from unittest.mock import Mock

configuration_values_file_full_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py"
)
logger = get_logger(
    configuration_values_file_full_path=configuration_values_file_full_path
)

accounts_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "ignore",
        "aws_api_managed_accounts.py",
    )
)

accounts = CommonUtils.load_object_from_module(accounts_file_full_path, "main")
AWSAccount.set_aws_account(accounts["1111"])
AWSAccount.set_aws_region(accounts["1111"].regions["us-west-2"])

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


def test_init_cloudfront_client():
    assert isinstance(CloudfrontClient(), CloudfrontClient)


def test_provision_origin_access_identity():
    cloudfront_client = CloudfrontClient()
    cloudfront_origin_access_identity = CloudfrontOriginAccessIdentity({})
    cloudfront_origin_access_identity.comment = "Alexey test access identity"
    cloudfront_client.provision_origin_access_identity(
        cloudfront_origin_access_identity
    )


def test_provision_distribution():
    cloudfront_client = CloudfrontClient()

    cloudfront_distribution = CloudfrontDistribution({})
    cloudfront_certificate = Mock()
    cloudfront_certificate.arn = mock_values["cloudfront_certificate.arn"]

    origin_access_identity = mock_values["origin-access-identity/cloudfront"]

    cloudfront_distribution.comment = "horey-test"

    cloudfront_distribution.tags = [
        {"Key": "Name", "Value": "horey-test"}
    ]

    cloudfront_distribution.distribution_config = {
        "Aliases": {"Quantity": 1, "Items": [mock_values["cloudfront_alias_value"]]},
        "Origins": {
            "Quantity": 1,
            "Items": [
                {
                    "Id": "horey-test-id",
                    "DomainName": "test.s3.amazonaws.com",
                    "OriginPath": "",
                    "CustomHeaders": {
                        "Quantity": 1,
                        "Items": [{"HeaderName": "X-SB-V", "HeaderValue": "1"}],
                    },
                    "S3OriginConfig": {"OriginAccessIdentity": origin_access_identity},
                    "ConnectionAttempts": 3,
                    "ConnectionTimeout": 10,
                    "OriginShield": {"Enabled": False},
                }
            ],
        },
        "DefaultCacheBehavior": {
            "TargetOriginId": "horey-test-id",
            "TrustedSigners": {"Enabled": False, "Quantity": 0},
            "TrustedKeyGroups": {"Enabled": False, "Quantity": 0},
            "ViewerProtocolPolicy": "redirect-to-https",
            "AllowedMethods": {
                "Quantity": 3,
                "Items": ["HEAD", "GET", "OPTIONS"],
                "CachedMethods": {"Quantity": 3, "Items": ["HEAD", "GET", "OPTIONS"]},
            },
            "SmoothStreaming": False,
            "Compress": True,
            "FunctionAssociations": {"Quantity": 0},
            "FieldLevelEncryptionId": "",
            "ForwardedValues": {
                "QueryString": False,
                "Cookies": {"Forward": "none"},
                "Headers": {"Quantity": 0},
                "QueryStringCacheKeys": {"Quantity": 0},
            },
            "MinTTL": 0,
            "DefaultTTL": 86400,
            "MaxTTL": 31536000,
        },
        "CustomErrorResponses": {
            "Quantity": 2,
            "Items": [
                {
                    "ErrorCode": 403,
                    "ResponsePagePath": "/index.html",
                    "ResponseCode": "200",
                    "ErrorCachingMinTTL": 300,
                },
                {
                    "ErrorCode": 404,
                    "ResponsePagePath": "/index.html",
                    "ResponseCode": "200",
                    "ErrorCachingMinTTL": 300,
                },
            ],
        },
        "Comment": "Horey test website",
        "PriceClass": "PriceClass_All",
        "Enabled": True,
        "ViewerCertificate": {
            "ACMCertificateArn": cloudfront_certificate.arn,
            "SSLSupportMethod": "sni-only",
            "MinimumProtocolVersion": "TLSv1.2_2019",
            "Certificate": cloudfront_certificate.arn,
            "CertificateSource": "acm",
        },
        "Restrictions": {"GeoRestriction": {"RestrictionType": "none", "Quantity": 0}},
        "HttpVersion": "http2",
        "IsIPV6Enabled": True,
    }

    cloudfront_client.provision_distribution(cloudfront_distribution)


if __name__ == "__main__":
    # test_provision_origin_access_identity()
    test_provision_distribution()

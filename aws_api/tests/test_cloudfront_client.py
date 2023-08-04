"""
Testing cloud front client functionality

"""
import os
import json
from unittest.mock import Mock
from unittest import TestCase

from horey.aws_api.aws_clients.cloudfront_client import CloudfrontClient
from horey.aws_api.aws_services_entities.cloudfront_distribution import (
    CloudfrontDistribution,
)
from horey.aws_api.aws_services_entities.cloudfront_function import (
    CloudfrontFunction,
)
from horey.aws_api.aws_services_entities.cloudfront_origin_access_identity import (
    CloudfrontOriginAccessIdentity,
)

from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.common_utils.common_utils import CommonUtils

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


# pylint: disable= missing-function-docstring


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
                    "Id": "s3-bucket-" + mock_values["cloudfront_origins_items_0"],
                    "DomainName": mock_values["cloudfront_origins_items_0_domain_name"],
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
            "TargetOriginId": "s3-bucket-" + mock_values["cloudfront_origins_items_0"],
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
            "LambdaFunctionAssociations": {'Quantity': 0}
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


def test_get_all_functions():
    cloudfront_client = CloudfrontClient()
    functions = cloudfront_client.get_all_functions()
    assert isinstance(functions, list)


def test_get_all_functions_full_info():
    cloudfront_client = CloudfrontClient()
    functions = cloudfront_client.get_all_functions(full_information=True)
    assert isinstance(functions, list)


def test_update_function_info():
    cloudfront_client = CloudfrontClient()
    function = Mock()
    function.name = "some-function"
    function.region = "us-east-1"
    function.stage = "DEVELOPMENT"
    assert cloudfront_client.update_function_info(function, full_information=True)


def test_update_function_info_non_existing_function():
    function = Mock()
    function.name = "some-function-non-existing"
    function.stage = "LIVE"
    function.region = "us-east-1"
    cloudfront_client = CloudfrontClient()
    assert not cloudfront_client.update_function_info(function, full_information=True)


function_to_provision = CloudfrontFunction({})
function_to_provision.name = "some-function"
function_to_provision.region = "us-west-2"
function_to_provision.function_config = {"Comment": function_to_provision.name,
                                         "Runtime": "cloudfront-js-2.0"
                                         }
function_to_provision.function_code = "function handler(event) {\n    // NOTE: This example function is for a viewer request event trigger. \n" \
                                      "    // Choose viewer request for event trigger when you associate this function with a distribution. \n " \
                                      "   var response = {\n        statusCode: 200,\n        statusDescription: 'OK',\n        headers: {\n  " \
                                      "          'cloudfront-functions': { value: 'generated-by-CloudFront-Functions-' }\n        }\n    };\n   " \
                                      " return response;\n}"


def test_provision_function_development():
    cloudfront_client = CloudfrontClient()
    function_to_provision.stage = "DEVELOPMENT"
    cloudfront_client.provision_function(function_to_provision)
    assert function_to_provision.e_tag is not None and function_to_provision.stage == "DEVELOPMENT"


def test_provision_function_update_development():
    cloudfront_client = CloudfrontClient()
    function_to_provision.function_code = "function handler(event) {\n    // NOTE: This example_2 function is for a viewer request event trigger. \n" \
                                          "    // Choose viewer request for event trigger when you associate this function with a distribution. \n" \
                                          "    var response = {\n        statusCode: 200,\n        statusDescription: 'OK',\n        headers: {\n" \
                                          "            'cloudfront-functions': { value: 'generated-by-CloudFront-Functions-' }\n        }\n    };\n" \
                                          "    return response;\n}"
    function_to_provision.stage = "DEVELOPMENT"
    cloudfront_client.provision_function(function_to_provision)
    assert function_to_provision.e_tag is not None and function_to_provision.stage == "DEVELOPMENT"

def test_provision_function_live():
    cloudfront_client = CloudfrontClient()
    function_to_provision.stage = "LIVE"
    cloudfront_client.provision_function(function_to_provision)
    assert function_to_provision.e_tag is not None and function_to_provision.stage == "LIVE"


def test_provision_function_update_live():
    cloudfront_client = CloudfrontClient()
    function_to_provision.function_code = "function handler(event) {\n    // NOTE: This example_2 function is for a viewer request event trigger. \n" \
                                          "    // Choose viewer request for event trigger when you associate this function with a distribution. \n" \
                                          "    var response = {\n        statusCode: 200,\n        statusDescription: 'OK',\n        headers: {\n" \
                                          "            'cloudfront-functions': { value: 'generated-by-CloudFront-Functions-' }\n        }\n    };\n" \
                                          "    return response;\n}"

    function_to_provision.stage = "LIVE"
    cloudfront_client.provision_function(function_to_provision)
    assert function_to_provision.e_tag is not None and function_to_provision.stage == "LIVE"

def test_dispose_function():
    cloudfront_client = CloudfrontClient()
    cloudfront_client.dispose_function(function_to_provision)


def test_test_function_live():
    event_object = {
        "version": "1.0",
        "context": {
            "eventType": "viewer-request"
        },
        "viewer": {
            "ip": "198.51.100.11"
        },
        "request": {
            "method": "GET",
            "uri": "/example.png",
            "headers": {
                "host": {"value": "example.org"}
            }
        }
    }
    cloudfront_client = CloudfrontClient()
    cloudfront_client.update_function_info(function_to_provision)
    function_to_provision.stage = "LIVE"
    ret = cloudfront_client.test_function(function_to_provision, json.dumps(event_object))
    assert json.loads(ret["FunctionOutput"])["response"]["headers"]["cloudfront-functions"]["value"] == "generated-by-CloudFront-Functions-"


def test_test_function_live_must_fail():
    class TestFunctionLiveMustFail(TestCase):
        """
        Used to check raise condition
        """

        def test_does_not_exist(self):
            with self.assertRaises(Exception) as exception_inst:
                event_object = {}
                cloudfront_client = CloudfrontClient()
                cloudfront_client.update_function_info(function_to_provision)
                function_to_provision.stage = "LIVE"
                cloudfront_client.test_function(function_to_provision, json.dumps(event_object))

            self.assertIn("NoSuchFunctionExists", repr(exception_inst.exception))

    TestFunctionLiveMustFail().test_does_not_exist()


def test_provision_function_development_deploy_bug():
    """
    Replace "return" with "return_does_not_exist"

    :return:
    """

    cloudfront_client = CloudfrontClient()
    function_to_provision.function_code = "function handler(event) {\n    // NOTE: should fail \n" \
                                          "    // Choose viewer request for event trigger when you associate this function with a distribution. \n" \
                                          "    var response = {\n        statusCode: 200,\n        statusDescription: 'OK',\n        headers: {\n" \
                                          "            'cloudfront-functions': { value: 'generated-by-CloudFront-Functions-' }\n        }\n    };\n" \
                                          "    return_does_not_exist response;\n}"
    function_to_provision.stage = "DEVELOPMENT"
    cloudfront_client.provision_function(function_to_provision)
    assert function_to_provision.e_tag is not None and function_to_provision.stage == "DEVELOPMENT"

def test_test_function_development_fail_on_bug():
    event_object = {
        "version": "1.0",
        "context": {
            "eventType": "viewer-request"
        },
        "viewer": {
            "ip": "198.51.100.11"
        },
        "request": {
            "method": "GET",
            "uri": "/example.png",
            "headers": {
                "host": {"value": "example.org"}
            }
        }
    }
    cloudfront_client = CloudfrontClient()
    cloudfront_client.update_function_info(function_to_provision)
    function_to_provision.stage = "DEVELOPMENT"
    ret = cloudfront_client.test_function(function_to_provision, json.dumps(event_object))

    assert ret.get("FunctionErrorMessage")




if __name__ == "__main__":
    # test_provision_origin_access_identity()
    # test_provision_distribution()
    test_get_all_functions()
    test_get_all_functions_full_info()
    test_update_function_info_non_existing_function()

    test_provision_function_development()
    test_test_function_live_must_fail()
    test_update_function_info()
    test_provision_function_update_development()
    test_dispose_function()

    test_provision_function_live()
    test_test_function_live()
    test_provision_function_update_live()
    test_provision_function_development_deploy_bug()
    test_test_function_development_fail_on_bug()
    test_dispose_function()

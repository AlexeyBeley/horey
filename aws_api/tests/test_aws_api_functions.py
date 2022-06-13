"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""
import json
import sys
import pdb

import pytest
import os
from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.aws_api.base_entities.region import Region
from horey.aws_api.aws_services_entities.acm_certificate import ACMCertificate
from horey.aws_api.aws_services_entities.sesv2_email_identity import SESV2EmailIdentity
from horey.aws_api.aws_services_entities.aws_lambda import AWSLambda
from horey.aws_api.aws_services_entities.lambda_event_source_mapping import LambdaEventSourceMapping
from horey.common_utils.common_utils import CommonUtils

configuration_values_file_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                   "h_logger_configuration_values.py")

logger = get_logger(configuration_values_file_full_path=configuration_values_file_full_path)

configuration = AWSAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                 "aws_api_configuration_values.py"))
configuration.init_from_file()

aws_api = AWSAPI(configuration=configuration)

mock_values_file_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"))
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


def test_add_managed_region():
    aws_api.add_managed_region(Region.get_region("us-west-2"))


def test_provision_certificate():
    cert = ACMCertificate({})
    cert.region = Region.get_region("us-east-1")
    cert.domain_name = "front.horey.com"
    cert.validation_method = "DNS"
    cert.tags = [
        {
            'Key': 'lvl',
            'Value': "tst"
        },
        {
            'Key': 'name',
            'Value': cert.domain_name.replace("*", "star")
        }
    ]

    hosted_zone_name = "horey.com"
    aws_api.provision_acm_certificate(cert, hosted_zone_name)

    assert cert.status == "ISSUED"


def test_provision_sesv2_domain_email_identity():
    email_identity = SESV2EmailIdentity({})
    email_identity.name = mock_values["email_identity.name"]
    email_identity.region = Region.get_region("us-west-2")
    email_identity.tags = [
        {
            "Key": "name",
            "Value": "value"
        }
    ]
    aws_api.provision_sesv2_domain_email_identity(email_identity)

    assert email_identity.status == "ISSUED"


def test_provision_aws_lambda_from_filelist():
    aws_lambda = AWSLambda({})
    aws_lambda.region = Region.get_region("us-west-2")
    aws_lambda.name = "horey-test-lambda"
    aws_lambda.role = mock_values["lambda:execution_role"]
    aws_lambda.handler = "lambda_test.lambda_handler"
    aws_lambda.runtime = "python3.8"
    aws_lambda.tags = {
        "lvl": "tst",
        "name": "horey-test"
    }

    files_paths = [os.path.join(os.path.dirname(os.path.abspath(__file__)), filename) for filename in
                   ["lambda_test.py", "lambda_test_2.py"]]
    aws_api.provision_aws_lambda_from_filelist(aws_lambda, files_paths, force=True)

    assert aws_lambda.state == "Active"


def test_provision_lambda_event_source_mapping():
    event_mapping = LambdaEventSourceMapping({})
    event_mapping.region = Region.get_region("us-west-2")
    event_mapping.function_identification = "horey-test-lambda"
    event_mapping.event_source_arn = mock_values["lambda_event_source_mapping:event_source_arn"]
    event_mapping.enabled = True

    aws_api.provision_lambda_event_source_mapping(event_mapping)

    assert event_mapping.state == "Enabled"


if __name__ == "__main__":
    #test_provision_certificate()
    #test_provision_aws_lambda_from_filelist()
    #test_provision_lambda_event_source_mapping()
    #test_copy_ecr_image()
    test_provision_sesv2_domain_email_identity()

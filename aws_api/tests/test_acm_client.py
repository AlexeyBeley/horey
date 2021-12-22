import os
import sys

from horey.aws_api.aws_clients.acm_client import ACMClient
from horey.aws_api.aws_services_entities.acm_certificate import ACMCertificate

import pdb
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.common_utils.common_utils import CommonUtils

from unittest.mock import Mock
configuration_values_file_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py")
logger = get_logger(configuration_values_file_full_path=configuration_values_file_full_path)

accounts_file_full_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "aws_api_managed_accounts.py"))

accounts = CommonUtils.load_object_from_module(accounts_file_full_path, "main")
AWSAccount.set_aws_account(accounts["1111"])
AWSAccount.set_aws_region(accounts["1111"].regions['us-west-2'])

mock_values_file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"))
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


def test_init_acm_client():
    assert isinstance(ACMClient(), ACMClient)


def test_provision_certificate():
    client = ACMClient()
    cert = ACMCertificate({})
    cert.region = AWSAccount.get_aws_region()

    cert.domain_name = "*.test.comp.com"
    cert.tags = [
        {
            'Key': 'lvl',
            'Value': "tst"
        }, {
            'Key': 'name',
            'Value': cert.domain_name.replace("*", "star")
        }
    ]

    cert.validation_method = "DNS"

    ret = client.provision_certificate(cert)
    pdb.set_trace()

    assert cert.arn is not None


def test_get_certificate_by_tags():
    client = ACMClient()
    domain_name = "*.test.comp.com"

    ret = client.get_certificate_by_tags(AWSAccount.get_aws_region(), {"name": domain_name.replace("*", "star")})

    assert ret is not None


if __name__ == "__main__":
    # test_register_task_definition()
    #test_provision_certificate()
    test_get_certificate_by_tags()

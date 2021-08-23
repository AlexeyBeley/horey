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


configuration_values_file_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py")

logger = get_logger(configuration_values_file_full_path=configuration_values_file_full_path)

configuration = AWSAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "aws_api_configuration_values.py"))
configuration.init_from_file()

aws_api = AWSAPI(configuration=configuration)


def test_add_managed_region():
    aws_api.add_managed_region(Region.get_region("us-west-2"))


def test_provision_certificate():
    cert = ACMCertificate({})
    cert.region = Region.get_region("us-west-2")
    cert.domain_name = "*.test.us-west-2.domain.com"
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

    hosted_zone_name = "test.us-west-2.domain.com"
    aws_api.provision_acm_certificate(cert, hosted_zone_name)

    assert cert.status == "ISSUED"


if __name__ == "__main__":
    test_provision_certificate()


import os
import sys

from horey.aws_api.aws_clients.sesv2_client import SESV2Client
from horey.aws_api.aws_services_entities.sesv2_email_template import SESV2EmailTemplate
from horey.aws_api.aws_services_entities.sesv2_email_identity import SESV2EmailIdentity
from horey.aws_api.aws_services_entities.sesv2_configuration_set import SESV2ConfigurationSet
import pdb
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.common_utils.common_utils import CommonUtils

configuration_values_file_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py")
logger = get_logger(configuration_values_file_full_path=configuration_values_file_full_path)

accounts_file_full_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "aws_api_managed_accounts.py"))

accounts = CommonUtils.load_object_from_module(accounts_file_full_path, "main")

#accounts["1111"].regions["us-east-1"] = Region.get_region("us-east-1")
#accounts["1111"].regions["eu-central-1"] = Region.get_region("eu-central-1")

AWSAccount.set_aws_account(accounts["1111"])
AWSAccount.set_aws_region(accounts["1111"].regions['us-west-2'])

mock_values_file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"))
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


def test_init_sesv2_client():
    assert isinstance(SESV2Client(), SESV2Client)


def test_provision_email_identity():
    client = SESV2Client()
    email_identity = SESV2EmailIdentity({})
    email_identity.name = mock_values["email_identity.name"]
    email_identity.region = Region.get_region("us-west-2")
    email_identity.tags = [
        {
            "Key": "name",
            "Value": "value"
        }
    ]
    client.provision_email_identity(email_identity)
    

def test_provision_email_template():
    client = SESV2Client()
    email_template = SESV2EmailTemplate({})
    email_template.name = "test"
    email_template.region = Region.get_region("us-west-2")
    email_template.template_content = {"Subject": "test_subject", "Text": "sample text"}
    client.provision_email_template(email_template)


def test_provision_configuration_set():
    client = SESV2Client()
    configuration_set = SESV2ConfigurationSet({})
    configuration_set.name = "test"
    configuration_set.region = Region.get_region("us-west-2")
    configuration_set.tracking_options = {
        "CustomRedirectDomain": mock_values["email_identity.name"]
      }
    configuration_set.reputation_options = {
        "ReputationMetricsEnabled": False
      }
    configuration_set.sending_options = {
        "SendingEnabled": True
      }
    configuration_set.tags = [
        {
            "Key": "name",
            "Value": "value"
        }
    ]
    client.provision_configuration_set(configuration_set)


if __name__ == "__main__":
    #test_init_sesv2_client()
    #test_provision_email_identity()
    #test_provision_configuration_set()
    test_provision_email_template()

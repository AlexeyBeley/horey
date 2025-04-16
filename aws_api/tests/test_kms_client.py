"""
Testing KMS client.

"""

import os

from horey.aws_api.aws_clients.kms_client import KMSClient
from horey.aws_api.aws_services_entities.kms_key import KMSKey
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.common_utils.common_utils import CommonUtils
from horey.aws_api.base_entities.region import Region

configuration_values_file_full_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py"
)
logger = get_logger(
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

# accounts["1111"].regions["us-east-1"] = Region.get_region("us-east-1")
# accounts["1111"].regions["eu-central-1"] = Region.get_region("eu-central-1")

#AWSAccount.set_aws_account(accounts["1111"])
#AWSAccount.set_aws_region(accounts["1111"].regions["us-west-2"])

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

client = KMSClient()


# pylint: disable= missing-function-docstring


def test_init_client():
    assert isinstance(KMSClient(), KMSClient)


def test_provision_key():
    key = KMSKey({})
    key.region = Region.get_region("us-west-2")
    key.name = "horey_test_key"
    key.tags = [
        {
            "TagKey": "name",
            "TagValue": key.name
        },
    ]
    key.description = "Horey Description"
    key.key_usage = "ENCRYPT_DECRYPT"
    key.aliases = [{"AliasName": "alias/AliasName1"}, {"AliasName": f"alias/{key.name}"}]
    client.provision_key(key)


def test_deprecate_key():
    key = KMSKey({})
    key.region = Region.get_region("us-west-1")
    key.name = "horey_test_key"
    key.tags = [
        {
            "TagKey": "name",
            "TagValue": key.name
        },
    ]
    key.aliases = [{"AliasName": "alias/AliasName1"}, {"AliasName": f"alias/{key.name}"}]
    client.provision_key(key)
    client.deprecate_key(key)




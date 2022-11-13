import os
import sys

from horey.aws_api.aws_clients.dynamodb_client import DynamoDBClient
from horey.aws_api.aws_services_entities.dynamodb_table import DynamoDBTable
import pdb
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
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

# accounts["1111"].regions["us-east-1"] = Region.get_region("us-east-1")
# accounts["1111"].regions["eu-central-1"] = Region.get_region("eu-central-1")

AWSAccount.set_aws_account(accounts["1111"])
AWSAccount.set_aws_region(accounts["1111"].regions["us-west-2"])

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


def test_init_dynamodb_client():
    assert isinstance(DynamoDBClient(), DynamoDBClient)


def test_provision_table():
    client = DynamoDBClient()
    table = DynamoDBTable({})
    table.name = "test"
    table.region = Region.get_region("us-west-2")
    table.attribute_definitions = [
        {"AttributeName": "attr_binary", "AttributeType": "B"},
        {"AttributeName": "attr_numeric", "AttributeType": "N"},
    ]

    table.key_schema = [
        {"AttributeName": "attr_binary", "KeyType": "HASH"},
        {"AttributeName": "attr_numeric", "KeyType": "RANGE"},
    ]

    # table.provisioned_throughput = {
    #    'ReadCapacityUnits': 5,
    #    'WriteCapacityUnits': 5
    # }

    table.billing_mode = "PAY_PER_REQUEST"
    table.stream_specification = {
        "StreamEnabled": True,
        "StreamViewType": "NEW_AND_OLD_IMAGES",
    }
    table.sse_specification = {
        "Enabled": True,
        "SSEType": "KMS",
        "KMSMasterKeyId": mock_values["table.KMSMasterKeyId"],
    }
    table.tags = [
        {"Key": "Name", "Value": "test"},
    ]

    ret = client.provision_table(table)


if __name__ == "__main__":
    test_init_dynamodb_client()
    test_provision_table()

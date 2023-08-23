"""
Testing dynamodb client
"""

import os
import pytest

from horey.aws_api.aws_clients.dynamodb_client import DynamoDBClient
from horey.aws_api.aws_services_entities.dynamodb_table import DynamoDBTable
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
        "..",
        "..",
        "ignore",
        "accounts",
        "managed_accounts.py",
    )
)

accounts = CommonUtils.load_object_from_module(accounts_file_full_path, "main")
AWSAccount.set_aws_account(accounts["dev"])

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

# pylint: disable= missing-function-docstring
@pytest.mark.skip(reason="To heavy")
def test_init_dynamodb_client():
    assert isinstance(DynamoDBClient(), DynamoDBClient)

TABLE_NAME = "test"
client = DynamoDBClient()
base_item = {"primary_key": "tet_key",
             "secondary_key": 1
             }

def test_dispose_table():
    table = DynamoDBTable({})
    table.name = TABLE_NAME
    table.region = Region.get_region("us-west-2")
    assert client.dispose_table(table)


def test_provision_table():
    table = DynamoDBTable({})
    table.name = TABLE_NAME
    table.region = Region.get_region("us-west-2")
    table.attribute_definitions = [
        {"AttributeName": "primary_key", "AttributeType": "S"},
        {"AttributeName": "secondary_key", "AttributeType": "N"},
    ]

    table.key_schema = [
        {"AttributeName": "primary_key", "KeyType": "HASH"},
        {"AttributeName": "secondary_key", "KeyType": "RANGE"},
    ]

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

    client.provision_table(table)
    assert table.id is not None

def test_update_table_information():
    table = DynamoDBTable({})
    table.name = TABLE_NAME
    table.region = Region.get_region("us-west-2")
    client.update_table_information(table)
    assert table.id is not None


item = {"primary_key": "test_primary_key",
        "secondary_key": 1,
        "builds": {"1": {"test_attribure_1": "1ab", "test_attribure_2": "2ab", "version": "1.0.0"},
                  "2": {"test_attribure_1": "2ab", "test_attribure_2": "3ab", "version": "1.0.0"}}}

dynamodbish_item = {"primary_key": {"S": "test_primary_key"},
        "secondary_key": {"N": "1"},
        "builds": {"M": {"1": {"M": {"test_attribure_1": {"S": "1ab"}, "test_attribure_2": {"S": "2ab"}, "version": {"S": "1.0.0"}}},
                         "2": {
                             "M": {"test_attribure_1": {"S": "2ab"}, "test_attribure_2": {"S": "3ab"}, "version": {"S": "1.0.0"}}}
                         }}}

def test_put_item():
    table = DynamoDBTable({})
    table.name = TABLE_NAME
    table.region = Region.get_region("us-west-2")

    assert client.put_item(table, item)


def test_get_item():
    table = DynamoDBTable({})
    table.name = TABLE_NAME
    table.region = Region.get_region("us-west-2")
    assert client.get_item(table, {"primary_key": "test_primary_key", "secondary_key": 1}) == item


def test_convert_to_dynamodbish():
    assert client.convert_to_dynamodbish(item) == dynamodbish_item


def test_convert_from_dynamodbish():
    assert client.convert_from_dynamodbish(dynamodbish_item) == item

if __name__ == "__main__":
    # test_provision_table()
    # test_put_item()
    # test_get_item()
    # test_convert_to_dynamodbish()
    # test_convert_from_dynamodbish()
    # test_init_dynamodb_client()
    # test_provision_table()
    # test_dispose_table()
    pass

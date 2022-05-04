import os
import sys

from horey.aws_api.aws_clients.glue_client import GlueClient
from horey.aws_api.aws_services_entities.glue_table import GlueTable
from horey.aws_api.aws_services_entities.glue_database import GlueDatabase
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


def test_init_glue_client():
    assert isinstance(GlueClient(), GlueClient)


def test_get_all_tables():
    client = GlueClient()
    ret = client.get_all_tables()
    assert isinstance(ret, list)


def test_get_all_databases():
    client = GlueClient()
    ret = client.get_all_databases()
    assert isinstance(ret, list)


def test_provision_database():
    client = GlueClient()
    database = GlueDatabase({})
    database.name = "test"
    database.region = Region.get_region("us-west-2")
    ret = client.provision_database(database)


def test_provision_table():
    client = GlueClient()
    table = GlueTable({})
    table.name = "test"
    table.region = Region.get_region("us-west-2")
    ret = client.provision_table(table)


if __name__ == "__main__":
    #test_init_glue_client()
    #test_get_all_databases()
    #test_get_all_tables()
    test_provision_database()
    test_provision_table()

import os
import pdb

from horey.aws_api.aws_clients.cloud_watch_client import CloudWatchClient
from horey.aws_api.aws_services_entities.cloud_watch_metric import CloudWatchMetric
from horey.aws_api.base_entities.region import Region

from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.common_utils.common_utils import CommonUtils


configuration_values_file_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py")
logger = get_logger(configuration_values_file_full_path=configuration_values_file_full_path)

accounts_file_full_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "aws_api_managed_accounts.py"))

accounts = CommonUtils.load_object_from_module(accounts_file_full_path, "main")
AWSAccount.set_aws_account(accounts["1111"])
AWSAccount.set_aws_region(accounts["1111"].regions['us-west-2'])

mock_values_file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"))
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


def test_init_client():
    assert isinstance(CloudWatchClient(), CloudWatchClient)


def test_get_region_metrics():
    client = CloudWatchClient()
    ret = client.get_region_metrics(Region.get_region("us-east-1"))
    assert isinstance(ret, list)


def test_get_region_alarms():
    client = CloudWatchClient()
    ret = client.get_all_alarms()
    assert isinstance(ret, list)


def test_provision_alert():
    pdb.set_trace()
    mock_values["arn"]


if __name__ == "__main__":
    test_init_client()
    test_get_region_metrics()
    #test_get_region_alarms()


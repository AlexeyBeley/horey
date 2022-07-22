import os
import pdb
from unittest.mock import Mock
from horey.aws_api.aws_clients.cloud_watch_logs_client import CloudWatchLogsClient
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
    assert isinstance(CloudWatchLogsClient(), CloudWatchLogsClient)


def test_get_region_log_group_metric_filters():
    client = CloudWatchLogsClient()
    ret = client.get_region_log_group_metric_filters(Region.get_region("us-east-1"))
    pdb.set_trace()
    assert isinstance(ret, list)


def test_yield_log_group_streams():
    client = CloudWatchLogsClient()
    group = Mock()
    group.region = Region.get_region("us-east-1")
    group.name = mock_values["us_east_1_cloudwatch_logs_group_name"]
    ret = []
    for stream in client.yield_log_group_streams(group):
        ret.append(stream)
    pdb.set_trace()
    assert isinstance(ret, list)


def test_yield_log_events():
    all_errors = []
    client = CloudWatchLogsClient()
    group = Mock()
    group.region = Region.get_region("eu-central-1")
    group.region = Region.get_region("us-east-1")
    group.name = mock_values["us_east_1_cloudwatch_logs_group_name"]
    ret = []
    all_streams = list(client.yield_log_group_streams(group))
    for counter_streams, stream in enumerate(all_streams):

        #if stream.name !=
        #    continue

        print(f"Stream_name: {stream.name} Streams_counter = {counter_streams}/ {len(all_streams)}")
        ret.append(stream)
        all_events = []
        for event in client.yield_log_events(group, stream):
            all_events.append(event)
            if "and its version" in event["message"]:
                all_errors.append(event["message"])
        pdb.set_trace()

    pdb.set_trace()
    min([int(x.split(" ")[-1][1:]) for x in all_errors])
    assert isinstance(ret, list)


if __name__ == "__main__":
    test_init_client()
    #test_get_region_log_group_metric_filters()
    #test_yield_log_group_streams()
    test_yield_log_events()

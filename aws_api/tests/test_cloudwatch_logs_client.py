"""
Test client.

"""
import datetime
import json
import os
from unittest.mock import Mock
from horey.aws_api.aws_clients.cloud_watch_logs_client import CloudWatchLogsClient
from horey.aws_api.base_entities.region import Region

from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
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
AWSAccount.set_aws_account(accounts["1111"])
AWSAccount.set_aws_region(accounts["1111"].regions["us-west-2"])

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


# pylint: disable= missing-function-docstring


def test_init_client():
    assert isinstance(CloudWatchLogsClient(), CloudWatchLogsClient)


def test_get_region_log_group_metric_filters():
    client = CloudWatchLogsClient()
    ret = client.get_region_log_group_metric_filters(Region.get_region("us-east-1"))
    assert isinstance(ret, list)


def test_yield_log_group_streams():
    client = CloudWatchLogsClient()
    group = Mock()
    group.region = Region.get_region("us-east-1")
    group.name = mock_values["us_east_1_cloudwatch_logs_group_name"]
    ret = []
    for stream in client.yield_log_group_streams(group):
        ret.append(stream)
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
        print(
            f"Stream_name: {stream.name} Streams_counter = {counter_streams}/ {len(all_streams)}"
        )
        ret.append(stream)
        all_events = []
        for event in client.yield_log_events(group, stream):
            all_events.append(event)
            if "and its version" in event["message"]:
                all_errors.append(event["message"])

    min(int(x.split(' ')[-1][1:]) for x in all_errors)
    assert isinstance(ret, list)


def test_save_stream_events():
    client = CloudWatchLogsClient()
    group = Mock()
    group.region = Region.get_region("us-east-1")
    group.name = mock_values["lg_name"]

    stream = Mock()
    stream.region = Region.get_region("us-east-1")
    file_path = ""

    for event in client.yield_log_events(group, stream):
        with open(file_path, "a") as fh:
            fh.write(json.dumps(event))


def test_get_region_cloud_watch_log_groups():
    client = CloudWatchLogsClient()
    ret = client.get_region_cloud_watch_log_groups("us-west-2")
    ret = client.get_region_cloud_watch_log_groups("us-east-1")
    ret = client.get_region_cloud_watch_log_groups("us-east-1")
    assert isinstance(ret, list)


def test_put_log_events_raw():
    client = CloudWatchLogsClient()
    dict_request = {"logGroupName": mock_values["logGroupName_provision_events"],
                    "logStreamName": mock_values["logStreamName_provision_events"],
                    "logEvents": [{
                        "timestamp": int(datetime.datetime.now().timestamp()*1000),
                        "message": "[ERROR]: Neo, the Horey has you!"
                    }]
                    }

    AWSAccount.set_aws_region("us-east-1")
    AWSAccount.set_aws_region("eu-central-1")
    ret = client.put_log_events_raw(dict_request)
    assert ret.get("rejectedLogEventsInfo") is None


if __name__ == "__main__":
    # test_init_client()
    # test_get_region_log_group_metric_filters()
    # test_yield_log_group_streams()
    # test_yield_log_events()
    # test_get_region_cloud_watch_log_groups()
    # test_put_log_events_raw()
    test_save_stream_events()

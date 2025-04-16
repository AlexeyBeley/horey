"""
Test client.

"""

import datetime
import json
import os
from unittest.mock import Mock

import pytest

from horey.aws_api.aws_clients.cloud_watch_logs_client import CloudWatchLogsClient
from horey.aws_api.aws_services_entities.cloud_watch_log_group import CloudWatchLogGroup
from horey.aws_api.base_entities.region import Region

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.common_utils.common_utils import CommonUtils


CloudWatchLogsClient().main_cache_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore",
            "cache"
        )
    )

# pylint: disable= missing-function-docstring

@pytest.mark.todo
def test_init_client():
    assert isinstance(CloudWatchLogsClient(), CloudWatchLogsClient)


@pytest.mark.skip
def test_get_region_log_group_metric_filters():
    client = CloudWatchLogsClient()
    ret = client.get_region_log_group_metric_filters(Region.get_region("us-east-1"))
    assert isinstance(ret, list)


@pytest.mark.skip
def test_yield_log_group_streams():
    client = CloudWatchLogsClient()
    group = Mock()
    group.region = Region.get_region("us-east-1")
    group.name = mock_values["us_east_1_cloudwatch_logs_group_name"]
    ret = []
    for stream in client.yield_log_group_streams(group):
        ret.append(stream)
    assert isinstance(ret, list)

@pytest.mark.skip
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

@pytest.mark.skip
def test_save_stream_events():
    client = CloudWatchLogsClient()
    group = Mock()
    group.region = Region.get_region("us-east-1")
    group.name = mock_values["lg_name"]

    stream = Mock()
    group.name = mock_values["lgs_name"]
    file_path = ""

    for event in client.yield_log_events(group, stream):
        with open(file_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(event)+"\n")

@pytest.mark.skip
def test_get_region_cloud_watch_log_groups():
    client = CloudWatchLogsClient()
    ret = client.get_region_cloud_watch_log_groups("us-west-2")
    ret = client.get_region_cloud_watch_log_groups("us-east-1")
    ret = client.get_region_cloud_watch_log_groups("us-east-1")
    assert isinstance(ret, list)

@pytest.mark.skip
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


log_group_name = "test-log-group"
log_stream_name = "test-stream-name"


@pytest.mark.todo
def test_provision_log_group():
    log_group = CloudWatchLogGroup({})
    log_group.name = log_group_name
    log_group.region = Region.get_region("us-west-2")
    log_group.tags = {"name": log_group.name}

    client = CloudWatchLogsClient()
    client.provision_log_group(log_group)
@pytest.mark.todo
def test_create_log_stream_raw():
    client = CloudWatchLogsClient()
    client.create_log_stream_raw({"logGroupName": log_group_name,

                                  "logStreamName": log_stream_name})
@pytest.mark.todo
def test_put_log_lines():
    client = CloudWatchLogsClient()
    log_group = CloudWatchLogGroup({})
    log_group.name = log_group_name
    log_group.region = Region.get_region("us-west-2")
    client.put_log_lines(log_group, ["test log line"])


@pytest.mark.todo
def test_yield_log_groups():
    client = CloudWatchLogsClient()
    cluster = None
    for cluster in client.yield_log_groups(region=Region.get_region("us-west-2")):
        break
    assert cluster.arn is not None


@pytest.mark.todo
def test_get_cloud_watch_log_groups_region_false():
    client = CloudWatchLogsClient()
    file_path = client.generate_cache_file_path(CloudWatchLogGroup, "us-west-2", full_information=False, get_tags=False)
    assert client.get_cloud_watch_log_groups()
    assert os.path.exists(file_path)


@pytest.mark.todo
def test_get_region_cloud_watch_log_groups_region_tags_true():
    client = CloudWatchLogsClient()
    file_path = client.generate_cache_file_path(CloudWatchLogGroup, "us-west-2", full_information=False, get_tags=True)
    assert client.get_region_cloud_watch_log_groups(Region.get_region("us-west-2"), get_tags=True)
    assert os.path.exists(file_path)


@pytest.mark.todo
def test_get_region_cloud_watch_log_groups_region_tags_false():
    client = CloudWatchLogsClient()
    file_path = client.generate_cache_file_path(CloudWatchLogGroup, "us-west-2", full_information=False, get_tags=False)
    assert client.get_region_cloud_watch_log_groups(Region.get_region("us-west-2"), get_tags=False)
    assert os.path.exists(file_path)


@pytest.mark.todo
def test_yield_log_group_metric_filters():
    client = CloudWatchLogsClient()
    obj = None
    for obj in client.yield_log_group_metric_filters(region=Region.get_region("us-west-2")):
        break
    assert obj.log_group_name is not None

@pytest.mark.todo
def test_get_cloud_watch_log_group_metric_filters_region_full_information_false():
    client = CloudWatchLogsClient()
    file_path = client.generate_cache_file_path(CloudWatchLogGroup, "us-west-2", full_information=False, get_tags=False)
    assert client.get_log_group_metric_filters()
    assert os.path.exists(file_path)

@pytest.mark.todo
def test_get_region_cloud_watch_log_group_metric_filters():
    client = CloudWatchLogsClient()
    file_path = client.generate_cache_file_path(CloudWatchLogGroup, "us-west-2", full_information=False, get_tags=False)
    assert client.get_region_log_group_metric_filters(Region.get_region("us-west-2"))
    assert os.path.exists(file_path)

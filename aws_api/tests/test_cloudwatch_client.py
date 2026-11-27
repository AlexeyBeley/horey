"""
Test cloudwatch client

"""

import os

import pytest
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm
from horey.aws_api.aws_services_entities.cloud_watch_metric import CloudWatchMetric
from horey.aws_api.aws_clients.cloud_watch_client import CloudWatchClient

CloudWatchClient().main_cache_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore",
            "cache"
        )
    )

# pylint: disable= missing-function-docstring

@pytest.mark.todo
def test_clear_cache():
    CloudWatchClient().clear_cache(CloudWatchAlarm)
    CloudWatchClient().clear_cache(CloudWatchMetric)

@pytest.mark.todo
def test_init_client():
    assert isinstance(CloudWatchClient(), CloudWatchClient)


@pytest.mark.todo
def test_get_region_metrics():
    client = CloudWatchClient()
    ret = client.get_all_metrics()
    assert isinstance(ret, list)
    assert len(ret) > 0

@pytest.mark.todo
def test_get_region_alarms():
    client = CloudWatchClient()
    ret = client.get_all_alarms()
    assert isinstance(ret, list)
    assert len(ret) > 0

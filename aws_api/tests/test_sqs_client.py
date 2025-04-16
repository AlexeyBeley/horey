"""
Test sqs client.

"""

import os
import pytest

from horey.aws_api.aws_clients.sqs_client import SQSClient
from horey.aws_api.aws_services_entities.sqs_queue import SQSQueue

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.common_utils.common_utils import CommonUtils

SQSClient().main_cache_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore",
            "cache"
        )
    )

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

# pylint: disable = missing-function-docstring

@pytest.mark.todo
def test_init_client():
    assert isinstance(SQSClient(), SQSClient)


@pytest.mark.skip
def test_provision_queue():
    client = SQSClient()
    sqs_queue = SQSQueue({})
    sqs_queue.region = AWSAccount.get_aws_region()
    sqs_queue.name = "sqs_queue_horey_test"
    sqs_queue.visibility_timeout = "30"
    sqs_queue.maximum_message_size = "262144"
    sqs_queue.message_retention_period = "604800"
    sqs_queue.delay_seconds = "0"
    sqs_queue.tags = {"name": sqs_queue.name}

    client.provision_queue(sqs_queue)
    assert sqs_queue.queue_url is not None


@pytest.mark.skip
def test_provision_queue_dlq():
    client = SQSClient()
    sqs_queue = SQSQueue({})
    sqs_queue.region = AWSAccount.get_aws_region()
    sqs_queue.name = "sqs_queue_horey_test_dlq"
    sqs_queue.visibility_timeout = "30"
    sqs_queue.maximum_message_size = "262144"
    sqs_queue.message_retention_period = "604800"
    sqs_queue.delay_seconds = "0"
    sqs_queue.tags = {"name": sqs_queue.name}

    client.provision_queue(sqs_queue)
    assert sqs_queue.queue_url is not None


@pytest.mark.skip
def test_provision_queue_update():
    client = SQSClient()
    sqs_queue = SQSQueue({})
    sqs_queue.region = AWSAccount.get_aws_region()
    sqs_queue.name = "sqs_queue_horey_test"
    sqs_queue.visibility_timeout = "30"
    sqs_queue.maximum_message_size = "262144"
    sqs_queue.message_retention_period = "604800"
    sqs_queue.delay_seconds = "0"
    sqs_queue.redrive_policy = (
        '{"deadLetterTargetArn":"'
        + mock_values["dlq_arn"]
        + '","maxReceiveCount":1000}'
    )
    sqs_queue.tags = {"name": sqs_queue.name}

    client.provision_queue(sqs_queue)
    assert sqs_queue.queue_url is not None

@pytest.mark.todo
def test_yield_queues_get_tags_true():
    client = SQSClient()
    obj = None
    for obj in client.yield_queues(get_tags=True):
        break
    assert obj.arn is not None
    assert obj.tags is not None


@pytest.mark.todo
def test_yield_queues_get_tags_false():
    client = SQSClient()
    obj = None
    for obj in client.yield_queues(get_tags=False):
        break
    assert obj.arn is not None
    assert obj.tags is None


@pytest.mark.todo
def test_yield_queues_raw():
    client = SQSClient()
    dict_src = None
    for dict_src in client.yield_queues_raw():
        break
    assert dict_src.get("QueueArn") is not None
    assert dict_src.get("QueueUrl") is not None


@pytest.mark.todo
def test_get_region_queues():
    client = SQSClient()
    ret = client.get_region_queues(Region.get_region("us-west-2"))
    assert len(ret) > 0

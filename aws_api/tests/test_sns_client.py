"""
AWS SNS client tests
"""
import os
import pytest

from horey.aws_api.aws_clients.sns_client import SNSClient
from horey.aws_api.aws_services_entities.sns_topic import SNSTopic
from horey.common_utils.common_utils import CommonUtils

SNSClient().main_cache_dir_path = os.path.abspath(
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

# pylint: disable= missing-function-docstring

@pytest.mark.todo
def test_init_client():
    assert isinstance(SNSClient(), SNSClient)

@pytest.mark.todo
def test_clear_cache():
    SNSClient().clear_cache(SNSTopic)

@pytest.mark.todo
def test_get_all_subscriptions():
    client = SNSClient()
    ret = client.get_all_subscriptions()
    assert ret is not None

@pytest.mark.todo
def test_get_all_topics():
    client = SNSClient()
    ret = client.get_all_topics()
    assert ret is not None

@pytest.mark.todo
def test_yield_topics():
    client = SNSClient()
    obj = None
    for obj in client.yield_topics():
        break
    assert obj.arn is not None


@pytest.mark.todo
def test_get_get_all_topics_full_information_false():
    client = SNSClient()
    ret = client.get_all_topics(full_information=False)
    assert len(ret) > 0


@pytest.mark.todo
def test_get_get_all_topics_full_information_true():
    client = SNSClient()
    ret = client.get_all_topics(full_information=True)
    assert len(ret) > 0


@pytest.mark.todo
def test_yield_subscriptions():
    client = SNSClient()
    obj = None
    for obj in client.yield_subscriptions():
        break
    assert obj.arn is not None


@pytest.mark.todo
def test_get_get_all_subscriptions_full_information_false():
    client = SNSClient()
    ret = client.get_all_subscriptions(full_information=False)
    assert len(ret) > 0


@pytest.mark.todo
def test_get_get_all_subscriptions_full_information_true():
    client = SNSClient()
    ret = client.get_all_subscriptions(full_information=True)
    assert len(ret) > 0

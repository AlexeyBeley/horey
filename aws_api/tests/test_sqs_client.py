import os
import pdb

from horey.aws_api.aws_clients.sqs_client import SQSClient
from horey.aws_api.aws_services_entities.sqs_queue import SQSQueue

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


def test_init_client():
    assert isinstance(SQSClient(), SQSClient)


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


if __name__ == "__main__":
    test_init_client()
    test_provision_queue_dlq()
    test_provision_queue()
    test_provision_queue_update()

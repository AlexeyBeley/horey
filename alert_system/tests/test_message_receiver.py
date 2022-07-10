import json
import pdb

from horey.alert_system.message_receiver import MessageReceiver
from horey.alert_system.message_receiver_configuration_policy import MessageReceiverConfigurationPolicy
from horey.alert_system.lambda_package.message import Message
import os
from horey.common_utils.common_utils import CommonUtils

mock_values_file_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"))
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


def test_init_message_receiver():
    assert isinstance(MessageReceiver(), MessageReceiver)


def test_provision_sns_topic():
    configuration = MessageReceiverConfigurationPolicy()
    configuration.horey_repo_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    configuration.slack_api_configuration_file = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "slack_api_configuration_values.py"))

    message_receiver = MessageReceiver(configuration)

    message_receiver.provision_sns_topic()


def test_provision_sns_subscription():
    configuration = MessageReceiverConfigurationPolicy()
    configuration.horey_repo_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    configuration.slack_api_configuration_file = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "slack_api_configuration_values.py"))

    message_receiver = MessageReceiver(configuration)

    message_receiver.provision_sns_subscription()


def test_provision_lambda_role():
    configuration = MessageReceiverConfigurationPolicy()
    configuration.horey_repo_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    configuration.slack_api_configuration_file = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "slack_api_configuration_values.py"))
    message_receiver = MessageReceiver(configuration)

    message_receiver.provision_lambda_role()


def test_provision_lambda():
    configuration = MessageReceiverConfigurationPolicy()
    configuration.horey_repo_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    configuration.slack_api_configuration_file = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "slack_api_configuration_values.py"))
    message_receiver = MessageReceiver(configuration)

    message_receiver.provision_lambda()


def test_provision():
    configuration = MessageReceiverConfigurationPolicy()
    configuration.sla = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "aws_api_configuration_values.py"))
    configuration.init_from_file()
    message_receiver = MessageReceiver(configuration)

    message_receiver.provision()


def test_provision_cloudwatch_alarm():
    configuration = MessageReceiverConfigurationPolicy()
    configuration.horey_repo_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    configuration.slack_api_configuration_file = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "slack_api_configuration_values.py"))
    message_receiver = MessageReceiver(configuration)
    message = Message()
    message.type = "test_message"
    message.generate_uuid()
    message.data = json.dumps({"key": "value", "tags": ["infra"]})
    message_receiver.provision_cloudwatch_alarm(mock_values["alarm_dimensions"], message)


if __name__ == "__main__":
    #test_provision_lambda()
    #test_provision_sns_topic()
    #test_provision_sns_subscription()
    test_provision_cloudwatch_alarm()

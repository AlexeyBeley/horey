import pdb

from horey.alert_system.message_receiver import MessageReceiver
from horey.alert_system.message_receiver_configuration_policy import MessageReceiverConfigurationPolicy
import os
from horey.common_utils.common_utils import CommonUtils

mock_values_file_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"))
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


def test_init_message_receiver():
    assert isinstance(MessageReceiver(), MessageReceiver)


def test_provision_sns():
    configuration = MessageReceiverConfigurationPolicy()
    configuration.configuration_file_full_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "aws_api_configuration_values.py"))
    configuration.init_from_file()
    message_receiver = MessageReceiver(configuration)

    message_receiver.provision_sns()


def test_provision_lambda():
    configuration = MessageReceiverConfigurationPolicy()
    configuration.slack_api_configuration_file = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "slack_api_configuration_values.py"))
    message_receiver = MessageReceiver(configuration)

    message_receiver.provision_lambda("generic_receiver_test")


def test_provision():
    configuration = MessageReceiverConfigurationPolicy()
    configuration.sla = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "aws_api_configuration_values.py"))
    configuration.init_from_file()
    message_receiver = MessageReceiver(configuration)

    message_receiver.provision()


if __name__ == "__main__":
    #test_provision_sns()
    test_provision_lambda()
    #test_provision()

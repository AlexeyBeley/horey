import pdb

from horey.alert_receiver.alert_receiver import AlertReceiver
from horey.alert_receiver.alert_receiver_configuraion_policy import AlertReceiverConfigurationPolicy
import os
from horey.common_utils.common_utils import CommonUtils
from horey.aws_api.aws_api import AWSAPI

mock_values_file_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"))
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

src_aws_region = "us-west-2"
dst_aws_region = "us-west-2"


def test_init_alert_receiver():
    assert isinstance(AlertReceiver(), AlertReceiver)


def test_provision_sns():
    configuration = AlertReceiverConfigurationPolicy()
    configuration.configuration_file_full_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "aws_api_configuration_values.py"))
    configuration.init_from_file()
    alert_receiver = AlertReceiver(configuration)

    alert_receiver.provision_sns()


def test_provision_lambda():
    configuration = AlertReceiverConfigurationPolicy()
    configuration.configuration_file_full_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "aws_api_configuration_values.py"))
    configuration.init_from_file()
    alert_receiver = AlertReceiver(configuration)

    alert_receiver.provision_lambda()


def test_provision():
    configuration = AlertReceiverConfigurationPolicy()
    configuration.configuration_file_full_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "aws_api_configuration_values.py"))
    configuration.init_from_file()
    alert_receiver = AlertReceiver(configuration)

    alert_receiver.provision()


if __name__ == "__main__":
    test_provision_sns()
    test_provision_lambda()
    test_provision()

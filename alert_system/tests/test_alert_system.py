import json
import pdb

from horey.alert_system.alert_system import AlertSystem
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy
from horey.alert_system.lambda_package.message import Message
import os
from horey.common_utils.common_utils import CommonUtils
from horey.aws_api.base_entities.region import Region

mock_values_file_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"))
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


def test_init_alert_system():
    assert isinstance(AlertSystem(), AlertSystem)


def test_provision_sns_topic():
    configuration = AlertSystemConfigurationPolicy()
    configuration.horey_repo_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    configuration.slack_api_configuration_file = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "slack_api_configuration_values.py"))

    alert_system = AlertSystem(configuration)

    alert_system.provision_sns_topic()


def test_provision_sns_subscription():
    configuration = AlertSystemConfigurationPolicy()
    configuration.horey_repo_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    configuration.slack_api_configuration_file = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "slack_api_configuration_values.py"))

    alert_system = AlertSystem(configuration)

    alert_system.provision_sns_subscription()


def test_provision_lambda_role():
    configuration = AlertSystemConfigurationPolicy()
    configuration.horey_repo_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    configuration.slack_api_configuration_file = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "slack_api_configuration_values.py"))
    alert_system = AlertSystem(configuration)

    alert_system.provision_lambda_role()


def test_provision_lambda():
    configuration = AlertSystemConfigurationPolicy()
    configuration.horey_repo_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    configuration.slack_api_configuration_file = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "slack_api_configuration_values.py"))
    alert_system = AlertSystem(configuration)

    alert_system.provision_lambda()


def test_provision():
    configuration = AlertSystemConfigurationPolicy()
    configuration.sla = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "aws_api_configuration_values.py"))
    configuration.init_from_file()
    alert_system = AlertSystem(configuration)

    alert_system.provision()


def test_provision_cloudwatch_alarm():
    configuration = AlertSystemConfigurationPolicy()
    configuration.horey_repo_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    configuration.slack_api_configuration_file = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "slack_api_configuration_values.py"))
    alert_system = AlertSystem(configuration)
    message = Message()
    message.type = "test_message"
    message.generate_uuid()
    message.data = {"key": "value", "tags": ["infra"]}
    alert_system.provision_cloudwatch_alarm(mock_values["alarm_dimensions"], message)


def test_provision_cloudwatch_logs_alarm():
    configuration = AlertSystemConfigurationPolicy()
    configuration.horey_repo_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    configuration.slack_api_configuration_file = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "slack_api_configuration_values.py"))
    configuration.region = "us-west-2"
    configuration.sns_topic_name = "topic_test_alert_system"

    alert_system = AlertSystem(configuration)

    message = Message()
    message.type = "test_message"
    message.generate_uuid()
    message.data = {"key": "value", "tags": ["infra"]}
    alert_system.provision_cloudwatch_logs_alarm(mock_values["log_group_name"], "[INFO]", "clwtch-log-error", message)


def test_deploy_lambda():
    configuration = AlertSystemConfigurationPolicy()
    configuration.horey_repo_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    configuration.slack_api_configuration_file = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "slack_api_configuration_values.py"))
    configuration.region = "us-west-2"

    configuration.lambda_name = "alert_system_test_deploy_lambda"
    configuration.deployment_dir_path = "/tmp/alert_system"
    configuration.sns_topic_name = "topic_test_alert_system"

    alert_system = AlertSystem(configuration)

    tags = [
        {
            "Key": "name",
            "Value": configuration.lambda_name
        }]

    alert_system.provision(tags, [])


if __name__ == "__main__":
    # test_provision_lambda()
    # test_provision_sns_topic()
    # test_provision_sns_subscription()
    # test_provision_cloudwatch_alarm()
    #test_provision_cloudwatch_logs_alarm()
    test_deploy_lambda()

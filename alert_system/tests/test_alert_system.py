import json
import pdb

from horey.alert_system.alert_system import AlertSystem
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy
from horey.alert_system.lambda_package.message import Message
from horey.aws_api.base_entities.region import Region
import os
from horey.common_utils.common_utils import CommonUtils
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm

mock_values_file_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"))
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

as_configuration = AlertSystemConfigurationPolicy()
as_configuration.horey_repo_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

as_configuration.region = "us-west-2"
as_configuration.lambda_name = "alert_system_test_deploy_lambda"
as_configuration.sns_topic_name = "topic_test_alert_system"

as_configuration.deployment_dir_path = "/tmp/horey_deployment"
as_configuration.notification_channels = ["notification_channel_slack.py"]
notification_channel_slack_configuration_file = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                 "notification_channel_slack_configuration_values.py"))


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
    as_configuration = AlertSystemConfigurationPolicy()
    as_configuration.horey_repo_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

    as_configuration.region = "us-west-2"
    as_configuration.lambda_name = "alert_system_test_deploy_lambda"
    as_configuration.sns_topic_name = "topic_test_alert_system"

    as_configuration.deployment_dir_path = "/tmp/horey_deployment"
    as_configuration.slack_api_configuration_file = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "slack_api_configuration_values.py"))

    alert_system = AlertSystem(as_configuration)
    tags = [
        {
            "Key": "name",
            "Value": as_configuration.lambda_name
        }]
    alert_system.provision(tags, [notification_channel_slack_configuration_file])


def test_create_lambda_package():
    alert_system = AlertSystem(as_configuration)
    alert_system.create_lambda_package([notification_channel_slack_configuration_file])


def test_provision_self_monitoring():
    alert_system = AlertSystem(as_configuration)
    alert_system.provision_self_monitoring()


def test_provision_cloudwatch_alarm():
    configuration = AlertSystemConfigurationPolicy()
    configuration.horey_repo_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    configuration.slack_api_configuration_file = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                     "slack_api_configuration_values.py"))
    configuration.region = "us-west-2"
    message = Message()
    message.uuid = "test1-test2"
    message.type = "cloudwatch-metric-lambda-duration"
    message.data = {"tags": ["alert_system"]}

    alert_system = AlertSystem(configuration)
    alarm = CloudWatchAlarm({})
    alarm.name = "test-alarm"
    alarm.actions_enabled = True
    alarm.alarm_description = json.dumps(message.convert_to_dict())
    alarm.insufficient_data_actions = []
    alarm.metric_name = "Duration"
    alarm.namespace = "AWS/Lambda"
    alarm.statistic = "Average"
    alarm.dimensions = [{"Name": "FunctionName", "Value": "alert_system_test_deploy_lambda"}]
    alarm.period = 300
    alarm.evaluation_periods = 1
    alarm.datapoints_to_alarm = 1
    alarm.threshold = 500.0
    alarm.comparison_operator = "GreaterThanThreshold"
    alarm.treat_missing_data = "missing"
    alert_system.provision_cloudwatch_alarm(alarm)


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

    message_data = {"key": "value", "tags": ["team_name"]}
    alert_system.provision_cloudwatch_logs_alarm(mock_values["log_group_name"], "[INFO]", "clwtch-log-error", message_data)


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

    alert_system.provision(tags, [notification_channel_slack_configuration_file])


if __name__ == "__main__":
    # test_provision_lambda()
    # test_provision_sns_topic()
    # test_provision_sns_subscription()
    #test_provision_cloudwatch_alarm()
    #test_provision_cloudwatch_logs_alarm()
    #test_deploy_lambda()
    #test_provision_self_monitoring()
    #test_provision()
    test_create_lambda_package()

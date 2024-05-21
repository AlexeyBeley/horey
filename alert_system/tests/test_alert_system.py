"""
Testing alert system functions.

"""

import json
import os
import pytest

from horey.alert_system.alert_system import AlertSystem
from horey.alert_system.alert_system_configuration_policy import (
    AlertSystemConfigurationPolicy,
)
from horey.alert_system.lambda_package.message import Message
from horey.common_utils.common_utils import CommonUtils
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm

mock_values_file_path = os.path.abspath(
    os.path.abspath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "alert_system_mock_values.py"
    ))
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

as_configuration = AlertSystemConfigurationPolicy()
as_configuration.horey_repo_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
)

as_configuration.region = "us-west-2"
as_configuration.lambda_name = "alert_system_test_deploy_lambda"
as_configuration.sns_topic_name = "topic_test_alert_system"
as_configuration.tags = [{"Key": "env_level", "Value": "development"}]

as_configuration.deployment_dir_path = "/tmp/horey_deployment"
as_configuration.notification_channel_file_names = "notification_channel_slack.py"
as_configuration.active_deployment_validation = True
notification_channel_slack_configuration_file = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "..",
        "ignore",
        "notification_channel_slack_configuration_values.py",
    )
)

# pylint: disable=missing-function-docstring

@pytest.mark.done
def test_init_alert_system():
    """
    Test initiation.

    @return:
    """

    assert isinstance(AlertSystem(as_configuration), AlertSystem)


@pytest.mark.done
def test_provision_sns_topic():
    """
    Test provisioning alert_system sns topic

    @return:
    """

    alert_system = AlertSystem(as_configuration)
    alert_system.provision_sns_topic()


@pytest.mark.done
def test_provision_sns_subscription():
    """
    Test provisioning alert_system sns topic subscription

    @return:
    """

    alert_system = AlertSystem(as_configuration)

    alert_system.provision_sns_subscription()


@pytest.mark.done
def test_provision_lambda_role():
    """
    Test provisioning alert_system lambda role.

    @return:
    """

    alert_system = AlertSystem(as_configuration)
    alert_system.provision_lambda_role()


@pytest.mark.done
def test_provision_lambda():
    """
    Test provisioning alert_system lambda.

    @return:
    """
    alert_system = AlertSystem(as_configuration)

    alert_system.provision_lambda([notification_channel_slack_configuration_file])


@pytest.mark.done
def test_provision():
    """
    Test provisioning all the alert_system components.

    @return:
    """

    alert_system = AlertSystem(as_configuration)
    tags = [{"Key": "name", "Value": as_configuration.lambda_name}]
    alert_system.provision(tags, [notification_channel_slack_configuration_file])


@pytest.mark.done
def test_provision_and_trigger_locally_lambda_handler():
    """
    Test provisioned lambda locally

    @return:
    """

    alert_system = AlertSystem(as_configuration)
    alert_system.provision_and_trigger_locally_lambda_handler([notification_channel_slack_configuration_file],
                                                              os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw_messages", "sns_form_raw_1.json"))


@pytest.mark.done
def test_provision_and_trigger_locally_lambda_handler_info():
    """
    Test provisioned lambda locally

    @return:
    """

    alert_system = AlertSystem(as_configuration)
    alert_system.provision_and_trigger_locally_lambda_handler([notification_channel_slack_configuration_file],
                                                              os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw_messages", "sns_form_raw_info.json"))


@pytest.mark.done
def test_create_lambda_package():
    """
    Test local package creation.

    @return:
    """

    alert_system = AlertSystem(as_configuration)
    alert_system.create_lambda_package([notification_channel_slack_configuration_file])


@pytest.mark.done
def test_provision_self_monitoring():
    """
    Test provisioning self monitoring

    @return:
    """

    alert_system = AlertSystem(as_configuration)
    alert_system.provision_self_monitoring()


@pytest.mark.done
def test_provision_cloudwatch_alarm():
    """
    Test provisioning cloudwatch generic alarm

    @return:
    """

    message = Message()
    message.uuid = "test1-test2"
    message.type = "cloudwatch-metric-lambda-duration"
    message.data = {"tags": ["alert_system"]}

    alert_system = AlertSystem(as_configuration)
    alarm = CloudWatchAlarm({})
    alarm.name = "test-alarm"
    alarm.actions_enabled = True
    alarm.alarm_description = json.dumps(message.convert_to_dict())
    alarm.insufficient_data_actions = []
    alarm.metric_name = "Duration"
    alarm.namespace = "AWS/Lambda"
    alarm.statistic = "Average"
    alarm.dimensions = [{"Name": "FunctionName", "Value": as_configuration.lambda_name}]
    alarm.period = 300
    alarm.evaluation_periods = 1
    alarm.datapoints_to_alarm = 1
    alarm.threshold = 500.0
    alarm.comparison_operator = "GreaterThanThreshold"
    alarm.treat_missing_data = "missing"
    alert_system.provision_cloudwatch_alarm(alarm)


@pytest.mark.done
def test_provision_cloudwatch_logs_alarm():
    """
    Test provisioning cloudwatch logs alarm

    @return:
    """

    alert_system = AlertSystem(as_configuration)

    message_data = {"key": "value", "tags": ["team_name"]}
    alert_system.provision_cloudwatch_logs_alarm(
        as_configuration.alert_system_lambda_log_group_name, "[ERROR]", "clwtch-log-error", message_data
    )


@pytest.mark.done
def test_provision_cloudwatch_sqs_visible_alarm():
    """
    Provision cloudwatch sqs visible alarm.

    @return:
    """
    alert_system = AlertSystem(as_configuration)

    message_data = {"key": "value", "tags": ["alert_system_monitoring"]}
    alert_system.provision_cloudwatch_sqs_visible_alarm(
        mock_values["sqs_queue_name"], 0.0, message_data
    )


@pytest.mark.done
def test_send_message_to_sns():
    message = Message()
    message.uuid = "test1-test2"
    message.type = "raw"
    message.data = {"tags": ["alert_system"], "level": "alert"}
    alert_system = AlertSystem(as_configuration)
    alert_system.send_message_to_sns(message)


@pytest.mark.done
def test_trigger_self_monitoring_log_error_alarm():
    alert_system = AlertSystem(as_configuration)
    alert_system.trigger_self_monitoring_log_error_alarm()


@pytest.mark.done
def test_trigger_self_monitoring_log_timeout_alarm():
    alert_system = AlertSystem(as_configuration)
    alert_system.trigger_self_monitoring_log_timeout_alarm()


@pytest.mark.done
def test_trigger_self_monitoring_errors_metric_alarm():
    alert_system = AlertSystem(as_configuration)
    alert_system.trigger_self_monitoring_errors_metric_alarm()


@pytest.mark.done
def test_trigger_self_monitoring_duration_alarm():
    alert_system = AlertSystem(as_configuration)
    alert_system.trigger_self_monitoring_duration_alarm()


@pytest.mark.todo
def test_provision_alert_system_ses_configuration_set():
    """
    Fix configuration set events destination provision
    :return:
    """
    alert_system = AlertSystem(as_configuration)
    alert_system.provision_alert_system_ses_configuration_set()


@pytest.mark.done
def test_send_ses_email():
    alert_system = AlertSystem(as_configuration)
    request_dict = {}
    ret = alert_system.aws_api.sesv2_client.get_all_email_identities(alert_system.region)
    for identity in ret:
        if identity.identity_type == "DOMAIN":
            break
    else:
        raise ValueError("No domain identity found")

    ret = alert_system.aws_api.ses_client.yield_receipt_rule_sets(region=alert_system.region)
    for rule_set in ret:
        for rule in rule_set.rules:
            if not rule["Enabled"]:
                continue
            if not rule.get("Recipients"):
                continue
            rule_recipient = rule["Recipients"][0]
            break
        else:
            continue
        break
    else:
        raise ValueError("No Recipients found")

    request_dict["FromEmailAddress"] = f"alert_system_test@{identity.name}"
    request_dict["Destination"] = {"ToAddresses": [rule_recipient]}
    request_dict["Content"] = {"Simple": {"Subject": {"Data": "Test alert", "Charset": "UTF-8"}, "Body": {'Text': {
                    'Data': 'string',
                    'Charset': "UTF-8"
                }}}}
    request_dict["ConfigurationSetName"] = alert_system.configuration.alert_system_ses_configuration_set_name

    alert_system.aws_api.sesv2_client.send_email_raw(alert_system.region, request_dict)

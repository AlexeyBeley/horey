"""
Testing alert system functions.

"""
import json
import os
import shutil
import time
from unittest.mock import Mock

import pytest
from common import ses_events

from horey.alert_system.alert_system import AlertSystem
from horey.alert_system.alert_system_configuration_policy import (
    AlertSystemConfigurationPolicy,
)
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm
from horey.aws_api.aws_services_entities.aws_lambda import AWSLambda
from horey.aws_api.base_entities.region import Region
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.alert_system.lambda_package.notification import Notification

# pylint: disable=missing-function-docstring


@pytest.mark.done
def test_provision_dynamodb(alert_system_configuration):
    """
    Test provisioning alert_system lambda.

    @return:
    """
    alert_system = AlertSystem(alert_system_configuration)
    alert_system.provision_dynamodb()


@pytest.mark.done
def test_provision_lambda(alert_system_configuration):
    """
    Test provisioning alert_system lambda.

    @return:
    """
    alert_system = AlertSystem(alert_system_configuration)
    alert_system.provision_lambda([])


@pytest.mark.done
def test_provision_self_monitoring_duration_alarm(alert_system_configuration):
    alert_system = AlertSystem(alert_system_configuration)
    alarm = alert_system.provision_self_monitoring_duration_alarm()
    alarm_description = json.loads(alarm.alarm_description)
    assert alarm_description == {"routing_tags": [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG],
                                 "lambda_name": "alert_system_test_deploy_lambda",
                                 "ALERT_SYSTEM_SELF_MONITORING": "ALERT_SYSTEM_SELF_MONITORING"}


@pytest.mark.done
def test_set_self_monitoring_duration_alarm_ok(alert_system_configuration):
    alert_system = AlertSystem(alert_system_configuration)
    alarm = alert_system.provision_self_monitoring_duration_alarm()
    assert alert_system.aws_api.cloud_watch_client.set_alarm_ok(alarm)


@pytest.mark.done
def test_trigger_self_monitoring_duration_alarm(alert_system_configuration):
    alert_system = AlertSystem(alert_system_configuration)
    response = alert_system.trigger_self_monitoring_duration_alarm()
    assert response is not None


@pytest.mark.done
def test_provision_self_monitoring_errors_metric_alarm(alert_system_configuration):
    alert_system = AlertSystem(alert_system_configuration)
    alarm = alert_system.provision_self_monitoring_errors_metric_alarm()
    alarm_description = json.loads(alarm.alarm_description)
    assert alarm_description == {"routing_tags": [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG],
                                 "lambda_name": "alert_system_test_deploy_lambda",
                                 "ALERT_SYSTEM_SELF_MONITORING": "ALERT_SYSTEM_SELF_MONITORING"}


@pytest.mark.done
def test_set_self_monitoring_errors_metric_alarm_ok(alert_system_configuration):
    alert_system = AlertSystem(alert_system_configuration)
    alarm = alert_system.provision_self_monitoring_errors_metric_alarm()
    assert alert_system.aws_api.cloud_watch_client.set_alarm_ok(alarm)


@pytest.mark.done
def test_trigger_self_monitoring_errors_metric_alarm(alert_system_configuration):
    alert_system = AlertSystem(alert_system_configuration)
    response = alert_system.trigger_self_monitoring_errors_metric_alarm()
    assert response is not None


@pytest.mark.done
def test_provision_self_monitoring_log_timeout_alarm(alert_system_configuration):
    alert_system = AlertSystem(alert_system_configuration)
    alarm = alert_system.provision_self_monitoring_log_timeout_alarm()
    alarm_description = json.loads(alarm.alarm_description)
    assert alarm_description == {"routing_tags": [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG],
                                 "log_group_name": "/aws/lambda/alert_system_test_deploy_lambda",
                                 "lambda_name": "alert_system_test_deploy_lambda",
                                 "log_group_filter_pattern": "Task timed out after",
                                 "ALERT_SYSTEM_SELF_MONITORING": "ALERT_SYSTEM_SELF_MONITORING"}


@pytest.mark.done
def test_set_self_monitoring_log_timeout_alarm_ok(alert_system_configuration):
    alert_system = AlertSystem(alert_system_configuration)
    alarm = alert_system.provision_self_monitoring_log_timeout_alarm()
    assert alert_system.aws_api.cloud_watch_client.set_alarm_ok(alarm)


@pytest.mark.done
def test_trigger_self_monitoring_log_timeout_alarm(alert_system_configuration):
    alert_system = AlertSystem(alert_system_configuration)
    response = alert_system.trigger_self_monitoring_log_timeout_alarm()
    assert response is not None


@pytest.mark.done
def test_provision_self_monitoring_log_error_alarm(alert_system_configuration):
    alert_system = AlertSystem(alert_system_configuration)
    alarm = alert_system.provision_self_monitoring_log_error_alarm()
    alarm_description = json.loads(alarm.alarm_description)
    assert alarm_description == {"routing_tags": [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG],
                                 "log_group_name": alert_system.configuration.alert_system_lambda_log_group_name,
                                 "lambda_name": alert_system.configuration.lambda_name,
                                 "log_group_filter_pattern": f'"{AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_LOG_ERROR_FILTER_PATTERN}"',
                                 "ALERT_SYSTEM_SELF_MONITORING": "ALERT_SYSTEM_SELF_MONITORING"}


@pytest.mark.done
def test_set_self_monitoring_log_error_alarm_ok(alert_system_configuration):
    alert_system = AlertSystem(alert_system_configuration)
    alarm = alert_system.provision_self_monitoring_log_error_alarm()
    assert alert_system.aws_api.cloud_watch_client.set_alarm_ok(alarm)


@pytest.mark.done
def test_trigger_self_monitoring_log_error_alarm(alert_system_configuration):
    alert_system = AlertSystem(alert_system_configuration)
    assert alert_system.trigger_self_monitoring_log_error_alarm()


@pytest.mark.done
def test_trigger_self_monitoring_log_error_alarm_loop(alert_system_configuration):
    alert_system = AlertSystem(alert_system_configuration)
    for i in range(60):
        assert alert_system.trigger_self_monitoring_log_error_alarm()
        time.sleep(60)


@pytest.mark.done
def test_init_alert_system(alert_system_configuration):
    """
    Test initiation.

    @return:
    """

    assert isinstance(AlertSystem(alert_system_configuration), AlertSystem)


@pytest.mark.done
def test_provision_sns_topic(alert_system_configuration):
    """
    Test provisioning alert_system sns topic

    @return:
    """

    alert_system = AlertSystem(alert_system_configuration)
    alert_system.provision_sns_topic()


@pytest.mark.done
def test_provision_sns_subscription(alert_system_configuration):
    """
    Test provisioning alert_system sns topic subscription

    @return:
    """

    alert_system = AlertSystem(alert_system_configuration)

    alert_system.provision_sns_subscription()


@pytest.mark.done
def test_provision_lambda_role(alert_system_configuration):
    """
    Test provisioning alert_system lambda role.

    @return:
    """

    alert_system = AlertSystem(alert_system_configuration)
    alert_system.provision_lambda_role()


@pytest.mark.todo
def test_validate_input(alert_system_configuration):
    """
    Test provisioning all the alert_system components.

    @return:
    """
    AWSAccount.set_aws_default_region(Region.get_region("us-west-2"))
    alert_system = AlertSystem(alert_system_configuration)
    shutil.copy2(os.path.abspath(
        os.path.join(os.path.dirname(__file__), "notification_channels", "notification_channel_echo_initializer.py")),
        alert_system.configuration.deployment_dir_path)
    alert_system.validate_input([os.path.join(alert_system_configuration.deployment_directory_path,
                                              "notification_channel_echo_initializer.py")])


@pytest.mark.todo
def test_provision(alert_system_configuration):
    """
    Test provisioning all the alert_system components.

    @return:
    """
    AWSAccount.set_aws_default_region(Region.get_region("us-west-2"))
    alert_system = AlertSystem(alert_system_configuration)
    shutil.copy2(os.path.abspath(
        os.path.join(os.path.dirname(__file__), "notification_channels", "notification_channel_echo_initializer.py")),
        alert_system.configuration.deployment_dir_path)
    alert_system.provision([os.path.join(alert_system_configuration.deployment_directory_path,
                                         "notification_channel_echo_initializer.py")])


@pytest.mark.todo
def test_provision_and_trigger_locally_lambda_handler(alert_system_configuration):
    """
    Test provisioned lambda locally

    @return:
    """

    alert_system = AlertSystem(alert_system_configuration)
    alert_system.provision_and_trigger_locally_lambda_handler([],
                                                              os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                           "raw_messages", "sns_form_raw_1.json"))


@pytest.mark.todo
def test_provision_and_trigger_locally_lambda_handler_info(alert_system_configuration):
    """
    Test provisioned lambda locally

    @return:
    """

    alert_system = AlertSystem(alert_system_configuration)
    alert_system.provision_and_trigger_locally_lambda_handler([],
                                                              os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                           "raw_messages", "sns_form_raw_info.json"))


@pytest.mark.todo
def test_create_lambda_package(as_configuration, lambda_package_alert_system_config_file):
    """
    Test local package creation.

    @return:
    """
    alert_system = AlertSystem(as_configuration)
    alert_system.validate_lambda_package = Mock()
    zip_file_path = alert_system.create_lambda_package([lambda_package_alert_system_config_file])
    assert os.path.isfile(zip_file_path)


@pytest.mark.todo
def test_validate_lambda_package_ses_events(alert_system_configuration):
    """
    Test local package creation.

    @return:
    """
    alert_system = AlertSystem(alert_system_configuration)
    alert_system.validate_lambda_package = Mock()
    zip_file_path = alert_system.create_lambda_package(([
        os.path.join(alert_system_configuration.deployment_directory_path,
                     "notification_channel_echo_initializer.py")]))
    extraction_dir = alert_system.extract_lambda_package_for_validation(zip_file_path)
    for ses_event in ses_events:
        ret = alert_system.trigger_lambda_handler_locally(extraction_dir, ses_event)
        assert ret.get("statusCode") == 200


@pytest.mark.todo
def test_validate_lambda_package_none(as_configuration, lambda_package_alert_system_config_file):
    """
    Test local package creation.

    @return:
    """
    alert_system = AlertSystem(as_configuration)
    alert_system.validate_lambda_package = Mock()
    zip_file_path = alert_system.create_lambda_package([lambda_package_alert_system_config_file])
    extraction_dir = alert_system.extract_lambda_package_for_validation(zip_file_path)
    ret = alert_system.trigger_lambda_handler_locally(extraction_dir, None)
    assert ret.get("statusCode") == 404


@pytest.mark.done
def test_provision_self_monitoring(alert_system_configuration):
    """
    Test provisioning self monitoring

    @return:
    """

    alert_system = AlertSystem(alert_system_configuration)
    alert_system.provision_self_monitoring()


@pytest.mark.done
def test_provision_cloudwatch_alarm(alert_system_configuration):
    """
    Test provisioning cloudwatch generic alarm

    @return:
    """

    alert_system = AlertSystem(alert_system_configuration)
    alarm = CloudWatchAlarm({})
    alarm.name = "test-alarm"
    alarm.actions_enabled = True
    alarm.alarm_description = json.dumps({"bla":"bla"})
    alarm.insufficient_data_actions = []
    alarm.metric_name = "Duration"
    alarm.namespace = "AWS/Lambda"
    alarm.statistic = "Average"
    alarm.dimensions = [{"Name": "FunctionName", "Value": alert_system_configuration.lambda_name}]
    alarm.period = 300
    alarm.evaluation_periods = 1
    alarm.datapoints_to_alarm = 1
    alarm.threshold = 500.0
    alarm.comparison_operator = "GreaterThanThreshold"
    alarm.treat_missing_data = "missing"
    alert_system.provision_cloudwatch_alarm(alarm)


@pytest.mark.done
def test_provision_cloudwatch_logs_alarm(alert_system_configuration):
    """
    Test provisioning cloudwatch logs alarm

    @return:
    """

    alert_system = AlertSystem(alert_system_configuration)

    alarm = alert_system.provision_cloudwatch_logs_alarm(
        alert_system_configuration.alert_system_lambda_log_group_name, "[ERROR]", "test-alarm-creation", [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG],
    )
    assert alarm


@pytest.mark.done
def test_provision_cloudwatch_logs_json_log_format_alarm(alert_system_configuration):
    """
    Test provisioning cloudwatch logs alarm

    @return:
    """

    alert_system = AlertSystem(alert_system_configuration)
    filter_text = json.dumps('"level": "error"')
    metric_uid = "json_format_test_alarm"
    alarm = alert_system.provision_cloudwatch_logs_alarm(
        alert_system_configuration.alert_system_lambda_log_group_name, filter_text, metric_uid, [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG]
    )
    alert_system.aws_api.cloud_watch_client.set_alarm_ok(alarm)

    line = json.dumps({"level": "error", "line": "Neo, the Horey has you!"})
    log_group_name = alert_system.configuration.alert_system_lambda_log_group_name

    lst_ret = []
    for _ in range(1000):
        try:
            test_time = alert_system.test_end_to_end_log_pattern_alert(log_group_name, line, alarm)
            lst_ret.append(test_time)
            time.sleep(301)
            alert_system.aws_api.cloud_watch_client.set_alarm_ok(alarm)
        except Exception:
            lst_ret.append(-1)


@pytest.mark.done
def test_provision_cloudwatch_sqs_visible_alarm(alert_system_configuration):
    """
    Provision cloudwatch sqs visible alarm.

    @return:
    """
    alert_system = AlertSystem(alert_system_configuration)

    message_data = {"key": "value", "tags": ["alert_system_monitoring"]}
    alert_system.provision_cloudwatch_sqs_visible_alarm(
        "sqs_queue_test_name", 0.0, message_data
    )


@pytest.mark.done
def test_send_message_to_sns(alert_system_configuration):
    alert_system = AlertSystem(alert_system_configuration)
    alert_system.send_message_to_sns({"bla": "bla"})


@pytest.mark.todo
def test_provision_ses_configuration_set(alert_system_configuration):
    """
    Fix configuration set events destination provision
    :return:
    """
    alert_system = AlertSystem(alert_system_configuration)
    alert_system.provision_ses_configuration_set()


@pytest.mark.todo
def test_send_ses_email(alert_system_configuration):
    alert_system = AlertSystem(alert_system_configuration)
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


@pytest.mark.done
def test_provision_event_bridge_rule(alert_system_configuration):
    alert_system = AlertSystem(alert_system_configuration)
    aws_lambda = AWSLambda({"FunctionName": alert_system.configuration.lambda_name})
    aws_lambda.region = alert_system.region
    alert_system.aws_api.lambda_client.update_lambda_information(aws_lambda, full_information=False)
    alert_system.provision_event_bridge_rule(aws_lambda=aws_lambda)


@pytest.mark.wip
def test_init_cloudwatch_metrics(alert_system_configuration):
    alert_system = AlertSystem(alert_system_configuration)
    metrics = list(alert_system.aws_api.cloud_watch_client.yield_client_metrics(region=alert_system.region))
    breakpoint()
    metrics_events = [x for x in metrics if x["Namespace"] == "AWS/Events"]
    metrics_dynamodb = [x for x in metrics if x["Namespace"] == "AWS/DynamoDB"]

    metric_names_events = {x["MetricName"] for x in metrics_events}
    response = {'InvocationAttempts',
                'MatchedEvents',
                'FailedInvocations',
                'InvocationsCreated',
                'SuccessfulInvocationAttempts',
                'IngestionToInvocationStartLatency',
                'IngestionToInvocationCompleteLatency',
                'Invocations',
                'TriggeredRules'}
    metric_names_dynamodb = {x["MetricName"] for x in metrics_dynamodb}
    response = {'ConsumedReadCapacityUnits',
                'ProvisionedReadCapacityUnits',
                'TimeToLiveDeletedItemCount',
                'ProvisionedWriteCapacityUnits',
                'AccountProvisionedWriteCapacityUtilization',
                'MaxProvisionedTableReadCapacityUtilization',
                'MaxProvisionedTableWriteCapacityUtilization',
                'AccountMaxTableLevelWrites',
                'AccountMaxWrites',
                'UserErrors',
                'AccountMaxReads',
                'SuccessfulRequestLatency',
                'ConsumedWriteCapacityUnits',
                'AccountProvisionedReadCapacityUtilization',
                'AccountMaxTableLevelReads',
                'ReturnedItemCount'}
    """
    event-bridge-rule-alert_system_test_deploy_lambd Invocations == 5

    Events -> Across all rules -> FailedInvocations


    """

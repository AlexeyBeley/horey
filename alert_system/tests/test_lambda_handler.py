"""
Test lambda handler functionality.

"""

import pytest
from common import ses_events, cloudwatch_events, malformed_cloudwatch_events, self_monitoring_valid_events
from horey.alert_system.lambda_package.lambda_handler import handler
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy

# pylint: disable= missing-function-docstring


@pytest.mark.done
@pytest.mark.parametrize("ses_event", ses_events)
def test_lambda_handler(ses_event, alert_system_configuration_file_path_with_echo):
    AlertSystemConfigurationPolicy.ALERT_SYSTEM_CONFIGURATION_FILE_PATH = alert_system_configuration_file_path_with_echo
    event_handler = handler(ses_event, None)
    assert event_handler["statusCode"] == 200


@pytest.mark.done
@pytest.mark.parametrize("ses_event", ses_events)
def test_lambda_handler_slack_notification(ses_event, alert_system_configuration_file_path_with_slack):
    AlertSystemConfigurationPolicy.ALERT_SYSTEM_CONFIGURATION_FILE_PATH = alert_system_configuration_file_path_with_slack
    event_handler = handler(ses_event, None)
    assert event_handler["statusCode"] == 200


@pytest.mark.done
@pytest.mark.parametrize("cloudwatch_event", cloudwatch_events)
def test_lambda_handler_cloudwatch_events_echo(cloudwatch_event, alert_system_configuration_file_path_with_echo):
    AlertSystemConfigurationPolicy.ALERT_SYSTEM_CONFIGURATION_FILE_PATH = alert_system_configuration_file_path_with_echo
    event_handler = handler(cloudwatch_event, None)
    assert event_handler["statusCode"] == 200


@pytest.mark.done
@pytest.mark.parametrize("cloudwatch_event", malformed_cloudwatch_events)
def test_lambda_handler_malformed_cloudwatch_events_echo(cloudwatch_event, alert_system_configuration_file_path_with_echo):
    AlertSystemConfigurationPolicy.ALERT_SYSTEM_CONFIGURATION_FILE_PATH = alert_system_configuration_file_path_with_echo
    event_handler = handler(cloudwatch_event, None)
    assert event_handler["statusCode"] == 404


@pytest.mark.done
@pytest.mark.parametrize("cloudwatch_event", self_monitoring_valid_events)
def test_lambda_handler_self_monitoring_valid_events_echo(cloudwatch_event, alert_system_configuration_file_path_with_echo):
    AlertSystemConfigurationPolicy.ALERT_SYSTEM_CONFIGURATION_FILE_PATH = alert_system_configuration_file_path_with_echo
    event_handler = handler(cloudwatch_event, None)
    assert event_handler["statusCode"] == 200


@pytest.mark.done
@pytest.mark.parametrize("cloudwatch_event", self_monitoring_valid_events)
def test_lambda_handler_self_monitoring_valid_events_slack(cloudwatch_event, alert_system_configuration_file_path_with_slack):
    AlertSystemConfigurationPolicy.ALERT_SYSTEM_CONFIGURATION_FILE_PATH = alert_system_configuration_file_path_with_slack
    event_handler = handler(cloudwatch_event, None)
    assert event_handler["statusCode"] == 200


@pytest.mark.done
@pytest.mark.parametrize("cloudwatch_event", cloudwatch_events)
def test_lambda_handler_cloudwatch_message_message_override_notify_echo(cloudwatch_event,
                                                                        alert_system_configuration_file_path_message_override_notify_echo):
    AlertSystemConfigurationPolicy.ALERT_SYSTEM_CONFIGURATION_FILE_PATH = alert_system_configuration_file_path_message_override_notify_echo
    event_handler = handler(cloudwatch_event, None)
    assert event_handler["statusCode"] == 200

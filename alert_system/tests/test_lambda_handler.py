
import pytest
from common import ses_events, cloudwatch_events
from horey.alert_system.lambda_package.lambda_handler import lambda_handler
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy


@pytest.mark.done
@pytest.mark.parametrize("ses_event", ses_events)
def test_lambda_handler(ses_event, alert_system_configuration_file_path):
    AlertSystemConfigurationPolicy.ALERT_SYSTEM_CONFIGURATION_FILE_PATH = alert_system_configuration_file_path
    event_handler = lambda_handler(ses_event, None)
    assert event_handler["statusCode"] == 200


@pytest.mark.done
@pytest.mark.parametrize("ses_event", ses_events)
def test_lambda_handler_slack_notification(ses_event, alert_system_configuration_file_path_with_slack):
    AlertSystemConfigurationPolicy.ALERT_SYSTEM_CONFIGURATION_FILE_PATH = alert_system_configuration_file_path_with_slack
    event_handler = lambda_handler(ses_event, None)
    assert event_handler["statusCode"] == 200


@pytest.mark.wip
@pytest.mark.parametrize("cloudwatch_event", cloudwatch_events)
def test_lambda_handler_cloudwatch_events(cloudwatch_event, alert_system_configuration_file_path):
    AlertSystemConfigurationPolicy.ALERT_SYSTEM_CONFIGURATION_FILE_PATH = alert_system_configuration_file_path
    event_handler = lambda_handler(cloudwatch_event, None)
    assert event_handler["statusCode"] == 200

"""
Test message factory

"""
import pytest
from common import cloudwatch_events, cloudwatch_direct_alarm_events
from horey.alert_system.lambda_package.message_cloudwatch_default import MessageCloudwatchDefault
# pylint: disable= missing-function-docstring


@pytest.mark.done
@pytest.mark.parametrize("event", cloudwatch_events)
def test_init_message_ses_default(event, alert_system_configuration):
    message = MessageCloudwatchDefault(event, alert_system_configuration)
    assert isinstance(message, MessageCloudwatchDefault)


@pytest.mark.done
@pytest.mark.parametrize("event", cloudwatch_events)
def test_generate_notification(event, alert_system_configuration):
    message = MessageCloudwatchDefault(event, alert_system_configuration)
    notification = message.generate_notification()
    assert notification


@pytest.mark.done
@pytest.mark.parametrize("event", cloudwatch_events)
def test_generate_cooldown_trigger_name_and_epoch_timestamp(event, alert_system_configuration):
    message = MessageCloudwatchDefault(event, alert_system_configuration)
    trigger_name, float_timestamp = message.generate_cooldown_trigger_name_and_epoch_timestamp()
    assert isinstance(trigger_name, str)
    assert isinstance(float_timestamp, float)


@pytest.mark.done
@pytest.mark.parametrize("event", cloudwatch_direct_alarm_events)
def test_generate_notification_direct_alert(event, alert_system_configuration):
    message = MessageCloudwatchDefault(event, alert_system_configuration)
    notification = message.generate_notification()
    assert notification


@pytest.mark.done
@pytest.mark.parametrize("event", cloudwatch_direct_alarm_events)
def test_direct_alarm_generate_cooldown_trigger_name_and_epoch_timestamp(event, alert_system_configuration):
    message = MessageCloudwatchDefault(event, alert_system_configuration)
    try:
        response = message.generate_cooldown_trigger_name_and_epoch_timestamp()
        assert response
    except MessageCloudwatchDefault.NoCooldown:
        assert True

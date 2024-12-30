"""
Test message factory

"""
import pytest
from common import raw_sns_events
from horey.alert_system.lambda_package.message_raw import MessageRaw
# pylint: disable= missing-function-docstring


@pytest.mark.done
@pytest.mark.parametrize("raw_event", raw_sns_events)
def test_init_message_ses_default(raw_event, alert_system_configuration):
    message = MessageRaw(raw_event, alert_system_configuration)
    assert isinstance(message, MessageRaw)


@pytest.mark.done
@pytest.mark.parametrize("raw_event", raw_sns_events)
def test_generate_notification(raw_event, alert_system_configuration):
    message = MessageRaw(raw_event, alert_system_configuration)
    notification = message.generate_notification()
    assert notification

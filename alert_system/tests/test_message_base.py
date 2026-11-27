"""
Test message factory

"""
import pytest
from common import cloudwatch_direct_alarm_events
from horey.alert_system.lambda_package.message_base import MessageBase
# pylint: disable= missing-function-docstring


@pytest.mark.done
@pytest.mark.parametrize("event", cloudwatch_direct_alarm_events)
def test_init_message_ses_default(event, alert_system_configuration):
    message = MessageBase(event, alert_system_configuration)
    assert isinstance(message, MessageBase)


@pytest.mark.done
@pytest.mark.parametrize("event", cloudwatch_direct_alarm_events)
def test_extract_message_dict(event, alert_system_configuration):
    message = MessageBase(event, alert_system_configuration)
    dict_src = message.extract_message_dict(message._dict_src)
    assert dict_src

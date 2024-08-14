"""
Test message factory

"""
import pytest
from common import ses_events
from horey.alert_system.lambda_package.message_ses_default import MessageSESDefault
# pylint: disable= missing-function-docstring


@pytest.mark.done
@pytest.mark.parametrize("ses_event", ses_events)
def test_init_message_ses_default(ses_event):
    message = MessageSESDefault(ses_event)
    assert isinstance(message, MessageSESDefault)


@pytest.mark.done
@pytest.mark.parametrize("ses_event", ses_events)
def test_generate_notification(ses_event):
    message = MessageSESDefault(ses_event)
    notification = message.generate_notification()
    assert notification

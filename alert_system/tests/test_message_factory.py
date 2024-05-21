"""
Test message factory

"""
import pytest
from common import ses_events, zabbix_events
from horey.alert_system.lambda_package.message_factory import MessageFactory
from horey.alert_system.lambda_package.message_ses_default import MessageSESDefault
# pylint: disable= missing-function-docstring


@pytest.mark.wip
def test_init_message_factory():
    assert isinstance(MessageFactory(None), MessageFactory)


@pytest.mark.wip
@pytest.mark.parametrize("ses_event", ses_events)
def test_generate_message_ses_events(ses_event):
    message_factory = MessageFactory(None)
    message = message_factory.generate_message(ses_event)
    assert isinstance(message, MessageSESDefault)


@pytest.mark.wip
@pytest.mark.parametrize("zabbix_event", zabbix_events)
def test_generate_message_zabbix_events(zabbix_event):
    message_factory = MessageFactory(None)
    message = message_factory.generate_message(zabbix_event)
    assert message

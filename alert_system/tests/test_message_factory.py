"""
Test message factory

"""
from pathlib import Path

import pytest
from common import ses_events, zabbix_events, cloudwatch_events
from horey.alert_system.lambda_package.message_factory import MessageFactory
from horey.alert_system.lambda_package.message_ses_default import MessageSESDefault
# pylint: disable= missing-function-docstring


@pytest.mark.done
def test_init_message_factory(alert_system_configuration):
    assert isinstance(MessageFactory(alert_system_configuration), MessageFactory)


@pytest.mark.done
@pytest.mark.parametrize("ses_event", ses_events)
def test_generate_message_ses_events(ses_event, alert_system_configuration):
    message_factory = MessageFactory(alert_system_configuration)
    message = message_factory.generate_message(ses_event)
    assert isinstance(message, MessageSESDefault)


@pytest.mark.done
@pytest.mark.parametrize("zabbix_event", zabbix_events)
def test_generate_message_zabbix_events(zabbix_event, alert_system_configuration):
    message_factory = MessageFactory(alert_system_configuration)
    message = message_factory.generate_message(zabbix_event)
    assert message


@pytest.mark.done
@pytest.mark.parametrize("cloudwatch_event", cloudwatch_events)
def test_generate_message_cloudwatch_override(cloudwatch_event, alert_system_configuration):
    alert_system_configuration.message_classes = [Path(".").parent.joinpath("message_override.py")]
    message_factory = MessageFactory(alert_system_configuration)
    message = message_factory.generate_message(cloudwatch_event)
    notification = message.generate_notification()
    assert notification.header == "override"

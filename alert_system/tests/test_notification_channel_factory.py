"""
Notification channel factory
"""

import sys
import pytest
from horey.common_utils.common_utils import CommonUtils
from horey.alert_system.lambda_package.notification_channels.notification_channel_factory import NotificationChannelFactory
from horey.alert_system.lambda_package.notification_channels.notification_channel_echo import NotificationChannelEcho
from horey.alert_system.lambda_package.notification_channels.notification_channel_ses import NotificationChannelSES
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy
from horey.alert_system.lambda_package.notification_channels.notification_channel_slack import NotificationChannelSlack
import fixtures

# pylint: disable= missing-function-docstring


@pytest.mark.wip
def test_load_notification_channel_echo():
    factory = NotificationChannelFactory()
    notification_channel = factory.load_notification_channel(sys.modules[NotificationChannelEcho.__module__].__file__)
    assert notification_channel


@pytest.mark.wip
def test_load_notification_channels():
    factory = NotificationChannelFactory()
    configuration = AlertSystemConfigurationPolicy()
    configuration.notification_channels = [sys.modules[NotificationChannelEcho.__module__].__file__,
                                           sys.modules[NotificationChannelSES.__module__].__file__,
                                           sys.modules[NotificationChannelSlack.__module__].__file__]

    notification_channel = factory.load_notification_channels(configuration)
    assert notification_channel


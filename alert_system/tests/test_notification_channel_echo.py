"""
Ses channel tests
"""
import types

import pytest
from horey.alert_system.lambda_package.notification_channels.notification_channel_echo import NotificationChannelEcho, main
from horey.alert_system.lambda_package.notification import Notification
import fixtures

# pylint: disable= missing-function-docstring


@pytest.mark.wip
def test_notify_alert_system_error_exists():
    notification_channel = NotificationChannelEcho()
    assert isinstance(notification_channel.notify_alert_system_error, types.FunctionType) or isinstance(notification_channel.notify_alert_system_error, types.MethodType)


@pytest.mark.wip
def test_notify_exists():
    notification_channel = NotificationChannelEcho()
    assert isinstance(notification_channel.notify, types.FunctionType) or isinstance(notification_channel.notify, types.MethodType)


@pytest.mark.wip
@pytest.mark.parametrize("notification_type", Notification.Types)
def test_notify(notification_type):
    notification = Notification()
    notification.text = "test"
    notification.tags = ["test"]
    notification.type = notification_type
    notification_channel = NotificationChannelEcho()
    assert notification_channel.notify(notification)


@pytest.mark.wip
@pytest.mark.parametrize("notification_type", Notification.Types)
def test_notify_alert_system_error(notification_type):
    notification = Notification()
    notification.text = "test"
    notification.tags = ["test"]
    notification.type = notification_type
    notification_channel = NotificationChannelEcho()
    assert notification_channel.notify_alert_system_error(notification)


@pytest.mark.wip
def test_main_notify_alert_system_error_exists():
    notification_channel = main()
    assert isinstance(notification_channel.notify_alert_system_error, types.FunctionType) or isinstance(notification_channel.notify_alert_system_error, types.MethodType)


@pytest.mark.wip
def test_main_notify_exists():
    notification_channel = main()
    assert isinstance(notification_channel.notify, types.FunctionType) or isinstance(notification_channel.notify, types.MethodType)


@pytest.mark.wip
@pytest.mark.parametrize("notification_type", Notification.Types)
def test_main_init_notification_channel_echo(notification_type):
    notification = Notification()
    notification.text = "test"
    notification.tags = ["test"]
    notification.type = notification_type
    notification_channel = main()
    assert notification_channel.notify(notification)


@pytest.mark.wip
@pytest.mark.parametrize("notification_type", Notification.Types)
def test_main_notify_alert_system_error(notification_type):
    notification = Notification()
    notification.text = "test"
    notification.tags = ["test"]
    notification.type = notification_type
    notification_channel = main()
    assert notification_channel.notify_alert_system_error(notification)

"""
Message dispatcher tests.

"""
import sys
import json
import os
import shutil

import pytest
from horey.common_utils.common_utils import CommonUtils
from horey.alert_system.lambda_package.message_ses_default import MessageSESDefault
from horey.alert_system.lambda_package.message_dispatcher import MessageDispatcher
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy
from horey.alert_system.lambda_package.notification_channels.notification_channel_echo import NotificationChannelEcho


# pylint: disable= missing-function-docstring


@pytest.fixture(name="lambda_package_tmp_dir_ses")
def fixture_lambda_package_tmp_dir_message_dispatcher_ses():
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "horey", "alert_system", "lambda_package"))
    dst_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "lambda_package"))

    shutil.copytree(src_dir, dst_dir)
    shutil.copy2(os.path.join(os.path.dirname(__file__), "notification_channel_ses_configuration_values.py"), dst_dir)
    yield dst_dir
    shutil.rmtree(dst_dir)


@pytest.fixture(name="lambda_package_tmp_dir_echo")
def fixture_lambda_package_tmp_dir_message_dispatcher_echo():
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "horey", "alert_system", "lambda_package"))
    dst_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "lambda_package"))

    shutil.copytree(src_dir, dst_dir)
    shutil.copy2(os.path.join(os.path.dirname(__file__), "notification_channel_echo_configuration_values.py"), dst_dir)
    yield dst_dir
    shutil.rmtree(dst_dir)


@pytest.fixture(name="message_dispatcher")
def fixture_message_dispatcher():
    configuration = AlertSystemConfigurationPolicy()
    configuration.region = "us-west-2"
    configuration.notification_channels = [sys.modules[NotificationChannelEcho.__module__].__file__]
    message_dispatcher = MessageDispatcher(configuration)
    yield message_dispatcher


@pytest.mark.todo
def test_message_dispatcher_raises_notification_channels_not_set():
    configuration = AlertSystemConfigurationPolicy()
    configuration.region = "us-west-2"
    with pytest.raises(Exception, match=r".*Notification channels not configured!.*"):
        MessageDispatcher(configuration)


@pytest.mark.todo
def test_init_message_dispatcher_ses_notification_channel(lambda_package_tmp_dir_ses):
    message_dispatcher_file_path = os.path.join(lambda_package_tmp_dir_ses, "message_dispatcher.py")
    message_dispatcher = CommonUtils.load_object_from_module_raw(message_dispatcher_file_path, "MessageDispatcher")
    assert message_dispatcher.__name__ == "MessageDispatcher"


@pytest.mark.done
def test_init_message_dispatcher_echo_notification_channel(lambda_package_tmp_dir_echo):
    message_dispatcher_file_path = os.path.join(lambda_package_tmp_dir_echo, "message_dispatcher.py")
    message_dispatcher = CommonUtils.load_object_from_module_raw(message_dispatcher_file_path, "MessageDispatcher")
    assert message_dispatcher.__name__ == "MessageDispatcher"


ses_events_dir = os.path.join(os.path.dirname(__file__), "ses_messages")
ses_events = []
for file_name in os.listdir(ses_events_dir):
    with open(os.path.join(ses_events_dir, file_name), encoding="utf-8") as fh:
        _ses_event = json.load(fh)
        ses_events.append(_ses_event)


cloudwatch_events_dir = os.path.join(os.path.dirname(__file__), "raw_messages")
cloudwatch_events = []
for file_name in os.listdir(cloudwatch_events_dir):
    with open(os.path.join(cloudwatch_events_dir, file_name), encoding="utf-8") as fh:
        _ses_event = json.load(fh)
        cloudwatch_events.append(_ses_event)


@pytest.mark.todo
@pytest.mark.parametrize("ses_event", ses_events)
def test_init_message_dispatcher_ses_events(message_dispatcher, ses_event):
    message = MessageSESDefault(ses_event)
    assert message_dispatcher.dispatch(message)


@pytest.mark.todo
@pytest.mark.parametrize("cloudwatch_event", cloudwatch_events)
def test_init_message_dispatcher_cloudwatch_events(lambda_package_tmp_dir_echo, cloudwatch_event):
    message_dispatcher_file_path = os.path.join(lambda_package_tmp_dir_echo, "message_dispatcher.py")
    message_dispatcher = CommonUtils.load_object_from_module_raw(message_dispatcher_file_path, "MessageDispatcher")
    message = MessageSESDefault(cloudwatch_event)
    assert message_dispatcher.dispatch(message)


@pytest.mark.done
@pytest.mark.parametrize("ses_event", ses_events)
def test_generate_alert_system_exception_notification(message_dispatcher, ses_event):
    message = MessageSESDefault(ses_event)
    try:
        raise RuntimeError("Test")
    except Exception as error_inst:
        notification = message_dispatcher.generate_alert_system_exception_notification(error_inst, message)
        assert notification.text
        assert notification.type == notification.Types.CRITICAL

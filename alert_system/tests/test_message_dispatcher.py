"""
Message dispatcher tests.

"""
import json
import os
import shutil

import pytest
from horey.common_utils.common_utils import CommonUtils
from horey.alert_system.lambda_package.message import Message
from horey.alert_system.lambda_package.notification_channel_base import NotificationChannelBase

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
    with open(os.path.join(ses_events_dir, file_name)) as fh:
        ses_event = json.load(fh)
        ses_events.append(ses_event)


cloudwatch_events_dir = os.path.join(os.path.dirname(__file__), "raw_messages")
cloudwatch_events = []
for file_name in os.listdir(cloudwatch_events_dir):
    with open(os.path.join(cloudwatch_events_dir, file_name)) as fh:
        ses_event = json.load(fh)
        cloudwatch_events.append(ses_event)


@pytest.mark.wip
@pytest.mark.parametrize("ses_event", ses_events)
def test_init_message_dispatcher_ses_events(lambda_package_tmp_dir_echo, ses_event):
    message_dispatcher_file_path = os.path.join(lambda_package_tmp_dir_echo, "message_dispatcher.py")
    message_dispatcher_class = CommonUtils.load_object_from_module_raw(message_dispatcher_file_path, "MessageDispatcher")
    message = Message(ses_event)
    assert message.type == Message.Types.SES_DEFAULT
    os.environ[NotificationChannelBase.NOTIFICATION_CHANNELS_ENVIRONMENT_VARIABLE] = "notification_channel_echo.py"
    message_dispatcher = message_dispatcher_class()

    assert message_dispatcher.dispatch(message)


@pytest.mark.todo
@pytest.mark.parametrize("cloudwatch_event", cloudwatch_events)
def test_init_message_dispatcher_cloudwatch_events(lambda_package_tmp_dir_echo, cloudwatch_event):
    message_dispatcher_file_path = os.path.join(lambda_package_tmp_dir_echo, "message_dispatcher.py")
    message_dispatcher = CommonUtils.load_object_from_module_raw(message_dispatcher_file_path, "MessageDispatcher")
    message = Message(ses_event)
    assert message.type == Message.Types.SES_DEFAULT
    assert message_dispatcher.dispatch(message)

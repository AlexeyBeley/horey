"""
Message dispatcher tests.

"""
import datetime
import sys
import json
import os
import shutil
from unittest.mock import patch

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
def test_init_message_dispatcher_ses_events(message_dispatcher, ses_event, alert_system_configuration):
    message = MessageSESDefault(ses_event, alert_system_configuration)
    assert message_dispatcher.dispatch(message)


@pytest.mark.todo
@pytest.mark.parametrize("cloudwatch_event", cloudwatch_events)
def test_init_message_dispatcher_cloudwatch_events(lambda_package_tmp_dir_echo, cloudwatch_event, alert_system_configuration):
    message_dispatcher_file_path = os.path.join(lambda_package_tmp_dir_echo, "message_dispatcher.py")
    message_dispatcher = CommonUtils.load_object_from_module_raw(message_dispatcher_file_path, "MessageDispatcher")
    message = MessageSESDefault(cloudwatch_event, alert_system_configuration)
    assert message_dispatcher.dispatch(message)


@pytest.mark.done
@pytest.mark.parametrize("ses_event", ses_events)
def test_generate_alert_system_exception_notification(message_dispatcher, ses_event, alert_system_configuration):
    message = MessageSESDefault(ses_event, alert_system_configuration)
    try:
        raise RuntimeError("Test")
    except Exception as error_inst:
        notification = message_dispatcher.generate_alert_system_exception_notification(error_inst, message)
        assert notification.text
        assert notification.type == notification.Types.CRITICAL


@pytest.mark.done
def test_update_dynamodb_alarm_time(alert_system_configuration):
    message_dispatcher = MessageDispatcher(alert_system_configuration)
    time_now = datetime.datetime.now(datetime.timezone.utc)
    timestamp = time_now.timestamp()
    assert message_dispatcher.update_dynamodb_alarm_time("test_alarm_name_1", timestamp)


@pytest.mark.done
def test_delete_dynamodb_alarm(alert_system_configuration):
    message_dispatcher = MessageDispatcher(alert_system_configuration)
    assert message_dispatcher.delete_dynamodb_alarm("test_alarm_name_1")


@pytest.mark.done
def test_yield_dynamodb_items(alert_system_configuration):
    message_dispatcher = MessageDispatcher(alert_system_configuration)
    for item in message_dispatcher.yield_dynamodb_items():
        assert item
        break


def yield_dynamodb_items_mock():
    time_now = datetime.datetime.now(datetime.timezone.utc)
    timestamp_now = time_now.timestamp()
    lst_ret = []
    dict_key = {"alarm_name": "alarm_name_expired_300",
                "alarm_state":
                    {"cooldown_time": 300,
                     "epoch_triggered": timestamp_now-301}}
    lst_ret.append(dict_key)

    dict_key = {"alarm_name": "alarm_name_expired_3600",
                "alarm_state":
                    {"cooldown_time": 3600,
                     "epoch_triggered": timestamp_now - 3601}}
    lst_ret.append(dict_key)

    dict_key = {"alarm_name": "alarm_name_not_expired_300",
                "alarm_state":
                    {"cooldown_time": 300,
                     "epoch_triggered": timestamp_now}}
    lst_ret.append(dict_key)

    yield from lst_ret


@pytest.mark.done
def test_run_dynamodb_update_routine(alert_system_configuration):
    message_dispatcher = MessageDispatcher(alert_system_configuration)
    message_dispatcher.yield_dynamodb_items = yield_dynamodb_items_mock
    with patch("horey.aws_api.aws_clients.cloud_watch_client.CloudWatchClient.set_alarm_ok") as mock_set_alarm_ok:
        assert message_dispatcher.run_dynamodb_update_routine()
        assert len(mock_set_alarm_ok.mock_calls) == 2
        assert mock_set_alarm_ok.mock_calls[0].args[0].name == "alarm_name_expired_300"
        assert mock_set_alarm_ok.mock_calls[1].args[0].name == "alarm_name_expired_3600"


@pytest.mark.wip
def test_handle_exception(alert_system_configuration):
    message_dispatcher = MessageDispatcher(alert_system_configuration)
    with pytest.raises(RuntimeError, match=r".Exception in Message Dispatcher.*"):
        message_dispatcher.handle_exception(ValueError("test"), {})

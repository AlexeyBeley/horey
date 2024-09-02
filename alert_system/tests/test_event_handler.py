"""
Message dispatcher tests.

"""
import datetime
import json
import os
import sys
import shutil
import pytest
from unittest.mock import Mock
from horey.alert_system.lambda_package.event_handler import EventHandler
from horey.alert_system.lambda_package.notification_channels.notification_channel_echo import NotificationChannelEcho
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy

# pylint: disable= missing-function-docstring


@pytest.fixture(name="lambda_package_alert_system_config_file")
def fixture_lambda_package_alert_system_config_file():
    dst_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "lambda_package"))
    if os.path.isdir(dst_dir):
        shutil.rmtree(dst_dir)
    os.makedirs(dst_dir)
    dict_config = {"region": "us-west-2",
                   "notification_channels": [sys.modules[NotificationChannelEcho.__module__].__file__]}
    alert_system_config_file_path = os.path.join(dst_dir, AlertSystemConfigurationPolicy.ALERT_SYSTEM_CONFIGURATION_FILE_PATH)
    with open(alert_system_config_file_path, "w", encoding="utf-8") as file_handler:
        json.dump(dict_config, file_handler)

    yield alert_system_config_file_path
    shutil.rmtree(dst_dir)


@pytest.mark.done
def test_init_event_handler(lambda_package_alert_system_config_file):
    event_handler = EventHandler(lambda_package_alert_system_config_file)
    assert event_handler


@pytest.mark.done
def test_handle_event(lambda_package_alert_system_config_file):
    event_handler = EventHandler(lambda_package_alert_system_config_file)
    dir_name = os.path.join(os.path.dirname(__file__), "cloudwatch_messages")
    file_path = os.path.join(dir_name, "alert_system_self_alert_event.json")
    with open(file_path, encoding="utf-8") as file_handler:
        event = json.load(file_handler)
    assert event_handler.handle_event(event)


@pytest.mark.done
def test_handle_event_bridge_event_raise_alert_not_found(alert_system_configuration_file_path_with_echo, event_bridge_events):
    event_handler = EventHandler(alert_system_configuration_file_path_with_echo)
    time_now = datetime.datetime.now(datetime.timezone.utc)
    timestamp_now = time_now.timestamp()
    event_handler.message_dispatcher.update_dynamodb_alarm_time("test_alarm_name_1", timestamp_now-301)
    event_handler.message_dispatcher.delete_dynamodb_alarm = Mock()

    for event in event_bridge_events:
        event_handler.handle_event(event)
        event_handler.message_dispatcher.delete_dynamodb_alarm.assert_called()


@pytest.mark.todo
def test_handle_event_bridge_event(alert_system_configuration_file_path_with_echo, event_bridge_events):
    event_handler = EventHandler(alert_system_configuration_file_path_with_echo)
    for event in event_bridge_events:
        assert event_handler.handle_event(event)

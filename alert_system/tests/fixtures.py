import json
import os
import shutil
import sys

import pytest
from horey.alert_system.lambda_package.notification_channels.notification_channel_echo import NotificationChannelEcho
from horey.alert_system.lambda_package.event_handler import EventHandler


@pytest.fixture(name="lambda_package_alert_system_config_file")
def fixture_lambda_package_alert_system_config_file():
    dst_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lambda_package"))
    if os.path.isdir(dst_dir):
        shutil.rmtree(dst_dir)
    os.makedirs(dst_dir)
    dict_config = {"region": "us-west-2",
                   "notification_channels": [sys.modules[NotificationChannelEcho.__module__].__file__]}
    alert_system_config_file_path = os.path.join(dst_dir, EventHandler.ALERT_SYSTEM_CONFIGURATION_FILE_NAME)
    with open(alert_system_config_file_path, "w") as file_handler:
        json.dump(dict_config, file_handler)

    yield alert_system_config_file_path
    shutil.rmtree(dst_dir)


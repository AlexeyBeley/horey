"""
Message dispatcher tests.

"""
import json
import os
import shutil

import pytest
from horey.common_utils.common_utils import CommonUtils
from horey.alert_system.lambda_package.message_ses_default import MessageSESDefault
from horey.alert_system.lambda_package.message_dispatcher import MessageDispatcher
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy
from horey.alert_system.lambda_package.notification_channel_base import NotificationChannelBase

# pylint: disable= missing-function-docstring


@pytest.fixture(name="lambda_package_tmp_dir_echo")
def fixture_lambda_package_tmp_dir():
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "horey", "alert_system", "lambda_package"))
    dst_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "lambda_package"))
    shutil.rmtree(dst_dir)

    shutil.copytree(src_dir, dst_dir)
    shutil.copy2(os.path.join(os.path.dirname(__file__), "notification_channel_echo_configuration_values.py"), dst_dir)
    yield dst_dir
    shutil.rmtree(dst_dir)


@pytest.mark.todo
def test_init_message_dispatcher_ses_notification_channel(fixture_lambda_package_tmp_dir):
    message_dispatcher_file_path = os.path.join(lambda_package_tmp_dir_ses, "message_dispatcher.py")
    message_dispatcher = CommonUtils.load_object_from_module_raw(message_dispatcher_file_path, "MessageDispatcher")
    assert message_dispatcher.__name__ == "MessageDispatcher"

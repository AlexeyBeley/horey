"""
Ses channel tests
"""
import os
import shutil

import pytest
from horey.common_utils.common_utils import CommonUtils

# pylint: disable= missing-function-docstring


@pytest.fixture(name="lambda_package_tmp_dir")
def fixture_lambda_package_tmp_dir_message_dispatcher():
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "horey", "alert_system", "lambda_package"))
    dst_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "lambda_package"))

    shutil.copytree(src_dir, dst_dir)
    shutil.copy2(os.path.join(os.path.dirname(__file__), "notification_channel_ses_configuration_values.py"), dst_dir)
    yield dst_dir
    shutil.rmtree(dst_dir)


@pytest.mark.done
def test_init_notification_channel_ses(lambda_package_tmp_dir):
    message_dispatcher_base_file_path = os.path.join(lambda_package_tmp_dir, "notification_channel_ses.py")
    message_dispatcher_base = CommonUtils.load_object_from_module_raw(message_dispatcher_base_file_path, "NotificationChannelSES")
    assert message_dispatcher_base.__name__ == "NotificationChannelSES"


@pytest.mark.done
def test_map_routing_tag_to_destinations(lambda_package_tmp_dir):
    message_dispatcher_base_file_path = os.path.join(lambda_package_tmp_dir, "notification_channel_ses.py")
    notification_channel_class = CommonUtils.load_object_from_module_raw(message_dispatcher_base_file_path, "NotificationChannelSES")

    config_policy_file_name = notification_channel_class.__module__ + "_configuration_policy"
    config_policy_path = os.path.join(lambda_package_tmp_dir, config_policy_file_name)
    class_name = notification_channel_class.__name__ + "ConfigurationPolicy"
    config_values_file_name = notification_channel_class.__module__ + "_configuration_values.py"
    config_policy = CommonUtils.load_object_from_module(
        config_policy_path,
        class_name
    )
    config_policy.configuration_file_full_path = config_values_file_name

    config_policy.init_from_file()

    notification_channel = notification_channel_class(config_policy)
    ret = notification_channel.map_routing_tag_to_destinations("team_front")
    assert ret == ["team_front@common.com"]


@pytest.mark.done
def test_send_email(lambda_package_tmp_dir):
    message_dispatcher_base_file_path = os.path.join(lambda_package_tmp_dir, "notification_channel_ses.py")
    notification_channel_class = CommonUtils.load_object_from_module_raw(message_dispatcher_base_file_path, "NotificationChannelSES")

    config_policy_file_name = notification_channel_class.__module__ + "_configuration_policy"
    config_policy_path = os.path.join(lambda_package_tmp_dir, config_policy_file_name)
    class_name = notification_channel_class.__name__ + "ConfigurationPolicy"
    config_values_file_name = notification_channel_class.__module__ + "_configuration_values.py"
    config_policy = CommonUtils.load_object_from_module(
        config_policy_path,
        class_name
    )
    config_policy.configuration_file_full_path = config_values_file_name

    config_policy.init_from_file()

    notification_channel = notification_channel_class(config_policy)

    notification_file_path = os.path.join(lambda_package_tmp_dir, "notification.py")
    notification_class = CommonUtils.load_object_from_module_raw(notification_file_path, "Notification")
    notification = notification_class()
    notification.header = "header test"
    notification.text = "body test"
    notification_channel.configuration.src_email = "horey@common.com"
    notification_channel.configuration.alert_system_monitoring_destination = "horey@common.com"

    notification_channel.send_email(notification, ["horey@common.com"])


@pytest.mark.done
def test_notify(lambda_package_tmp_dir):
    message_dispatcher_base_file_path = os.path.join(lambda_package_tmp_dir, "notification_channel_ses.py")
    notification_channel_class = CommonUtils.load_object_from_module_raw(message_dispatcher_base_file_path, "NotificationChannelSES")

    config_policy_file_name = notification_channel_class.__module__ + "_configuration_policy"
    config_policy_path = os.path.join(lambda_package_tmp_dir, config_policy_file_name)
    class_name = notification_channel_class.__name__ + "ConfigurationPolicy"
    config_values_file_name = notification_channel_class.__module__ + "_configuration_values.py"
    config_policy = CommonUtils.load_object_from_module(
        config_policy_path,
        class_name
    )
    config_policy.configuration_file_full_path = config_values_file_name

    config_policy.init_from_file()

    notification_channel = notification_channel_class(config_policy)

    notification_file_path = os.path.join(lambda_package_tmp_dir, "notification.py")
    notification_class = CommonUtils.load_object_from_module_raw(notification_file_path, "Notification")
    notification = notification_class()
    notification.routing_tags = ["frontend"]
    notification.header = "Notification "
    notification.type = "PARTY"
    notification.text = "body Notification"
    notification_channel.configuration.src_email = "horey@common.com"
    notification_channel.configuration.alert_system_monitoring_destination ="horey@common.com"
    notification_channel.configuration.routing_tag_to_email_mapping = {"frontend": "horey@common.com"}

    notification_channel.notify(notification)

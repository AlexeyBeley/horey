"""
Module handling most of the basic message behavior.
Checks message type to invoke relevant handler.
Sends the notification to the channels.

"""

import datetime
import json
import os
import traceback
import urllib.parse

from horey.alert_system.lambda_package.notification_channels.notification_channel_factory import NotificationChannelFactory
from horey.alert_system.lambda_package.notification import Notification

from horey.common_utils.common_utils import CommonUtils
from horey.h_logger import get_logger

logger = get_logger()


class MessageDispatcher:
    """
    Main class.

    """

    def __init__(self, configuration):
        self.configuration = configuration
        self.notification_channels = []
        if not self.init_notification_channels():
            raise RuntimeError("No notification channels configured")

    def init_notification_channels(self):
        """
        i
        :return:
        """
        if not self.configuration.notification_channels:
            raise ValueError(f"Notification channels not configured! {self.configuration.notification_channels=}")

        self.notification_channels = NotificationChannelFactory().load_notification_channels(self.configuration)

        return len(self.notification_channels) > 0 and \
            len(self.notification_channels) == len(self.configuration.notification_channels)

    @staticmethod
    def load_notification_channel(file_name):
        """
        Load notification channel class from python module.

        @param file_name:
        @return:
        """

        module_obj = CommonUtils.load_module(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
        )
        candidates = []
        for attr_name in module_obj.__dict__:
            if attr_name == "NotificationChannelBase":
                continue
            if attr_name.startswith("NotificationChannel"):
                candidate = getattr(module_obj, attr_name)
                if issubclass(candidate, NotificationChannelBase) or "NotificationChannelBase" in str(candidate.__weakref__):
                    candidates.append(candidate)

        if len(candidates) != 1:
            raise RuntimeError(f"Found {candidates} in {file_name}")

        return candidates[0]

    @staticmethod
    def init_notification_channel(notification_channel_class):
        """
        Load configuration file and init notification channel with configuration file.

        @param notification_channel_class:
        @return:
        """
        try:
            config_policy_file_name = notification_channel_class.CONFIGURATION_POLICY_FILE_NAME
            class_name = notification_channel_class.CONFIGURATION_POLICY_CLASS_NAME
        except AttributeError:
            config_policy_file_name = notification_channel_class.__module__ + "_configuration_policy"
            class_name = notification_channel_class.__name__ + "ConfigurationPolicy"

        config_policy_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            config_policy_file_name
        )

        config_policy = CommonUtils.load_object_from_module(
            config_policy_path,
            class_name
        )
        try:
            config_values_file_name = config_policy.CONFIGURATION_FILE_NAME
        except AttributeError:
            config_values_file_name = notification_channel_class.__module__ + "_configuration_values.py"

        config_policy.configuration_file_full_path = (
            config_values_file_name
        )
        config_policy.init_from_file()

        return notification_channel_class(config_policy)

    def dispatch(self, message):
        """
        Route the message to relevant notification channels.§

        @param message:
        @return:
        """

        try:
            notification = message.generate_notification()
            for notification_channel in self.notification_channels:
                notification_channel.notify(notification)
        except Exception as error_inst:
            notification = self.generate_alert_system_exception_notification(error_inst, message)

            for notification_channel in self.notification_channels:
                notification_channel.notify_alert_system_error(notification)
            raise RuntimeError("Exception in Message Dispatcher") from error_inst

        return True

    @staticmethod
    def generate_alert_system_exception_notification(error_inst, message):
        """
        Generate notification about alert system exception
        :return:
        """

        traceback_str = "".join(traceback.format_tb(error_inst.__traceback__))
        logger.exception(f"{traceback_str}\n{repr(error_inst)}")

        try:
            text = json.dumps(message.convert_to_dict(), indent=4)
        except Exception as internal_exception:
            text = f"Could not convert message to dict: error: {repr(internal_exception)}, message: {str(message)}"

        notification = Notification()
        notification.type = Notification.Types.CRITICAL
        notification.header = "Unhandled message in alert_system"
        notification.text = text
        return notification

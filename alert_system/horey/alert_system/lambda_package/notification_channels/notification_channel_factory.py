"""
Message being received by the Alert System Lambda.

"""

from horey.h_logger import get_logger
from horey.common_utils.common_utils import CommonUtils

logger = get_logger()


class NotificationChannelFactory:
    """
    Main class.

    """

    def load_notification_channels(self, configuration):
        """

        :return:
        """

        return [self.load_notification_channel(file_path) for file_path in configuration.notification_channels]

    def load_notification_channel(self, initializer_file_path):
        """
        Init notification channel from initializer file path

        :param initializer_file_path:
        :return:
        """

        notification_channel = CommonUtils.load_object_from_module(initializer_file_path, "main")
        return notification_channel

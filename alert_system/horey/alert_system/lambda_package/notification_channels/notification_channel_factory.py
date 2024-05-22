"""
Message being received by the Alert System Lambda.

"""

from horey.h_logger import get_logger
from horey.alert_system.lambda_package.message_ses_default import MessageSESDefault
from horey.alert_system.lambda_package.message_zabbix_default import MessageZabbixDefault
from horey.alert_system.lambda_package.message_base import MessageBase

logger = get_logger()


class NotificationChannelFactory:
    """
    Main class.

    """

    def __init__(self, configuration):
        self.configuration = configuration

    def load_notification_channels(self):
        """

        :return:
        """
        breakpoint()

    def load_notification_channel(self, initializer_file_path):
        """
        Init notification channel from initializer file path

        :param initializer_file_path:
        :return:
        """
        breakpoint()
        for message_class in self.message_classes:
            try:
                return message_class.init_from_dict(dict_event)
            except MessageBase.NotAMatchError:
                pass
        raise ValueError(f"Can not find message generator for event: {dict_event}")







        #for message_class in self.message_classes:

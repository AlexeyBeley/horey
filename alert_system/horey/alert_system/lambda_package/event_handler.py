"""
Event Handler.
"""

from horey.alert_system.lambda_package.message_dispatcher import MessageDispatcher
from horey.alert_system.lambda_package.message_factory import MessageFactory
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy

from horey.h_logger import get_logger
logger = get_logger()


class EventHandler:
    """
    Class handling the received events.

    """

    ALERT_SYSTEM_CONFIGURATION_FILE_NAME = "alert_system_configuration.json"

    def __init__(self):
        configuration = AlertSystemConfigurationPolicy()
        configuration.configuration_file_full_path = self.ALERT_SYSTEM_CONFIGURATION_FILE_NAME
        configuration.init_from_file()

        self.message_factory = MessageFactory(configuration)
        self.message_dispatcher = MessageDispatcher(configuration)

    def handle_event(self, event):
        """
        Handle the received event.

        @param event:
        @return:
        """

        message = self.message_factory.generate_message(event)
        return self.message_dispatcher.dispatch(message)



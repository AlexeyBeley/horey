"""
Event Handler.
"""

import traceback
from horey.alert_system.lambda_package.message import Message

from horey.alert_system.lambda_package.message_dispatcher import MessageDispatcher
from horey.alert_system.lambda_package.message_factory import MessageFactory
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy

from horey.h_logger import get_logger
logger = get_logger()


class EventHandler:
    """
    Class handling the received events.

    """

    def __init__(self):
        configuration = AlertSystemConfigurationPolicy()
        self.message_factory = MessageFactory(configuration)
        self.message_dispatcher = MessageDispatcher(configuration)

    def handle_event(self, event):
        """
        Handle the received event.

        @param event:
        @return:
        """

        message = self.extract_message(event)
        return self.message_dispatcher.dispatch(message)

    def extract_message(self, event):
        """
        Build Message object from the event dictionary.

        @param event:
        @return:
        """

        if "Records" in event:
            return self.extract_message_records(event)
        raise NotImplementedError(event)

    def extract_message_records(self, event):
        """
        For cloudwatch message - convert records to Message objects.

        @param event:
        @return:
        """

        message = Message(dic_src=event)
        try:
            message.init_from_dict()
        except Exception as error_inst:
            traceback_str = "".join(traceback.format_tb(error_inst.__traceback__))
            logger.exception(f"{traceback_str}\n{repr(error_inst)}")

        return message


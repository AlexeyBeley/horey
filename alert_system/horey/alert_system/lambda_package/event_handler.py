import json
import traceback
from message import Message

try:
    from message_dispatcher import MessageDispatcher
except ModuleNotFoundError:
    from message_dispatcher_base import MessageDispatcherBase as MessageDispatcher


class EventHandler:
    """
    Class handling the received events.

    """

    def __init__(self, logger):
        self.logger = logger
        self.message_dispatcher = MessageDispatcher()

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
            self.logger.exception(f"{traceback_str}\n{repr(error_inst)}")

        return message


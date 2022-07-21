import pdb

from .base_message_dispatcher import BaseMessageDispatcher


class MessageDispatcher(BaseMessageDispatcher):
    def __init__(self):
        super(MessageDispatcher, self).__init__()
        self.handler_mapper["queue_1"] = self.queue_handler

    def queue_handler(self, message):
        pdb.set_trace()



import pdb

from base_message_dispatcher import BaseMessageDispatcher
from horey.h_logger import get_logger

logger = get_logger()


class MessageDispatcher(BaseMessageDispatcher):
    def __init__(self):
        super(MessageDispatcher, self).__init__()



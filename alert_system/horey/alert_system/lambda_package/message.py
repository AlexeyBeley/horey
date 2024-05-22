"""
Message being received by the Alert System Lambda.

"""

import uuid
import json
from enum import Enum
from horey.common_utils.common_utils import CommonUtils
from horey.h_logger import get_logger

logger = get_logger()


class Message:
    """
    Main class.

    """

    def __init__(self, dic_src):
        self._dict_src = dic_src
        self._uuid = None
        self._data = None
        self._type = None
        self.records = None
        try:
            del dic_src["dict_src"]
        except KeyError:
            pass
        self.init_from_dict()

    @property
    def uuid(self):
        """
        Unique identifier for one instance of the message family marked by "type"
        For example multiple cloud_watch_log messages.

        @return:
        """

        return self._uuid

    @uuid.setter
    def uuid(self, value):
        """
        UUID setter.

        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(value)
        self._uuid = value

    @property
    def data(self):
        """
        Dictionary you operate to customize the message handling.

        @param value:
        @return:
        """

        return self._data

    @data.setter
    def data(self, value):
        """
        Data setter.

        @param value:
        @return:
        """

        if not isinstance(value, dict):
            raise ValueError(value)
        self._data = value

    @property
    def type(self):
        """
        Used to map the message to appropriate handling function.

        @return:
        """
        return self._type

    @type.setter
    def type(self, type_value):
        """
        Type setter.

        @param type_value:
        @return:
        """

        if type_value.value not in [msg_type.value for msg_type in Message.Types]:
            raise ValueError(type_value)
        self._type = type_value

    @property
    def dict_src(self):
        """
        Source dict of the message- needed for debugging in case the message has proceeding issues.

        @return:
        """

        return self._dict_src

    @dict_src.setter
    def dict_src(self, value):
        """
        dict_src setter.

        @param value:
        @return:
        """

        self._dict_src = value

    def generate_uuid(self):
        """
        Generate UID to mark the specific message implementation.

        @return:
        """

        self.uuid = str(uuid.uuid4())

    def init_from_dict(self):
        """
        Init the message from dictionary.

        @return:
        """

        if len(self.dict_src["Records"]) != 1:
            raise RuntimeError(self.dict_src)

        record = self.dict_src["Records"][0]
        if record["EventSource"] != "aws:sns":
            raise NotImplementedError(self.dict_src)

        dict_message_raw = json.loads(record["Sns"]["Message"])
        if "AlarmDescription" in dict_message_raw:
            breakpoint()
            self.type = Message.Types.CLOUDWATCH_DEFAULT
            try:
                dict_message = json.loads(dict_message_raw["AlarmDescription"])
            except Exception:
                logger.warning(
                    f"Was not able to json load AlarmDescription: {dict_message_raw}"
                )
                return
        elif "mail" in dict_message_raw:
            dict_message = dict_message_raw
            self.type = Message.Types.SES_DEFAULT
        else:
            breakpoint()
            dict_message = {}
            self.type = Message.Types.UNKNOWN

        for key, value in dict_message.items():
            setattr(self, CommonUtils.camel_case_to_snake_case(key), value)

    class Types(Enum):
        """
        Message types
        """

        SES_DEFAULT = "ses_default"
        CLOUDWATCH_DEFAULT = "cloudwatch_default"
        UNKNOWN = "unknown"

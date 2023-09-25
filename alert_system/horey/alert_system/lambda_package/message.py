"""
Message being received by the Alert System Lambda.

"""

import uuid
import json
from horey.common_utils.common_utils import CommonUtils
from horey.h_logger import get_logger

logger = get_logger()


class Message:
    """
    Main class.

    """

    def __init__(self, dic_src=None):
        self._dict_src = dic_src
        self._uuid = None
        self._data = None
        self._type = None

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
    def type(self, value):
        """
        Type setter.

        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(value)
        self._type = value

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

    def init_from_dict(self, dict_src):
        """
        Init the message from dictionary.

        @param dict_src:
        @return:
        """

        if "AlarmDescription" in dict_src:
            self.type = "cloudwatch_default"
            try:
                dict_src = json.loads(dict_src["AlarmDescription"])
            except Exception:
                logger.warning(
                    f"Was not able to json load AlarmDescription: {dict_src}"
                )
                return

        try:
            del dict_src["dict_src"]
        except KeyError:
            pass

        for key, value in dict_src.items():
            setattr(self, CommonUtils.camel_case_to_snake_case(key), value)

        self.init_default_type()

    def init_default_type(self):
        """
        Init type based on message structure.

        @return:
        """

        if self.type is not None:
            return

        if hasattr(self, "bounce"):
            self.type = "ses_default"
            return

        raise NotImplementedError(self.dict_src)

    def convert_to_dict(self):
        """
        Convert the message to dict.

        @return:
        """

        return {
            key[1:]: value
            for key, value in self.__dict__.items()
            if key.startswith("_")
        }

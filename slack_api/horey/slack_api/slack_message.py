import pdb
import json
from horey.h_logger import get_logger
from enum import Enum
logger = get_logger()


class SlackMessage:
    def __init__(self):
        self._type = None
        self.message = None
        self.subject = None
        self.src_username = None
        self.dst_channel = None
        self._text_color = None
        self._icon_emoji = None

    def convert_to_json(self):
        return json.dumps(self.convert_to_dict())
    
    def convert_to_dict(self):

        slack_data = {"text": self.subject,
                      "attachments": [{
                          "text": self.message,
                          "color": self.text_color,
                      }],
                      "channel": self.dst_channel,
                      "username": self.src_username,
                      "icon_emoji": self.icon_emoji
                      }
        pdb.set_trace()
        return slack_data

    def init_from_dict(self, dict_src):
        pdb.set_trace()

    @property
    def type(self):
        if self._type is None:
            raise ValueError("type was not set")
        return self._type

    @type.setter
    def type(self, value):
        if not isinstance(value, str):
            raise ValueError(f"type must be string received {value} of type: {type(value)}")

        self._type = value

    @property
    def text_color(self):
        if self._text_color is None:
            if self.type == self.Types.STABLE:
                self._text_color = "#7CD197"
            elif self.type == self.Types.WARNING:
                self._text_color = "danger"
            elif self.type == self.Types.CRITICAL:
                self._text_color = "danger"
            else:
                raise RuntimeError(f"Unknown type: {self.type}")
        
        return self._text_color

    @text_color.setter
    def text_color(self, value):
        if not isinstance(value, str):
            raise ValueError(f"text_color must be string received {value} of text_color: {type(value)}")

        self._text_color = value

    @property
    def icon_emoji(self):
        if self._icon_emoji is None:
            if self.type == self.Types.STABLE:
                self._icon_emoji = ":white_check_mark:"
            elif self.type == self.Types.WARNING:
                self._icon_emoji = ":bangbang:"
            elif self.type == self.Types.CRITICAL:
                self._icon_emoji = ":bangbang:"
            else:
                raise RuntimeError(f"Unknown type: {self.type}")
        return self._icon_emoji

    @icon_emoji.setter
    def icon_emoji(self, value):
        if not isinstance(value, str):
            raise ValueError(f"icon_emoji must be string received {value} of icon_emoji: {type(value)}")

        self._icon_emoji = value

    class Types(Enum):
        STABLE = 0
        WARNING = 1
        CRITICAL = 2

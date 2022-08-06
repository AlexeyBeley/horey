import pdb
from enum import Enum


class Notification:
    def __init__(self):
        self._type = None
        self._text = None
        self._header = None
        self._link = None
        self._link_href = None
        self._tags = None

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, value):
        if not isinstance(value, str):
            raise ValueError(value)
        self._tags = value

    @property
    def link_href(self):
        return self._link_href

    @link_href.setter
    def link_href(self, value):
        if not isinstance(value, str):
            raise ValueError(value)
        self._link_href = value

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, value):
        if not isinstance(value, str):
            raise ValueError(value)
        self._link = value

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, value):
        if not isinstance(value, str):
            raise ValueError(value)
        self._header = value
        
    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if not isinstance(value, str):
            raise ValueError(value)
        self._text = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        pdb.set_trace()
        Notification.Types
        self._type = value

    class Types(Enum):
        INFO = "INFO"
        STABLE = "STABLE"
        WARNING = "WARNING"
        CRITICAL = "CRITICAL"
        PARTY = "PARTY"

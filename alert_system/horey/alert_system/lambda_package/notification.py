"""
Notification to be sent as a message dispatching result.

"""

from enum import Enum


class Notification:
    """
    Main class.

    """
    ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG = "ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG"

    def __init__(self):
        self._type = None
        self._text = None
        self._header = None
        self._link = None
        self._link_href = None
        self._routing_tags = None

    def print(self):
        """
        Pretty print.

        :return:
        """

        str_ret = "\n".join([f"{attr_name}: {getattr(self, attr_name)}" for attr_name in ["type",
                                                                                       "header",
                                                                                       "routing_tags",
                                                                                       "link_href",
                                                                                       "link",
                                                                                       "text"]])
        print(str_ret)
        return str_ret

    @property
    def routing_tags(self):
        """
        Routing routing_tags - notification destinations decision based on these routing_tags.

        @return:
        """
        return self._routing_tags

    @routing_tags.setter
    def routing_tags(self, value):
        """
        Route routing_tags setter.

        @param value:
        @return:
        """

        self._routing_tags = value

    @property
    def link_href(self):
        """
        If you want explicit link added to the notification, you use HREF
        to make it user-friendly.

        @return:
        """
        return self._link_href

    @link_href.setter
    def link_href(self, value):
        """
        Link href setter.

        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(value)
        self._link_href = value

    @property
    def link(self):
        """
        You can add a summarizing URL link to the notification.
        Each Notification channel implements handling of this data implicitly.

        @return:
        """

        return self._link

    @link.setter
    def link(self, value):
        """
        Link setter.

        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(value)
        self._link = value

    @property
    def header(self):
        """
        Header message of the notification. Summary.

        @return:
        """

        return self._header

    @header.setter
    def header(self, value):
        """
        Header setter.

        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(value)
        self._header = value

    @property
    def text(self):
        """
        Notification data you want the receiver to get.

        @return:
        """

        return self._text

    @text.setter
    def text(self, value):
        """
        Text setter.

        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(value)
        self._text = value

    @property
    def type(self):
        """
        Notification Type. Enum options are below.

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

        notification_types = [notification_type.value for notification_type in Notification.Types]
        if value.value not in notification_types:
            raise ValueError(f"Received {value} while expecting one of {notification_types}")
        self._type = value

    class Types(Enum):
        """
        Possible types of the Notification.

        """

        DEBUG = "DEBUG"
        INFO = "INFO"
        STABLE = "STABLE"
        WARNING = "WARNING"
        CRITICAL = "CRITICAL"
        PARTY = "PARTY"

import pdb
import json


class NotificationChannelBase:
    def __init__(self, configuration):
        self.configuration = configuration

    def get_message_routes(self, message):
        raise NotImplementedError("get_message_routes")

    def get_alert_routes(self,  alert):
        raise NotImplementedError("get_alert_routes")

    @property
    def system_alerts_routes(self):
        raise NotImplementedError("system_alerts_routes")

    class UnknownTag(ValueError):
        """
        Raise in case tag specified has no route.
        """


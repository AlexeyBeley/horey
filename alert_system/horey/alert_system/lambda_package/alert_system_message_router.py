import pdb
import json


class AlertSystemMessageRouter:
    def __init__(self, system_alerts_slack_channel=None):
        try:
            with open("slack_address_book.json") as file_handler:
                self.slack_mappings = json.load(file_handler)
                if self.slack_mappings.get("system_alerts") is None and system_alerts_slack_channel is not None:
                    self.slack_mappings["system_alerts"] = system_alerts_slack_channel
        except Exception:
            if system_alerts_slack_channel is not None:
                self.slack_mappings = {"system_alerts": system_alerts_slack_channel} if \
                    system_alerts_slack_channel is not None else None

    def get_slack_routes(self, message, alarm=None):
        if message is None:
            if alarm is not None:
                data = alarm.alert_system_data
            else:
                raise RuntimeError()
        else:
            data = message.data

        tags = data.get("tags")
        lst_ret = []
        for tag in tags:
            channel = self.slack_mappings.get(tag)
            if channel is None:
                raise self.UnknownTag(f"Can not find slack channel for tag {tag}")
            lst_ret.append(channel)
        return lst_ret

    @property
    def system_alerts_slack_channel(self):
        return self.slack_mappings.get("system_alerts") if self.slack_mappings is not None else None

    class UnknownTag(ValueError):
        """
        Raise in case tag specified has no route.
        """


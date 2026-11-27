"""
Sample value
"""


class ConfigValues:
    """
    Main class
    """
    def __init__(self):
        self.region = "us-west-2"
        self.src_email = "self@common.com"
        self.routing_tag_to_email_mapping = {"team_front": "team_front@common.com",
                                             "team_backend": "team_backend@common.com",
                                             }
        self.alert_system_monitoring_destination = "alive@common.com"


def main():
    """
    Standard

    :return:
    """
    return ConfigValues()

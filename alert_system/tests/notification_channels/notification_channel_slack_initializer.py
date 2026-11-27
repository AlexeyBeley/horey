"""
Notification Channel to send SES email.

"""
import os.path

from horey.alert_system.notification_channels.notification_channel_slack import NotificationChannelSlack

from horey.alert_system.notification_channels.notification_channel_slack import NotificationChannelSlackConfigurationPolicy
from horey.alert_system.lambda_package.notification import Notification


def main():
    """
    Entrypoint used by NotificationChannels Factory to generate notification channels.

    :return:
    """

    config = NotificationChannelSlackConfigurationPolicy()
    config.configuration_file_full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "ignore", "slack_api_configuration_values.py"))
    config.init_from_file()
    config.tag_to_channel_mapping = {Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG: "#test_bot"}

    return NotificationChannelSlack(config)

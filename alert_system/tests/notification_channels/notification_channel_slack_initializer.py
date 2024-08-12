"""
Notification Channel to send SES email.

"""
import os.path

from horey.alert_system.lambda_package.notification_channels.notification_channel_slack import NotificationChannelSlack

from horey.alert_system.lambda_package.notification_channels.notification_channel_slack import NotificationChannelSlackConfigurationPolicy


def main():
    config = NotificationChannelSlackConfigurationPolicy()
    config.configuration_file_full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "ignore", "slack_api_configuration_values.py"))
    config.init_from_file()
    config.tag_to_channel_mapping = {NotificationChannelSlackConfigurationPolicy.ALERT_SYSTEM_MONITORING_ROUTING_TAG: "#test_bot"}

    return NotificationChannelSlack(config)

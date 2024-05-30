"""
Notification Channel to send SES email.

"""

import os
from horey.alert_system.lambda_package.notification_channels.notification_channel_ses import NotificationChannelSES, NotificationChannelSESConfigurationPolicy


def main():
    config = NotificationChannelSESConfigurationPolicy()
    config.configuration_file_full_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                       "notification_channel_ses_config.json"))
    config.init_from_file()
    return NotificationChannelSES(config)

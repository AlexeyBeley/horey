"""
Notification Channel to send SES email.

"""

from horey.alert_system.lambda_package.notification_channels.notification_channel_echo import NotificationChannelEcho


def main():
    return NotificationChannelEcho()

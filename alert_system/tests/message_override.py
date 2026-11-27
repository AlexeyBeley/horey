"""
Sample overriding

"""

from horey.alert_system.lambda_package.message_cloudwatch_default import MessageCloudwatchDefault


class OverrideMessageCloudwatchDefault(MessageCloudwatchDefault):
    """
    Main class overriding cloudwatch default.

    """

    def generate_notification(self):
        """
        Generate notification.

        :return:
        """

        notification = super().generate_notification()
        notification.header = "override"
        return notification


def main():
    """
    Entrypoint to load class

    :return:
    """

    return OverrideMessageCloudwatchDefault

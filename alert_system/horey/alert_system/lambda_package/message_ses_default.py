"""
Message being received by the Alert System Lambda.

"""
import datetime

from horey.h_logger import get_logger
from horey.alert_system.lambda_package.message_base import MessageBase
from horey.alert_system.lambda_package.notification import Notification


logger = get_logger()


class MessageSESDefault(MessageBase):
    """
    Main class.

    """

    def __init__(self, dict_src, configuration):
        """
        Try to init from dict

        :param dict_src:
        :return:
        """

        super().__init__(dict_src, configuration)
        self.message_dict = MessageBase.extract_message_dict(dict_src)

        if self.message_dict.get("notificationType") == "AmazonSnsSubscriptionSucceeded":
            return

        if "mail" not in self.message_dict:
            raise MessageBase.NotAMatchError("Not a match")

    def generate_notification(self):
        """
        Generate notification from message.

        :return:
        """
        if self.message_dict.get("notificationType") == "AmazonSnsSubscriptionSucceeded":
            return self.generate_notification_amazon_sns_subscription_succeeded()
        notification = Notification()
        mail = self.message_dict.get("mail") or {}
        time_string = None

        end_time = None
        start_time = None
        try:
            time_string = f'Alarm time: {self._dict_src["Records"][0]["Sns"]["Timestamp"]}'
            end_time = datetime.datetime.strptime(
                self._dict_src["Records"][0]["Sns"]["Timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z"
            )
            start_time = end_time - datetime.timedelta(minutes=5)
            end_time += datetime.timedelta(minutes=1)
        except Exception as inst_error:
            logger.info(repr(inst_error))

        if not time_string:
            time_string = f'Email time: {mail.get("timestamp")}'

        try:
            region = mail.get("sourceArn").split(":")[3]
        except Exception as error_inst:
            region = repr(error_inst)
        try:
            message_id = mail.get("messageId")
        except Exception as error_inst:
            message_id = repr(error_inst)
        try:
            destination = mail.get("destination")
        except Exception as error_inst:
            destination = repr(error_inst)

        event_type = self.message_dict.get("notificationType") or self.message_dict.get("eventType")
        if not event_type:
            notification.type = Notification.Types.CRITICAL
            data = self._dict_src or self.message_dict
            notification.text = f"Was not able to find delivery type: {data}"
            email_status = "Missing both 'notificationType' and 'eventType'"
        elif event_type == "Delivery":
            notification.type = Notification.Types.DEBUG
            notification.text = f"Delivery. Region: {region}. {time_string}."
            email_status = "Delivery"
        elif event_type == "DeliveryDelay":
            notification.type = Notification.Types.WARNING
            info = self.message_dict.get("deliveryDelay") or destination
            notification.text = f"DeliveryDelay. Region: {region}. {time_string}. messageId: {message_id}. Info: {info}"
            email_status = "DeliveryDelay"
        elif event_type == "Bounce":
            notification.type = Notification.Types.WARNING
            notification.text = f"Region: {region}\n" \
                                f"{time_string}\n" \
                                f"MessageId: {message_id}\n" \
                                f"Destination {destination}"
            email_status = "Bounce"
        elif event_type == "Send":
            notification.type = Notification.Types.DEBUG
            notification.text = f"Send. Region: {region}. {time_string}. messageId: {message_id}. Destination: {destination}"
            email_status = "Send"
        else:
            notification.type = Notification.Types.CRITICAL
            notification.text = f"Event Type: {event_type}. Event: {self._dict_src}"
            email_status = "ALERT_SYSTEM_ERROR"
        notification.header = (
                notification.header or f"SES {email_status}"
        )

        notification.link = self.generate_cloudwatch_log_search_link(self.configuration.alert_system_lambda_log_group_name,
                                                                     message_id,
                                                                     start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                                                     end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                                                                     )
        notification.link_href = "View Cloudwatch Logs"
        return notification

    def generate_notification_amazon_sns_subscription_succeeded(self):
        """
        Unique message - subscription.

        :return:
        """

        notification = Notification()
        timestamp = self._dict_src["Records"][0]["Sns"]["Timestamp"]
        notification.text = f"Timestamp: {timestamp}. " + self.message_dict.get("message")
        notification.type = Notification.Types.PARTY
        notification.header = "Amazon Sns Subscription Succeeded to SES events"
        return notification

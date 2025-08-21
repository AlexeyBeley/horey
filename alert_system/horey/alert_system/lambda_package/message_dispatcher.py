"""
Module handling most of the basic message behavior.
Checks message type to invoke relevant handler.
Sends the notification to the channels.

"""
import datetime
import json
import traceback

from horey.alert_system.lambda_package.notification_channels.notification_channel_factory import \
    NotificationChannelFactory
from horey.alert_system.lambda_package.notification import Notification

from horey.h_logger import get_logger
from horey.aws_api.aws_clients.dynamodb_client import DynamoDBClient
from horey.aws_api.aws_services_entities.dynamodb_table import DynamoDBTable
from horey.aws_api.aws_clients.cloud_watch_client import CloudWatchClient
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm
from horey.aws_api.base_entities.region import Region

logger = get_logger()


class MessageDispatcher:
    """
    Main class.

    """

    def __init__(self, configuration):
        self.configuration = configuration
        self.notification_channels = []
        self.region = Region.get_region(self.configuration.region)
        if not self.init_notification_channels():
            raise RuntimeError("No notification channels configured")

    def init_notification_channels(self):
        """
        i
        :return:
        """
        if not self.configuration.notification_channels:
            raise ValueError(f"Notification channels not configured! {self.configuration.notification_channels=}")

        self.notification_channels = NotificationChannelFactory().load_notification_channels(self.configuration)

        return len(self.notification_channels) > 0 and \
            len(self.notification_channels) == len(self.configuration.notification_channels)

    def dispatch(self, message):
        """
        Route the message to relevant notification channels.§

        @param message:
        @return:
        """

        try:
            notification = message.generate_notification()
            for notification_channel in self.notification_channels:
                notification_channel.notify(notification)
        except Exception as error_inst:
            self.handle_exception(error_inst, message)
        return True

    def handle_exception(self, error_inst, data):
        """
        Generate and send error notification

        :param error_inst:
        :param data:
        :return:
        """

        notification = self.generate_alert_system_exception_notification(error_inst, data)
        if not notification.link_href or not notification.link:
            notification.link_href = "HAS2 lambda"
            notification.link = f"https://{self.configuration.region}.console.aws.amazon.com/lambda/home?region={self.configuration.region}#/functions/{self.configuration.lambda_name}?tab=monitoring"

        for notification_channel in self.notification_channels:
            notification_channel.notify_alert_system_error(notification)
        raise RuntimeError(f"Exception in Message Dispatcher: {repr(error_inst)}") from error_inst

    @staticmethod
    def generate_alert_system_exception_notification(error_inst, data):
        """
        Generate notification about alert system exception
        :return:
        """
        if not isinstance(data, dict):
            try:
                data = data.convert_to_dict()
            except Exception as internal_inst_error:
                data = {"error": f"{repr(internal_inst_error)=}, {data=}"}
        traceback_str = "".join(traceback.format_tb(error_inst.__traceback__))
        logger.exception(f"Unhandled message:\n{traceback_str}\n{repr(error_inst)}")

        text = json.dumps(data, indent=4)

        notification = Notification()
        notification.type = Notification.Types.CRITICAL
        notification.header = "Unhandled message in alert_system"
        notification.text = text
        return notification

    def yield_dynamodb_items(self):
        """
        Fetch alert data from dynamo

        :return:
        """

        dynamodb_client = DynamoDBClient()
        table = DynamoDBTable({})
        table.name = self.configuration.dynamodb_table_name
        table.region = Region.get_region(self.configuration.region)
        dynamodb_client.update_table_information(table, raise_if_not_found=True)
        for item in dynamodb_client.scan(table):
            item["alarm_state"]["epoch_triggered"] = float(item["alarm_state"]["epoch_triggered"])
            yield item

    def update_dynamodb_alarm(self, alarm_name: str, alarm_epoch_utc: float):
        """
        Put alarm time in db.

        :param alarm_name:
        :param alarm_epoch_utc: float epoch
        :return:
        """

        dynamodb_client = DynamoDBClient()
        table = DynamoDBTable({})
        table.name = self.configuration.dynamodb_table_name
        table.region = self.region
        dynamodb_client.update_table_information(table, raise_if_not_found=True)
        dict_key = {"alarm_name": alarm_name,
                    "alarm_state":
                        {"cooldown_time": 300,
                         "epoch_triggered": str(alarm_epoch_utc)}}

        logger.info(f"Updating time triggered time: {alarm_name=} {alarm_epoch_utc=}")
        return dynamodb_client.put_item(table, dict_key)

    def delete_dynamodb_alarm(self, alarm_name: str):
        """
        Delete alarm from db

        :param alarm_name:
        :return:
        """

        dynamodb_client = DynamoDBClient()
        table = DynamoDBTable({})
        table.name = self.configuration.dynamodb_table_name
        table.region = self.region
        dynamodb_client.update_table_information(table, raise_if_not_found=True)
        dict_key = {"alarm_name": alarm_name}
        return dynamodb_client.delete_item(table, dict_key)

    def run_dynamodb_update_routine(self):
        """

        :return:
        """
        client = CloudWatchClient()
        time_now = datetime.datetime.now(datetime.timezone.utc)
        timestamp_now = time_now.timestamp()
        for item in self.yield_dynamodb_items():

            alarm = CloudWatchAlarm({"AlarmName": item["alarm_name"]})
            alarm.region = self.region

            if not client.update_alarm_information(alarm):
                self.delete_dynamodb_alarm(item["alarm_name"])
                continue
            if alarm.state_value != "ALARM":
                continue
            # todo: check if too old: cleanup report
            # todo: cleanup report check alarm state never changed, check if alarm needed/tested
            # if alarm.state_updated_timestamp < time_now - 300:
            #    logger.warning(f"Unhandled state for alarm {alarm.name}: {alarm.state_updated_timestamp=} {alarm.state_transitioned_timestamp=}")
            if timestamp_now - alarm.state_transitioned_timestamp.timestamp() < item["alarm_state"]["cooldown_time"]:
                continue

            try:
                client.set_alarm_ok(alarm)
            except Exception as inst_error:
                if "ResourceNotFound" not in repr(inst_error):
                    raise
                self.delete_dynamodb_alarm(item["alarm_name"])
                continue

            self.update_dynamodb_alarm(item["alarm_name"], alarm.state_transitioned_timestamp.timestamp())
        return True

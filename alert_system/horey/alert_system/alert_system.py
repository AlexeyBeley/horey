"""
AlertSystem deployment and testing module.
It is responsible to Manage all parts of the system:
SNS, Cloudwatch Log Filter, Cloudwatch Alarms and AlertSystemLambda.

"""
import copy
import datetime
import json
import os
import shutil
import uuid

# pylint: disable=no-name-in-module
from horey.h_logger import get_logger
from horey.common_utils.common_utils import CommonUtils
from horey.serverless.packer.packer import Packer
from horey.aws_api.aws_services_entities.aws_lambda import AWSLambda
from horey.aws_api.base_entities.region import Region
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_services_entities.iam_role import IamRole
from horey.aws_api.aws_services_entities.sns_subscription import SNSSubscription
from horey.aws_api.aws_services_entities.sns_topic import SNSTopic
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm
from horey.aws_api.aws_services_entities.cloud_watch_log_group_metric_filter import (
    CloudWatchLogGroupMetricFilter,
)
from horey.aws_api.aws_services_entities.cloud_watch_log_group import CloudWatchLogGroup
from horey.alert_system.lambda_package.message import Message
from horey.alert_system.lambda_package.notification_channel_base import (
    NotificationChannelBase,
)
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy


logger = get_logger()


class AlertSystem:
    """
    Alert system management class.

    """

    def __init__(self, configuration: AlertSystemConfigurationPolicy, aws_api=None):
        self.configuration = configuration
        self.packer = Packer()
        self.aws_api = aws_api or AWSAPI()
        self.region = Region.get_region(self.configuration.region)
        self.tags = None

    def provision(self, tags, lambda_files):
        """
        Full provision of the AlertSystem receiving side components.
        i.e. parts that receive the Alarms and sends the notifications to the User Facing Channels.

        The opposite part of the system - Alarm sending part is implemented separately since it's part of
        the monitored services CI/CD.

        There are provision_cloudwatch_alarm and provision_cloudwatch_logs_alarm to help automate the
        sending side as well.

        @param tags: [{"Key": "string", "Value": "string"}]
        @param lambda_files: Files needed by AlertSystemLambda - new dispatcher or SlackAPI configuration.
        @return:
        """

        self.tags = copy.deepcopy(tags)
        self.provision_sns_topic()
        self.provision_lambda(lambda_files)
        self.provision_sns_subscription()

        self.provision_log_group()

        self.provision_self_monitoring()

        self.test_self_monitoring()

    def provision_log_group(self):
        """
        Provision log group- on a fresh provisioning self monitoring will have no log group to monitor.
        Until first lambda invocation.

        @param tags:
        @return:
        """

        log_group = CloudWatchLogGroup({})
        log_group.region = self.region
        log_group.name = self.configuration.alert_system_lambda_log_group_name
        log_group.tags = {tag["Key"]: tag["Value"] for tag in self.tags}
        log_group.tags["name"] = log_group.name
        self.aws_api.provision_cloudwatch_log_group(log_group)

    def provision_lambda(self, files):
        """
        Provision alert system receiving side lambda.

        @param files:
        @return:
        """

        self.create_lambda_package(files)
        return self.deploy_lambda()

    def provision_self_monitoring(self):
        """
        Provision self monitoring different parts.

        @return:
        """

        self.provision_self_monitoring_log_error_alarm()
        self.provision_self_monitoring_log_timeout_alarm()
        self.provision_self_monitoring_errors_metric_alarm()
        self.provision_self_monitoring_duration_alarm()

    def test_self_monitoring(self):
        """
        Run all self monitoring testing functions.

        :return:
        """

        self.trigger_self_monitoring_log_error_alarm()
        self.trigger_self_monitoring_log_timeout_alarm()
        self.trigger_self_monitoring_errors_metric_alarm()
        self.trigger_self_monitoring_duration_alarm()

    def provision_self_monitoring_log_error_alarm(self):
        """
        Find [ERROR] log messages in self log.

        @return:
        """

        filter_text = '"[ERROR]"'
        metric_name_raw = f"{self.configuration.lambda_name}-log-error"
        message_data = {"tags": ["alert_system_monitoring"]}
        self.provision_cloudwatch_logs_alarm(
            self.configuration.alert_system_lambda_log_group_name, filter_text, metric_name_raw, message_data
        )

    def provision_self_monitoring_log_timeout_alarm(self):
        """
        Find lambda timeout messages in self log.

        @return:
        """

        filter_text = "Task timed out after"
        message_data = {"tags": ["alert_system_monitoring"]}
        self.provision_cloudwatch_logs_alarm(
            self.configuration.alert_system_lambda_log_group_name, filter_text, self.configuration.self_monitoring_log_timeout_metric_name_raw, message_data
        )

    def provision_self_monitoring_duration_alarm(self):
        """
        Check self metric for running to long.

        @return:
        """

        message = Message()
        message.uuid = str(uuid.uuid4())
        message.type = "cloudwatch_metric_lambda_duration"
        message.data = {"tags": ["alert_system_monitoring"]}

        alarm = CloudWatchAlarm({})
        alarm.name = f"{self.configuration.lambda_name}-metric-duration"
        alarm.actions_enabled = True
        alarm.alarm_description = json.dumps(message.convert_to_dict())
        alarm.insufficient_data_actions = []
        alarm.metric_name = "Duration"
        alarm.namespace = "AWS/Lambda"
        alarm.statistic = "Average"
        alarm.dimensions = [
            {"Name": "FunctionName", "Value": self.configuration.lambda_name}
        ]
        alarm.period = 300
        alarm.evaluation_periods = 1
        alarm.datapoints_to_alarm = 1
        alarm.threshold = self.configuration.lambda_timeout * 0.6 * 1000
        alarm.comparison_operator = "GreaterThanThreshold"
        alarm.treat_missing_data = "notBreaching"
        self.provision_cloudwatch_alarm(alarm)

    def provision_self_monitoring_errors_metric_alarm(self):
        """
        Provision cloudwatch metric Lambda errors.
        Lambda service metric shows the count of failed Lambda executions.

        @return:
        """

        message = Message()
        message.uuid = str(uuid.uuid4())
        message.type = "cloudwatch_logs_metric_sns_alarm"
        message.data = {"tags": ["alert_system_monitoring"]}

        alarm = CloudWatchAlarm({})
        alarm.name = f"{self.configuration.lambda_name}-metric-errors"
        alarm.actions_enabled = True
        alarm.alarm_description = json.dumps(message.convert_to_dict())
        alarm.insufficient_data_actions = []
        alarm.metric_name = "Errors"
        alarm.namespace = "AWS/Lambda"
        alarm.statistic = "Average"
        alarm.dimensions = [
            {"Name": "FunctionName", "Value": self.configuration.lambda_name}
        ]
        alarm.period = 300
        alarm.evaluation_periods = 1
        alarm.datapoints_to_alarm = 1
        alarm.threshold = 1.0
        alarm.comparison_operator = "GreaterThanThreshold"
        alarm.treat_missing_data = "notBreaching"
        self.provision_cloudwatch_alarm(alarm)

    def create_lambda_package(self, files):
        """
        Create the zip package to be deployed.
        NotificationChannelSlackConfigurationPolicy.CONFIGURATION_FILE_NAME can be one of the files

        :return:
        """
        self.packer.create_venv(self.configuration.deployment_venv_path)
        current_dir = os.getcwd()
        os.chdir(self.configuration.deployment_directory_path)
        self.packer.install_horey_requirements(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "lambda_package",
                "requirements.txt",
            ),
            self.configuration.deployment_venv_path,
            self.configuration.horey_repo_path,
        )

        self.packer.zip_venv_site_packages(
            self.configuration.lambda_zip_file_name,
            self.configuration.deployment_venv_path
        )

        external_files = [os.path.basename(file_path) for file_path in files]
        lambda_package_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "lambda_package"
        )
        lambda_package_files = [
            os.path.join(lambda_package_dir, file_name)
            for file_name in os.listdir(lambda_package_dir)
            if file_name not in external_files
        ]
        files_paths = lambda_package_files + files
        self.packer.add_files_to_zip(
            self.configuration.lambda_zip_file_name, files_paths
        )

        self.validate_lambda_package()
        logger.info(f"Created lambda package: {self.configuration.deployment_directory_path}/{self.configuration.lambda_zip_file_name}")

        os.chdir(current_dir)

    def validate_lambda_package(self):
        """
        Unzip in a temporary dir and init the base dispatcher class.

        @return:
        """

        validation_dir_name = os.path.splitext(self.configuration.lambda_zip_file_name)[
            0
        ]
        try:
            os.makedirs(validation_dir_name)
        except FileExistsError:
            shutil.rmtree(validation_dir_name)
            os.makedirs(validation_dir_name)

        tmp_zip_path = os.path.join(
            validation_dir_name, self.configuration.lambda_zip_file_name
        )
        shutil.copyfile(self.configuration.lambda_zip_file_name, tmp_zip_path)
        self.packer.extract(tmp_zip_path, validation_dir_name)

        os.environ[
            NotificationChannelBase.NOTIFICATION_CHANNELS_ENVIRONMENT_VARIABLE
        ] = self.configuration.notification_channel_file_names
        current_dir = os.getcwd()
        os.chdir(validation_dir_name)

        message_dispatcher = CommonUtils.load_object_from_module(
            "message_dispatcher_base.py", "MessageDispatcherBase"
        )
        if self.configuration.active_deployment_validation:
            message_dispatcher.dispatch(None)
        os.chdir(current_dir)

    def provision_lambda_role(self):
        """
        Provision the alert_system receiving Lambda role.

        @return:
        """

        iam_role = IamRole({})
        iam_role.description = "alert_system lambda role"
        iam_role.name = self.configuration.lambda_role_name
        iam_role.path = self.configuration.lambda_role_path
        iam_role.max_session_duration = 12 * 60 * 60
        iam_role.assume_role_policy_document = """{
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Principal": {
                "Service": "lambda.amazonaws.com"
              },
              "Action": "sts:AssumeRole"
            }
          ]
        }"""
        iam_role.managed_policies_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
        tags = copy.deepcopy(self.tags)
        tags.append({"Key": "name", "Value": iam_role.name})
        iam_role.tags = tags
        self.aws_api.provision_iam_role(iam_role)
        return iam_role

    def deploy_lambda(self):
        """
        Deploy the lambda object into AWS service.

        @return:
        """

        topic = SNSTopic({})
        topic.name = self.configuration.sns_topic_name
        topic.region = self.region
        if not self.aws_api.sns_client.update_topic_information(topic, full_information=False):
            raise RuntimeError("Could not update topic information")

        role = self.provision_lambda_role()

        aws_lambda = AWSLambda({})
        aws_lambda.region = self.region
        aws_lambda.name = self.configuration.lambda_name
        aws_lambda.handler = "lambda_handler.lambda_handler"
        aws_lambda.runtime = "python3.9"
        aws_lambda.role = role.arn
        aws_lambda.timeout = self.configuration.lambda_timeout
        aws_lambda.memory_size = 512

        aws_lambda.tags = {"Name": aws_lambda.name}
        aws_lambda.policy = {
            "Version": "2012-10-17",
            "Id": "default",
            "Statement": [
                {
                    "Sid": f"trigger_from_topic_{topic.name}",
                    "Effect": "Allow",
                    "Principal": {"Service": "sns.amazonaws.com"},
                    "Action": "lambda:InvokeFunction",
                    "Resource": None,
                    "Condition": {"ArnLike": {"AWS:SourceArn": topic.arn}},
                }
            ],
        }

        aws_lambda.environment = {
            "Variables": {
                NotificationChannelBase.NOTIFICATION_CHANNELS_ENVIRONMENT_VARIABLE: self.configuration.notification_channel_file_names,
                "DISABLE": "false",
            }
        }

        with open(
            os.path.join(
                self.configuration.deployment_directory_path,
                self.configuration.lambda_zip_file_name,
            ),
            "rb",
        ) as myzip:
            aws_lambda.code = {"ZipFile": myzip.read()}
        self.aws_api.provision_aws_lambda(aws_lambda, update_code=True)
        return aws_lambda

    def provision_sns_topic(self):
        """
        Provision the SNS topic receiving alert_system messages.

        @return:
        """
        topic = SNSTopic({})
        topic.region = self.region
        topic.name = self.configuration.sns_topic_name
        topic.attributes = {"DisplayName": topic.name}
        topic.tags =copy.deepcopy(self.tags)
        topic.tags.append({"Key": "Name", "Value": topic.name})

        self.aws_api.provision_sns_topic(topic)

    def provision_sns_subscription(self):
        """
        Subscribe the receiving lambda to the SNS topic.

        @return:
        """

        topic = SNSTopic({})
        topic.name = self.configuration.sns_topic_name
        topic.region = self.region
        if not self.aws_api.sns_client.update_topic_information(topic, full_information=False):
            raise RuntimeError("Could not update topic information")

        aws_lambda = AWSLambda({})
        aws_lambda.name = self.configuration.lambda_name
        aws_lambda.region = self.region

        if not self.aws_api.lambda_client.update_lambda_information(
            aws_lambda, full_information=False
        ):
            raise RuntimeError("Could not update aws_lambda information")

        subscription = SNSSubscription({})
        subscription.region = self.region
        subscription.name = self.configuration.subscription_name
        subscription.protocol = "lambda"
        subscription.topic_arn = topic.arn
        subscription.endpoint = aws_lambda.arn
        self.aws_api.provision_sns_subscription(subscription)

    def provision_cloudwatch_alarm(self, alarm):
        """
        Provision cloudwatch alarm - add self topic to it.

        @param alarm:
        @return:
        """

        topic = SNSTopic({})
        topic.name = self.configuration.sns_topic_name
        topic.region = self.region
        if not self.aws_api.sns_client.update_topic_information(topic, full_information=False):
            raise RuntimeError("Could not update topic information")

        alarm.region = self.region
        alarm.ok_actions = [topic.arn]
        alarm.alarm_actions = [topic.arn]
        self.aws_api.cloud_watch_client.set_cloudwatch_alarm(alarm)

    def provision_cloudwatch_logs_alarm(
        self, log_group_name, filter_text, metric_name_raw, message_data
    ):
        """
        Provision Cloud watch logs based alarm.

        @param message_data: dict
        @param filter_text:
        @param log_group_name:
        @param metric_name_raw:
        @return:
        """
        if not isinstance(message_data["tags"], list):
            raise ValueError(
                f"Routing tags must be a list, received: '{message_data['tags']}'"
            )
        if len(message_data["tags"]) == 0:
            raise ValueError(f"No routing tags: received: '{message_data['tags']}'")

        message_data["log_group_name"] = log_group_name
        message_data["log_group_filter_pattern"] = filter_text
        metric_name = f"metric-{metric_name_raw}"

        metric_filter = CloudWatchLogGroupMetricFilter({})
        metric_filter.log_group_name = log_group_name
        metric_filter.name = f"metric-filter-{log_group_name}-{metric_name_raw}"
        metric_filter.filter_pattern = filter_text
        metric_filter.metric_transformations = [
            {
                "metricName": metric_name,
                "metricNamespace": log_group_name,
                "metricValue": "1",
            }
        ]
        metric_filter.region = self.region
        self.aws_api.cloud_watch_logs_client.provision_metric_filter(metric_filter)

        message = Message()
        message.type = "cloudwatch_logs_metric_sns_alarm"
        message.data = message_data
        message.generate_uuid()

        alarm = CloudWatchAlarm({})
        alarm.region = self.region
        alarm.name = f"alarm-{log_group_name}-{metric_name_raw}"
        alarm.actions_enabled = True
        alarm.alarm_description = json.dumps(message.convert_to_dict())
        alarm.metric_name = metric_name
        alarm.namespace = log_group_name
        alarm.statistic = "Sum"
        alarm.period = 300
        alarm.evaluation_periods = 1
        alarm.datapoints_to_alarm = 1
        alarm.threshold = 0.0
        alarm.comparison_operator = "GreaterThanThreshold"
        alarm.treat_missing_data = "notBreaching"
        self.provision_cloudwatch_alarm(alarm)

    def provision_cloudwatch_sqs_visible_alarm(
        self, sqs_queue_name, threshold, message_data
    ):
        """
        Number of SQS visible messages.

        @param sqs_queue_name:
        @param threshold:
        @param message_data:
        @return:
        """

        message = Message()
        message.type = "cloudwatch_sqs_visible_alarm"
        message.generate_uuid()
        message.data = message_data
        message.data["queue_name"] = sqs_queue_name

        alarm = CloudWatchAlarm({})
        alarm.region = self.region
        alarm.name = (
            f"alert_system_alarm-{sqs_queue_name}-ApproximateNumberOfMessagesVisible"
        )
        alarm.actions_enabled = True
        alarm.alarm_description = json.dumps(message.convert_to_dict())
        alarm.insufficient_data_actions = []
        alarm.metric_name = "ApproximateNumberOfMessagesVisible"
        alarm.namespace = "AWS/SQS"
        alarm.statistic = "Average"
        alarm.dimensions = [{"Name": "QueueName", "Value": sqs_queue_name}]
        alarm.period = 300
        alarm.evaluation_periods = 1
        alarm.datapoints_to_alarm = 1
        alarm.threshold = threshold
        alarm.comparison_operator = "GreaterThanThreshold"
        alarm.treat_missing_data = "notBreaching"

        self.provision_cloudwatch_alarm(alarm)

    def provision_and_trigger_locally_lambda_handler(self, lambda_files, event_json_file_path):
        """
        Locally test event in the being provisioned infra.

        :param lambda_files:
        :param event_json_file_path:
        :return:
        """

        self.create_lambda_package(lambda_files)

        validation_dir_name = os.path.splitext(self.configuration.lambda_zip_file_name)[0]
        validation_dir_path = os.path.join(self.configuration.deployment_directory_path, validation_dir_name)
        current_dir = os.getcwd()
        os.chdir(validation_dir_path)

        event_handler = CommonUtils.load_object_from_module("lambda_handler.py", "EventHandler")
        with open(event_json_file_path, encoding="utf-8") as file_handler:
            event = json.load(file_handler)

        ret = event_handler.handle_event(event)

        os.chdir(current_dir)
        return ret

    def send_message_to_sns(self, message, topic_arn=None):
        """
        Send message to self sns_topic.

        :param topic_arn:
        :param message:
        :return:
        """

        if topic_arn is None:
            topic = SNSTopic({})
            topic.name = self.configuration.sns_topic_name
            topic.region = self.region
            self.aws_api.sns_client.update_topic_information(topic, full_information=False)
            topic_arn = topic.arn
        self.aws_api.sns_client.raw_publish(topic_arn, message.type, json.dumps(message.convert_to_dict()))

    def trigger_self_monitoring_log_error_alarm(self):
        """
        Trigger the alarm using cloudwatch log stream filter metric.

        :return:
        """

        log_group = CloudWatchLogGroup({})
        log_group.region = self.region
        log_group.name = self.configuration.alert_system_lambda_log_group_name

        self.aws_api.cloud_watch_logs_client.put_log_lines(log_group, ["[ERROR]: Neo, the Horey has you!"])

    def trigger_self_monitoring_log_timeout_alarm(self):
        """
        Test
        # todo: datetime.datetime.now(datetime.UTC)

        :return:
        """
        dict_request = {"Namespace": self.configuration.alert_system_lambda_log_group_name,
                        "MetricData": [{"MetricName": f"metric-{self.configuration.self_monitoring_log_timeout_metric_name_raw}",
                                        "Timestamp": datetime.datetime.utcnow(),
                                        "Value": 1
                                        }]}
        self.aws_api.cloud_watch_client.put_metric_data_raw(self.region, dict_request)

    def trigger_self_monitoring_errors_metric_alarm(self):
        """
        These are built in metrics. So we can not change the metric itself and must move
        one step further - set alarm state manually.

        :return:
        """

        dict_request = {"AlarmName": f"{self.configuration.lambda_name}-metric-errors",
                        "StateValue": "ALARM",
                        "StateReason":"Test"}
        self.aws_api.cloud_watch_client.set_alarm_state_raw(self.region, dict_request)

    def trigger_self_monitoring_duration_alarm(self):
        """
        These are built in metrics. So we can not change the metric itself and must move
        one step further - set alarm state manually.

        :return:
        """

        dict_request = {"AlarmName": f"{self.configuration.lambda_name}-metric-duration",
                        "StateValue": "ALARM",
                        "StateReason": "Test"}
        self.aws_api.cloud_watch_client.set_alarm_state_raw(self.region, dict_request)

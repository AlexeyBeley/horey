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
from time import perf_counter
import email.utils

# pylint: disable=no-name-in-module
from horey.h_logger import get_logger
from horey.common_utils.bash_executor import BashExecutor
from horey.common_utils.common_utils import CommonUtils
from horey.serverless.packer.packer import Packer
from horey.aws_api.aws_services_entities.aws_lambda import AWSLambda
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_services_entities.iam_role import IamRole
from horey.aws_api.aws_services_entities.sns_subscription import SNSSubscription
from horey.aws_api.aws_services_entities.sns_topic import SNSTopic
from horey.aws_api.aws_services_entities.sesv2_configuration_set import SESV2ConfigurationSet
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm
from horey.aws_api.aws_services_entities.cloud_watch_log_group_metric_filter import (
    CloudWatchLogGroupMetricFilter,
)
from horey.aws_api.aws_services_entities.cloud_watch_log_group import CloudWatchLogGroup
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy
from horey.pip_api.pip_api import PipAPI
from horey.pip_api.pip_api_configuration_policy import PipAPIConfigurationPolicy

from horey.alert_system.lambda_package.message_cloudwatch_default import MessageCloudwatchDefault
from horey.alert_system.lambda_package.notification import Notification


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
        self.tags = configuration.tags
        pip_api_configuration = PipAPIConfigurationPolicy()
        pip_api_configuration.multi_package_repositories = {"horey.": configuration.horey_repo_path}
        pip_api_configuration.horey_parent_dir_path = os.path.dirname(configuration.horey_repo_path)
        pip_api_configuration.venv_dir_path = configuration.deployment_venv_path
        self.pip_api = PipAPI(configuration=pip_api_configuration)
        AWSAccount.set_aws_default_region(self.region)

    def provision(self, lambda_files):
        """
        Full provision of the AlertSystem receiving side components.
        i.e. parts that receive the Alarms and sends the notifications to the User Facing Channels.

        The opposite part of the system - Alarm sending part is implemented separately since it's part of
        the monitored services CI/CD.

        There are provision_ cloudwatch_alarm and provision_cloudwatch _logs_alarm to help automate the
        sending side as well.

        @param lambda_files: Files needed by AlertSystemLambda - new dispatcher or SlackAPI configuration.
        @return:
        """
        self.validate_input(lambda_files)
        self.provision_sns_topic()
        self.provision_lambda(lambda_files)
        self.provision_sns_subscription()

        self.provision_log_group()

        self.provision_self_monitoring()

    def validate_input(self, lambda_files):
        """
        Validate the configuration.

        :return:
        """

        for file_path in lambda_files:
            if not os.path.exists(file_path):
                raise ValueError(f"File does not exist: {file_path}")

        return True

    def provision_log_group(self):
        """
        Provision log group - on a fresh provisioning self monitoring will have no log group to monitor.
        Until first lambda invocation.

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

        self.build_and_validate(files)

        return self.deploy_lambda()

    def build_and_validate(self, files, event=None):
        """
        Build the package locally and validate it

        :param event:
        :param files:
        :return:
        """

        zip_file_path = self.create_lambda_package(files)
        return self.validate_lambda_package(zip_file_path, event=event)

    def provision_self_monitoring(self):
        """
        Provision self monitoring different parts.

        @return:
        """

        self.provision_self_monitoring_log_error_alarm()
        self.trigger_self_monitoring_log_error_alarm()

        self.provision_self_monitoring_log_timeout_alarm()
        self.trigger_self_monitoring_log_timeout_alarm()

        self.provision_self_monitoring_errors_metric_alarm()
        self.trigger_self_monitoring_errors_metric_alarm()

        self.provision_self_monitoring_duration_alarm()
        self.trigger_self_monitoring_duration_alarm()

    def provision_self_monitoring_log_error_alarm(self):
        """
        Find [ERROR] log messages in self log.

        @return:
        """

        filter_text = f'"{AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_LOG_ERROR_FILTER_PATTERN}"'
        alarm_description = {
                        "lambda_name": self.configuration.lambda_name,
                        MessageCloudwatchDefault.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY: MessageCloudwatchDefault.ALERT_SYSTEM_SELF_MONITORING_TYPE_VALUE}
        return self.provision_cloudwatch_logs_alarm(self.configuration.alert_system_lambda_log_group_name,
                                                    filter_text,
                                                    "error",
                                                    [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG],
                                                    alarm_description=alarm_description,
        )

    def provision_self_monitoring_log_timeout_alarm(self):
        """
        Find lambda timeout messages in self log.

        @return:
        """

        filter_text = AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_LOG_TIMEOUT_FILTER_PATTERN
        alarm_description = {"lambda_name": self.configuration.lambda_name,
                        MessageCloudwatchDefault.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY: MessageCloudwatchDefault.ALERT_SYSTEM_SELF_MONITORING_TYPE_VALUE}
        return self.provision_cloudwatch_logs_alarm(self.configuration.alert_system_lambda_log_group_name,
                                                    filter_text,
                                                    "timeout",
                                                    [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG],
                                                    alarm_description=alarm_description
        )

    def provision_self_monitoring_errors_metric_alarm(self):
        """
        Provision cloudwatch metric Lambda errors.
        Lambda service metric shows the count of failed Lambda executions.

        @return:
        """

        alarm = CloudWatchAlarm({})
        alarm.name = f"{self.configuration.lambda_name}-metric-errors"
        alarm.actions_enabled = True
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

        alarm_description = {"routing_tags": [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG],
                        "lambda_name": self.configuration.lambda_name,
                        MessageCloudwatchDefault.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY: MessageCloudwatchDefault.ALERT_SYSTEM_SELF_MONITORING_TYPE_VALUE}
        alarm.alarm_description = json.dumps(alarm_description)

        self.provision_cloudwatch_alarm(alarm)
        return alarm

    def provision_self_monitoring_duration_alarm(self):
        """
        Check self metric for running to long.

        @return:
        """

        alarm = CloudWatchAlarm({})
        alarm.name = f"{self.configuration.lambda_name}-metric-duration"
        alarm.actions_enabled = True
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
        alarm_description = {"routing_tags": [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG],
                        "lambda_name": self.configuration.lambda_name,
                        MessageCloudwatchDefault.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY: MessageCloudwatchDefault.ALERT_SYSTEM_SELF_MONITORING_TYPE_VALUE}
        alarm.alarm_description = json.dumps(alarm_description)

        self.provision_cloudwatch_alarm(alarm)
        return alarm

    def create_lambda_package(self, files):
        """
        Create the zip package to be deployed.
        NotificationChannelSlackConfigurationPolicy.CONFIGURATION_FILE_NAME can be one of the files

        :return:
        """

        for file in files:
            if "requirements.txt" in file:
                raise NotImplementedError("Need to implement requirements overwrite in venv using serverless")

        current_dir = os.getcwd()
        os.chdir(self.configuration.deployment_directory_path)
        self.pip_api.install_requirements_from_file(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "lambda_package",
                "requirements.txt",
            )
        )

        self.packer.zip_venv_site_packages(
            self.configuration.lambda_zip_file_name,
            self.configuration.deployment_venv_path
        )

        # old: lambda_handler_file_path = sys.modules["horey.alert_system.lambda_package.lambda_handler"].__file__
        lambda_handler_file_path = os.path.join(os.path.dirname(__file__), "lambda_package", "lambda_handler.py")

        notification_channels_and_message_classes_file_paths = self.configuration.notification_channels[:]
        alert_system_config_file_path = os.path.join(self.configuration.deployment_directory_path,
                                                      AlertSystemConfigurationPolicy.ALERT_SYSTEM_CONFIGURATION_FILE_PATH)

        lambda_package_configuration = AlertSystemConfigurationPolicy()
        lambda_package_configuration.init_from_policy(self.configuration)
        # todo: cd to parent(alert_system_config_file_path) and add os.file.exists in alert system configuration policy on notification channels
        lambda_package_configuration.notification_channels = [os.path.basename(notification_channel_file_path) for notification_channel_file_path in
                                                              lambda_package_configuration.notification_channels]
        if self.configuration.message_classes:
            notification_channels_and_message_classes_file_paths += self.configuration.message_classes[:]
            lambda_package_configuration.message_classes = [os.path.basename(message_class_file_path) for
                                                              message_class_file_path in
                                                              lambda_package_configuration.message_classes]

        lambda_package_configuration.generate_configuration_file(alert_system_config_file_path)

        self.packer.add_files_to_zip(
            self.configuration.lambda_zip_file_name, files + [lambda_handler_file_path, alert_system_config_file_path] + notification_channels_and_message_classes_file_paths
        )
        logger.info(
            f"Created lambda package: {self.configuration.deployment_directory_path}/{self.configuration.lambda_zip_file_name}")

        os.chdir(current_dir)
        return os.path.join(
            self.configuration.deployment_directory_path,
            self.configuration.lambda_zip_file_name,
        )

    def validate_lambda_package(self, zip_file_path, event=None):
        """
        Unzip in a temporary dir and init the base dispatcher class.

        @return:
        """

        extraction_dir = self.extract_lambda_package_for_validation(zip_file_path)
        return self.trigger_lambda_handler_locally(extraction_dir, event)

    @staticmethod
    def trigger_lambda_handler_locally(extraction_dir, event):
        """
        Run the lambda handler locally

        :param extraction_dir:
        :param event:
        :return:
        """
        result_file_path = os.path.join(extraction_dir, "result.json")
        if os.path.exists(result_file_path):
            os.remove(result_file_path)
        shutil.copy2(os.path.join(os.path.dirname(__file__), "tests", "trigger_local.py"),
                     extraction_dir)
        with open(os.path.join(extraction_dir, "event.json"), "w", encoding="utf-8") as file_handler:
            json.dump(event, file_handler)
        ret = BashExecutor.run_bash(f"python {extraction_dir}/trigger_local.py")
        if not os.path.exists(result_file_path):
            return ret
        with open(result_file_path, encoding="utf-8") as file_handler:
            exec_ret = json.load(file_handler)
        return exec_ret

    def extract_lambda_package_for_validation(self, zip_file_path):
        """
        Extract the zip to local tmp dir.

        :return:
        """
        validation_dir_name = os.path.splitext(zip_file_path)[
                                  0
                              ] + "_validation"
        try:
            os.makedirs(validation_dir_name)
        except FileExistsError:
            shutil.rmtree(validation_dir_name)
            os.makedirs(validation_dir_name)

        tmp_zip_path = os.path.join(
            validation_dir_name, self.configuration.lambda_zip_file_name
        )
        shutil.copyfile(zip_file_path, tmp_zip_path)
        self.packer.extract(tmp_zip_path, validation_dir_name)
        return validation_dir_name

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
        aws_lambda.runtime = "python3.12"
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
        topic.tags = copy.deepcopy(self.tags)
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

    def provision_ses_configuration_set(self, configuration_set=None, declerative=True):
        """
        Provision alert_system ses configuration set.

        @return:
        """

        topic = SNSTopic({})
        topic.name = self.configuration.sns_topic_name
        topic.region = self.region
        if not self.aws_api.sns_client.update_topic_information(topic, full_information=False):
            raise RuntimeError("Could not update topic information")

        if configuration_set is None:
            if not declerative:
                raise ValueError("Can not create new configuration set in Declarative mode")
            configuration_set = SESV2ConfigurationSet({})
            configuration_set.name = self.configuration.ses_configuration_set_name
            configuration_set.region = self.region
            configuration_set.reputation_options = {"ReputationMetricsEnabled": True}
            configuration_set.sending_options = {"SendingEnabled": True}
            configuration_set.tags = copy.deepcopy(self.tags)
            configuration_set.tags.append({"Key": "name", "Value": configuration_set.name})
            configuration_set.event_destinations = []

        for event_destination in configuration_set.event_destinations:
            if event_destination.get("Name") == "alert_system_default_dst":
                break
        else:
            configuration_set.event_destinations.append({"Name": "alert_system_default_dst",
                                                         "Enabled": True,
                                                         "MatchingEventTypes": ["BOUNCE", "CLICK", "COMPLAINT",
                                                                                "DELIVERY",
                                                                                "OPEN", "REJECT", "RENDERING_FAILURE",
                                                                                "SEND"],
                                                         "SnsDestination": {
                                                             "TopicArn": topic.arn}})

        self.aws_api.sesv2_client.provision_configuration_set(configuration_set, declerative=declerative)
        return configuration_set

    def provision_cloudwatch_logs_alarm(self, log_group_name, filter_text, metric_uid, routing_tags, alarm_description=None
    ):
        """
        Provision Cloud watch logs based alarm.

        @return:
        :param routing_tags:
        :param metric_uid:
        :param filter_text:
        :param message_dict: extensive data to be stored in alert description
        :param log_group_name:
        """

        if not alarm_description:
            alarm_description = {}
        alarm_description["log_group_name"] = log_group_name
        alarm_description["log_group_filter_pattern"] = filter_text
        alarm_description["routing_tags"] = routing_tags
        if not log_group_name or not isinstance(log_group_name, str):
            raise ValueError(f"{log_group_name=}")
        if not isinstance(routing_tags, list):
            raise ValueError(
                f"Routing tags must be a list, received: '{alarm_description}'"
            )
        if len(routing_tags) == 0:
            raise ValueError(f"No routing tags: received: '{alarm_description}'")

        metric_filter = self.provision_log_group_metric_filter(log_group_name, metric_uid, filter_text)

        alarm = CloudWatchAlarm({})
        alarm.region = self.region
        alarm.name = f"has2-alarm-{log_group_name}-{metric_uid}"
        alarm.actions_enabled = True
        alarm.alarm_description = json.dumps(alarm_description)
        alarm.metric_name = metric_filter.name
        # todo: remove after test: alarm.metric_name = metric_filter.metric_transformations[0]["metricName"]
        alarm.namespace = log_group_name
        alarm.statistic = "Sum"
        alarm.period = 300
        alarm.evaluation_periods = 1
        alarm.datapoints_to_alarm = 1
        alarm.threshold = 0.0
        alarm.comparison_operator = "GreaterThanThreshold"
        alarm.treat_missing_data = "notBreaching"
        self.provision_cloudwatch_alarm(alarm)
        self.trigger_log_filter_text_alarm(log_group_name, [f"{filter_text}: Neo, the Horey has you!"])
        # todo: self.test_end_to_end_log_pattern_alert()
        return alarm

    def provision_log_group_metric_filter(self, log_group_name, metric_uid, filter_text):
        """
        Create/Update filter

        :param filter_text:
        :param log_group_name:
        :param metric_uid:
        :return:
        """

        metric_filter = CloudWatchLogGroupMetricFilter({})
        metric_filter.log_group_name = log_group_name
        metric_filter.name = f"has2-metric-filter-{log_group_name}-{metric_uid}"
        metric_filter.filter_pattern = filter_text
        metric_filter.metric_transformations = [
            {
                "metricName": metric_filter.name,
                "metricNamespace": log_group_name,
                "metricValue": "1",
            }
        ]
        metric_filter.region = self.region
        self.aws_api.cloud_watch_logs_client.provision_metric_filter(metric_filter)
        return metric_filter

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

        alarm = CloudWatchAlarm({})
        alarm.region = self.region
        alarm.name = (
            f"has2_alarm-{sqs_queue_name}-ApproximateNumberOfMessagesVisible"
        )
        alarm.actions_enabled = True
        if "queue_name" not in message_data:
            dict_base = {"queue_name": sqs_queue_name}
            dict_base.update(message_data)
            alarm.alarm_description = json.dumps(dict_base)
        else:
            alarm.alarm_description = json.dumps(message_data)

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

        :param lambda_files:
        :param event_json_file_path:
        :return:
        """
        raise DeprecationWarning("Use the new trigger_lambda_handler_locally")

    def send_message_to_sns(self, message, topic_arn=None, subject="Default SNS Message Subject"):
        """
        Send message to self sns_topic.

        :param subject:
        :param topic_arn:
        :param message:
        :return:
        """

        if isinstance(message, dict):
            message = json.dumps(message)
        if not isinstance(message, str):
            raise RuntimeError(f"Message should be either dict or str: {type(message)}, {message}")

        if topic_arn is None:
            topic = SNSTopic({})
            topic.name = self.configuration.sns_topic_name
            topic.region = self.region
            self.aws_api.sns_client.update_topic_information(topic, full_information=False)
            topic_arn = topic.arn

        self.aws_api.sns_client.raw_publish(topic_arn, subject, message)

    def trigger_self_monitoring_log_error_alarm(self):
        """
        Trigger the alarm using cloudwatch log stream filter metric.

        :return:
        """

        log_group = CloudWatchLogGroup({})
        log_group.region = self.region
        log_group.name = self.configuration.alert_system_lambda_log_group_name

        return self.aws_api.cloud_watch_logs_client.put_log_lines(log_group, [f"{AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_LOG_ERROR_FILTER_PATTERN}: Neo, the Horey has you!"])

    def trigger_self_monitoring_log_timeout_alarm(self):
        """
        Test
        # Old: datetime.datetime.utcnow(),

        dict_request = {"Namespace": self.configuration.alert_system_lambda_log_group_name,
                        "MetricData": [
                            {"MetricName": f"metric-{self.configuration.self_monitoring_log_timeout_metric_name_raw}",
                             "Timestamp": datetime.datetime.now(datetime.UTC),
                             "Value": 1
                             }]}
        self.aws_api.cloud_watch_client.put_metric_data_raw(self.region, dict_request)
        :return:
        """
        return self.trigger_log_filter_text_alarm(self.configuration.alert_system_lambda_log_group_name,
                                                  [f"{AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_LOG_TIMEOUT_FILTER_PATTERN}: Neo, the Horey has you!"])

    def trigger_log_filter_text_alarm(self, log_group_name, lines):
        """
        Write log lines to log group to trigger self lambda.

        :param log_group_name:
        :param lines:
        :return:
        """

        log_group = CloudWatchLogGroup({})
        log_group.region = self.region
        log_group.name = log_group_name
        return self.aws_api.cloud_watch_logs_client.put_log_lines(log_group, lines)

    def trigger_self_monitoring_errors_metric_alarm(self):
        """
        These are built in metrics. So we can not change the metric itself and must move
        one step further - set alarm state manually.

        :return:
        """

        dict_request = {"AlarmName": f"{self.configuration.lambda_name}-metric-errors",
                        "StateValue": "ALARM",
                        "StateReason": "Explicitly changed state to ALARM"}
        return self.aws_api.cloud_watch_client.set_alarm_state_raw(self.region, dict_request)

    def trigger_self_monitoring_duration_alarm(self):
        """
        These are built in metrics. So we can not change the metric itself and must move
        one step further - set alarm state manually.

        :return:
        """

        dict_request = {"AlarmName": f"{self.configuration.lambda_name}-metric-duration",
                        "StateValue": "ALARM",
                        "StateReason": "Explicitly changed state to ALARM"}
        return self.aws_api.cloud_watch_client.set_alarm_state_raw(self.region, dict_request)

    def provision_ses_email_identity(self, email_identity):
        """
        Update self monitoring data and provision.

        :param email_identity:
        :return:
        """

        topic = SNSTopic({})
        topic.name = self.configuration.sns_topic_name
        topic.region = self.region
        if not self.aws_api.sns_client.update_topic_information(topic, full_information=False):
            raise RuntimeError("Could not update topic information")

        email_identity.bounce_topic = topic.arn
        email_identity.complaint_topic = topic.arn
        email_identity.delivery_topic = topic.arn

        email_identity.headers_in_bounce_notifications_enabled = True
        email_identity.headers_in_complaint_notifications_enabled = True
        email_identity.headers_in_delivery_notifications_enabled = True
        self.aws_api.provision_ses_domain_email_identity(email_identity)

    def set_alarm_ok(self, alarm):
        """
        Change the alarm state.

        :param alarm:
        :return:
        """

        dict_request = {"AlarmName": alarm.name,
                        "StateValue": "OK",
                        "StateReason": "Explicitly changed state to OK"}

        return self.aws_api.cloud_watch_client.set_alarm_state_raw(self.region, dict_request)

    def test_end_to_end_log_pattern_alert(self, log_group_name, line, alarm):
        """
        Check the

        :return:
        """
        log_group = CloudWatchLogGroup({})
        log_group.region = self.region
        log_group.name = log_group_name

        response = self.aws_api.cloud_watch_logs_client.put_log_lines(log_group, [line])
        log_line_written_time = email.utils.parsedate_to_datetime(response["ResponseMetadata"]["HTTPHeaders"]["date"])
        stream_last_event_max_limit = log_line_written_time - datetime.timedelta(hours=1)

        yield_log_group_streams_request = {"logGroupName": log_group_name,
                        "orderBy": "LastEventTime",
                        "descending": True}
        limit_time = datetime.datetime.now() + datetime.timedelta(seconds=alarm.period+5)
        start_waiting = perf_counter()

        while datetime.datetime.now() < limit_time:
            analized_streams_counter = 0
            for stream in self.aws_api.cloud_watch_logs_client.yield_log_group_streams_raw(self.region,
                                                                                                   yield_log_group_streams_request):
                analized_streams_counter += 1
                last_event_timestamp = CommonUtils.timestamp_to_datetime(stream.last_event_timestamp / 1000)
                if last_event_timestamp < stream_last_event_max_limit:
                    logger.info(f"Analyzed {analized_streams_counter} streams, reached time limit")
                    break

                # AWS has a delay in this param change so this filter can not work.
                # if last_event_timestamp < log_line_written_time:
                #     continue

                for event in self.aws_api.cloud_watch_logs_client.yield_log_events(log_group, stream, filters_req={"startFromHead": False}):
                    if event["message"] == line:
                        continue

                    if "Handling event" not in event["message"]:
                        continue

                    if alarm.arn not in event["message"]:
                        continue

                    event_ingestion_time = CommonUtils.timestamp_to_datetime(event["ingestionTime"]/1000)
                    if event_ingestion_time < log_line_written_time:
                        continue

                    end_waiting = perf_counter()
                    total_time = end_waiting - start_waiting
                    logger.info(f"Total time since publish to handle: {total_time}")
                    return total_time
        raise RuntimeError("Reached timeout")


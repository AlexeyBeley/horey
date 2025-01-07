"""
AlertSystem deployment and testing module.
It is responsible to Manage all parts of the system:
SNS, Cloudwatch Log Filter, Cloudwatch Alarms and AlertSystemLambda.

"""

import copy
import datetime
import json
import os
import pathlib
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
from horey.aws_api.aws_services_entities.iam_policy import IamPolicy
from horey.aws_api.aws_services_entities.sns_subscription import SNSSubscription
from horey.aws_api.aws_services_entities.sns_topic import SNSTopic
from horey.aws_api.aws_services_entities.dynamodb_table import DynamoDBTable
from horey.aws_api.aws_services_entities.sesv2_configuration_set import SESV2ConfigurationSet
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm
from horey.aws_api.aws_services_entities.cloud_watch_log_group_metric_filter import (
    CloudWatchLogGroupMetricFilter,
)
from horey.aws_api.aws_services_entities.event_bridge_target import EventBridgeTarget
from horey.aws_api.aws_services_entities.event_bridge_rule import EventBridgeRule
from horey.aws_api.aws_services_entities.cloud_watch_log_group import CloudWatchLogGroup
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy
from horey.pip_api.pip_api import PipAPI
from horey.pip_api.pip_api_configuration_policy import PipAPIConfigurationPolicy

from horey.alert_system.lambda_package.notification import Notification

logger = get_logger()
BashExecutor.set_logger(logger, override=False)


class AlertSystem:
    """
    Alert system management class.

    """

    def __init__(self, configuration: AlertSystemConfigurationPolicy, aws_api=None):
        self.configuration = configuration
        self.packer = Packer()
        self.aws_api = aws_api or AWSAPI()
        try:
            self.region = Region.get_region(self.configuration.region)
            if AWSAccount.get_default_region() is None:
                AWSAccount.set_aws_default_region(self.region)
        except configuration.UndefinedValueError:
            pass
        try:
            self.tags = configuration.tags
        except configuration.UndefinedValueError:
            pass

        pip_api_configuration = PipAPIConfigurationPolicy()
        try:
            pip_api_configuration.multi_package_repositories = {"horey.": configuration.horey_repo_path}
            pip_api_configuration.horey_parent_dir_path = os.path.dirname(configuration.horey_repo_path)
        except configuration.UndefinedValueError:
            pass
        pip_api_configuration.venv_dir_path = configuration.deployment_venv_path
        self._lambda_arn = None
        self.pip_api = PipAPI(configuration=pip_api_configuration)
        if self.configuration.routing_tags is None:
            self.configuration.routing_tags = [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG]

    @property
    def lambda_arn(self):
        if self._lambda_arn is None:
            aws_lambda = AWSLambda({})
            aws_lambda.name = self.configuration.lambda_name
            aws_lambda.region = self.region

            if not self.aws_api.lambda_client.update_lambda_information(
                    aws_lambda, full_information=False
            ):
                raise RuntimeError("Could not update aws_lambda information")

            self._lambda_arn = aws_lambda.arn
        return self._lambda_arn

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
        self.provision_dynamodb()
        self.provision_event_bridge_rule()
        aws_lambda = self.provision_lambda(lambda_files)
        self.provision_event_bridge_rule(aws_lambda=aws_lambda)
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
        self.validate_lambda_package(zip_file_path, event=event)
        return zip_file_path

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

        alarm = self.provision_self_monitoring_event_bridge_successful_invocations_alarm()
        self.aws_api.cloud_watch_client.set_alarm_state(alarm, "ALARM")

    def provision_self_monitoring_log_error_alarm(self):
        """
        Find [ERROR] log messages in self log.

        @return:
        """

        filter_text = f'"{AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_LOG_ERROR_FILTER_PATTERN}"'
        alarm_description = {
            "lambda_name": self.configuration.lambda_name,
            AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY: AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_VALUE}
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
                             AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY: AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_VALUE}
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
                             AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY: AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_VALUE}
        alarm.alarm_description = json.dumps(alarm_description)

        self.provision_cloudwatch_alarm(alarm)
        return alarm

    def provision_self_monitoring_event_bridge_successful_invocations_alarm(self):
        """
        Provision cloudwatch metric EventBridge Successful Invocations
        It should be equal to 5 in 5 minutes.

        @return:
        """

        alarm = CloudWatchAlarm({})
        alarm.name = f"has2-{self.configuration.lambda_name}-eventbridge-successful-invocations"
        alarm.actions_enabled = True
        alarm.insufficient_data_actions = []
        alarm.metric_name = "Invocations"
        alarm.namespace = "AWS/Events"
        alarm.statistic = "Sum"
        alarm.dimensions = [
            {"Name": "RuleName", "Value": self.configuration.event_bridge_rule_name}
        ]
        alarm.period = 300
        alarm.evaluation_periods = 1
        alarm.datapoints_to_alarm = 1
        alarm.threshold = 5.0
        alarm.comparison_operator = "LessThanThreshold"
        alarm.treat_missing_data = "notBreaching"

        alarm_description = {"routing_tags": [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG],
                             "lambda_name": self.configuration.lambda_name,
                             AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY: AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_VALUE}
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
                             AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY: AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_VALUE}
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
            ),
            force_reinstall=True
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
        lambda_package_configuration.notification_channels = [os.path.basename(notification_channel_file_path) for
                                                              notification_channel_file_path in
                                                              lambda_package_configuration.notification_channels]
        if self.configuration.message_classes:
            notification_channels_and_message_classes_file_paths += self.configuration.message_classes[:]
            lambda_package_configuration.message_classes = [os.path.basename(message_class_file_path) for
                                                            message_class_file_path in
                                                            lambda_package_configuration.message_classes]

        lambda_package_configuration.generate_configuration_file(alert_system_config_file_path)

        self.packer.add_files_to_zip(
            self.configuration.lambda_zip_file_name, files + [lambda_handler_file_path,
                                                              alert_system_config_file_path] + notification_channels_and_message_classes_file_paths
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
        return self.trigger_lambda_handler_locally_python(extraction_dir, event)

    @staticmethod
    def trigger_lambda_handler_locally_python(extraction_dir, event):
        """
        Run the lambda handler locally

        :param extraction_dir:
        :param event:
        :return:
        """

        shutil.copy2(os.path.join(os.path.dirname(__file__), "tests", "trigger_local.py"),
                     extraction_dir)
        curdir = pathlib.Path(".").resolve()
        os.chdir(extraction_dir)
        try:
            main_function = CommonUtils.load_object_from_module_raw(extraction_dir / "trigger_local.py", "main")
            return main_function(event)
        finally:
            os.chdir(curdir)

    @staticmethod
    def trigger_lambda_handler_locally_bash(extraction_dir, event):
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
        validation_dir_path = os.path.splitext(zip_file_path)[
                                  0
                              ] + "_validation"
        try:
            os.makedirs(validation_dir_path)
        except FileExistsError:
            shutil.rmtree(validation_dir_path)
            os.makedirs(validation_dir_path)

        tmp_zip_path = os.path.join(
            validation_dir_path, self.configuration.lambda_zip_file_name
        )
        shutil.copyfile(zip_file_path, tmp_zip_path)
        self.packer.extract(tmp_zip_path, validation_dir_path)
        return pathlib.Path(validation_dir_path)

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
        iam_role.inline_policies = [self.generate_inline_dynamodb_policy(), self.generate_inline_cloudwatch_policy()]
        tags = copy.deepcopy(self.tags)
        tags.append({"Key": "name", "Value": iam_role.name})
        iam_role.tags = tags
        self.aws_api.provision_iam_role(iam_role)
        return iam_role

    def generate_inline_dynamodb_policy(self):
        """
        DynamoDB access

        :return:
        """
        policy = IamPolicy({})
        policy.document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": [
                        "dynamodb:PutItem",
                        "dynamodb:UpdateItem",
                        "dynamodb:GetItem",
                        "dynamodb:Scan",
                        "dynamodb:DescribeTable",
                        "dynamodb:ListTagsOfResource",
                        "dynamodb:DeleteItem"
                    ],
                    "Resource": [
                        f"arn:aws:dynamodb:{self.configuration.region}:{self.aws_api.dynamodb_client.account_id}:table/{self.configuration.dynamodb_table_name}",
                        f"arn:aws:dynamodb:{self.configuration.region}:{self.aws_api.dynamodb_client.account_id}:table/{self.configuration.dynamodb_table_name}//index/*"
                    ],
                    "Effect": "Allow"
                }
            ]
        }
        policy.name = "inline_dynamodb"
        policy.description = "DynamoDB access policy"
        policy.tags = copy.deepcopy(self.tags)
        policy.tags.append({
            "Key": "Name",
            "Value": policy.name
        })
        return policy

    def generate_inline_cloudwatch_policy(self):
        """
        Cloudwatch access

        :return:
        """

        policy = IamPolicy({})
        policy.document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": [
                        "cloudwatch:SetAlarmState"
                    ],
                    "Resource": [
                        f"arn:aws:cloudwatch:{self.configuration.region}:{self.aws_api.dynamodb_client.account_id}:alarm:*"
                    ],
                    "Effect": "Allow"
                }
            ]
        }
        policy.name = "inline_cloudwatch"
        policy.description = "Cloudwatch access policy"
        policy.tags = copy.deepcopy(self.tags)
        policy.tags.append({
            "Key": "Name",
            "Value": policy.name
        })
        return policy

    def deploy_lambda(self):
        """
        Deploy the lambda object into AWS service.

        @return:
        """

        events_rule = EventBridgeRule({})
        events_rule.name = self.configuration.event_bridge_rule_name
        events_rule.region = self.region
        self.aws_api.events_client.update_rule_information(events_rule)

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
                },
                {"Sid": f"trigger_{self.configuration.lambda_name}",
                 "Effect": "Allow",
                 "Principal": {"Service": "events.amazonaws.com"},
                 "Action": "lambda:InvokeFunction",
                 "Resource": None,
                 "Condition": {"ArnLike": {
                     "AWS:SourceArn": events_rule.arn}}}
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

    def provision_dynamodb(self):
        """
        Used for alert status storing.
        {'sensor_uid': {'S': 'test_manual'}, 'alarm_state': {'M': {'cooldown_time': {'N': '300'}, 'epoch_triggered': {'N': '11111111111111'}}}}
        {'sensor_uid': {'S': 'test_manual2'}}

        :return:
        """

        table = DynamoDBTable({})
        table.name = self.configuration.dynamodb_table_name
        table.region = self.region
        table.billing_mode = "PAY_PER_REQUEST"
        table.attribute_definitions = [
            {
                "AttributeName": "alarm_name",
                "AttributeType": "S"
            }
        ]

        table.key_schema = [
            {
                "AttributeName": "alarm_name",
                "KeyType": "HASH"
            }
        ]

        table.tags = copy.deepcopy(self.tags)
        table.tags.append({
            "Key": "Name",
            "Value": table.name
        })
        self.aws_api.dynamodb_client.provision_table(table)

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

    # pylint: disable = too-many-arguments
    def provision_cloudwatch_logs_alarm(self, log_group_name, filter_text, metric_uid, routing_tags,
                                        alarm_description=None
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

        return self.aws_api.cloud_watch_logs_client.put_log_lines(log_group, [
            f"{AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_LOG_ERROR_FILTER_PATTERN}: Neo, the Horey has you!"])

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
                                                  [
                                                      f"{AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_LOG_TIMEOUT_FILTER_PATTERN}: Neo, the Horey has you!"])

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
        limit_time = datetime.datetime.now() + datetime.timedelta(seconds=alarm.period + 5)
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

                for event in self.aws_api.cloud_watch_logs_client.yield_log_events(log_group, stream, filters_req={
                    "startFromHead": False}):
                    if event["message"] == line:
                        continue

                    if "Handling event" not in event["message"]:
                        continue

                    if alarm.arn not in event["message"]:
                        continue

                    event_ingestion_time = CommonUtils.timestamp_to_datetime(event["ingestionTime"] / 1000)
                    if event_ingestion_time < log_line_written_time:
                        continue

                    end_waiting = perf_counter()
                    total_time = end_waiting - start_waiting
                    logger.info(f"Total time since publish to handle: {total_time}")
                    return total_time
        raise RuntimeError("Reached timeout")

    def provision_event_bridge_rule(self, aws_lambda=None):
        """
        Event bridge rule - the trigger used to trigger the lambda each minute.

        :return:
        """

        rule = EventBridgeRule({})
        rule.name = self.configuration.event_bridge_rule_name
        rule.description = "Triggering rule for alert system lambda"
        rule.region = self.region
        rule.schedule_expression = "rate(1 minute)"
        rule.event_bus_name = "default"
        rule.state = "ENABLED"
        rule.tags = copy.deepcopy(self.tags)
        rule.tags.append({
            "Key": "name",
            "Value": rule.name
        })

        if aws_lambda is not None:
            target = EventBridgeTarget({})
            target.id = f"target-{self.configuration.lambda_name}"
            target.arn = aws_lambda.arn
            rule.targets.append(target)

        self.aws_api.provision_events_rule(rule)
        return rule

    def trigger_lambda_with_raw_event(self, event_dict):
        """
        Trigger the deployed lambda.

        :param event_dict:
        :return:
        """

        errors = []
        mandatory = {
            "routing_tags": list,
            "type": list,
            "text": str,
            "header": str,
        }
        optional = {"link": str,
                    "link_href": str}

        for key in mandatory:
            if key not in event_dict:
                errors.append(f"Mandatory key {key} is not present in {event_dict}")

        if errors:
            raise ValueError("\n".join(errors))

        breakpoint()
        request = {"": ""}
        ret = self.aws_api.lambda_client.invoke_raw(self.region, request)

    def generate_resource_alarms(self, resource_alarms_builder,
                                 metric_data_start_time=None,
                                 metric_data_end_time=None,
                                 metric_name=None):
        """
        Generate alarms based on 2 weeks data

        :param metric_name:
        :param metric_data_end_time:
        :param metric_data_start_time:
        :param resource_alarms_builder:
        :return:
        """

        metric_filters = resource_alarms_builder.generate_cluster_metric_filters()

        all_metrics = []
        for filters_req in metric_filters:
            metrics_fetched_from_aws = list(
                self.aws_api.cloud_watch_client.yield_client_metrics(self.region,
                                                                     filters_req=filters_req))
            if not metrics_fetched_from_aws:
                logger.warning(f"Was not able to find metrics by filter {filters_req}")
                continue

            filter_dimensions = {dim["Name"]: dim["Value"] for dim in filters_req["Dimensions"]}
            metrics_fetched_from_aws_filtered_by_request_dimensions = [result for result in metrics_fetched_from_aws if
                                                                       {dim["Name"]: dim["Value"] for dim in
                                                                        result["Dimensions"]} == filter_dimensions]
            if not metrics_fetched_from_aws_filtered_by_request_dimensions:
                raise RuntimeError(f"Was not able to find metrics: {filters_req}")

            if metric_name:
                metrics_fetched_from_aws_filtered_by_request_dimensions = [metric_raw for metric_raw in
                                                                           metrics_fetched_from_aws_filtered_by_request_dimensions \
                                                                           if metric_raw["MetricName"] == metric_name]

            all_metrics += metrics_fetched_from_aws_filtered_by_request_dimensions

        return self.generate_alarms_from_metrics(resource_alarms_builder, all_metrics,
                                                 metric_data_start_time=metric_data_start_time,
                                                 metric_data_end_time=metric_data_end_time)

    def generate_alarms_from_metrics(self, resource_alarms_builder, metrics, metric_data_start_time=None,
                                     metric_data_end_time=None):
        """
        Filtered resource metrics transformed into alarms.

        :param metric_data_start_time:
        :param metric_data_end_time:
        :param resource_alarms_builder:
        :param metrics:
        :return:
        """

        lst_ret = []
        lst_del = []

        for i, metric_raw in enumerate(metrics):
            logger.info(f"Generated alarms for {i}/{len(metrics)} metrics")

            all_metric_values = self.get_metric_statistics(metric_raw, start_time=metric_data_start_time,
                                                           end_time=metric_data_end_time)

            min_value, max_value = resource_alarms_builder.generate_metric_alarm_limits(metric_raw, all_metric_values)
            slug = resource_alarms_builder.generate_metric_alarm_slug(metric_raw)

            alarm = self.get_base_alarm(f"{self.configuration.lambda_name}-{slug}_min", metric_raw, min_value,
                                        "LessThanThreshold")
            if min_value is not None:
                lst_ret.append(alarm)
            else:
                lst_del.append(alarm)

            alarm = self.get_base_alarm(f"{self.configuration.lambda_name}-{slug}_max", metric_raw, max_value,
                                        "GreaterThanThreshold")
            if max_value is not None:

                lst_ret.append(alarm)
            else:
                lst_del.append(alarm)
        logger.info(f"Generated alarms from metrics. To add: {len(lst_ret)}, to delete: {len(lst_del)}")
        return lst_ret, lst_del

    def generate_builder_filtered_resource_alarms(self, resource_alarms_builder, metrics,
                                                  metric_data_start_time=None,
                                                  metric_data_end_time=None):
        """
        Let the builder filter alarms itself.

        :param metric_data_end_time:
        :param metric_data_start_time:
        :param resource_alarms_builder:
        :param metrics:
        :return:
        """

        all_metrics = resource_alarms_builder.filter_metrics(metrics)
        return self.generate_alarms_from_metrics(resource_alarms_builder, all_metrics,
                                                 metric_data_start_time=metric_data_start_time,
                                                 metric_data_end_time=metric_data_end_time)

    def get_base_alarm(self, name, metric_raw, threshold, comparison_operator):
        """
        Generate template alarm.

        :return:
        """

        if len(name) > 255:
            raise ValueError(f"Alarm name can be up to 255 chars: {len(name)=} {name=}")

        alarm = CloudWatchAlarm({})
        alarm.name = name
        alarm.actions_enabled = True
        alarm.insufficient_data_actions = []
        alarm.metric_name = metric_raw["MetricName"]
        alarm.namespace = "AWS/RDS"
        alarm.statistic = "Average"
        alarm.dimensions = metric_raw["Dimensions"]
        alarm.period = 60
        alarm.evaluation_periods = 3
        alarm.datapoints_to_alarm = 3
        alarm.threshold = threshold
        alarm.comparison_operator = comparison_operator
        alarm.treat_missing_data = "notBreaching"

        alarm_description = {"routing_tags": self.configuration.routing_tags}
        alarm.alarm_description = json.dumps(alarm_description)
        alarm.region = self.region
        alarm.ok_actions = [self.lambda_arn]
        alarm.alarm_actions = [self.lambda_arn]
        return alarm

    def get_metric_statistics(self, metric_raw, start_time=None, end_time=None):
        """
        Find proper value
        Start time between 3 hours and 15 days ago - Use a multiple of 60 seconds (1 minute).
        Start time between 15 and 63 days ago - Use a multiple of 300 seconds (5 minutes).
        Start time greater than 63 days ago - Use a multiple of 3600 seconds (1 hour).

        :return:
        """

        now = datetime.datetime.now(datetime.timezone.utc)
        if end_time and end_time > now:
            raise ValueError("Maximal end time can be now or less")
        end_time = end_time or now

        # about 8 seconds to the end of 15 days
        minimal_possible_time = now - datetime.timedelta(seconds=int(14.9999 * 24 * 60 * 60))
        if start_time and start_time < minimal_possible_time:
            raise ValueError("Minimal start time must be greater then 15 days from now")
        if end_time < minimal_possible_time:
            raise ValueError("Maximal end time must be greater then 15 days from now")

        start_time = start_time or minimal_possible_time
        seconds = int((end_time - start_time).total_seconds())

        statistics = ["SampleCount", "Average", "Sum", "Minimum", "Maximum"]
        period = 60
        all_metric_values = self.get_metric_statistics_helper(metric_raw, statistics, end_time, seconds, period)

        return all_metric_values

    def get_metric_statistics_helper(self, metric_raw, statistics, end_time, seconds, period):
        """
        Loop over metric statistics:
        'You have requested up to 10800 datapoints, which exceeds the limit of 1440. You may reduce the datapoints requested by increasing Period, or decreasing the time range.'

        :param metric_raw:
        :param statistics:
        :param end_time:
        :param seconds:
        :param period:
        :return:
        """

        ret = []
        while seconds > 0:
            seconds_delta = min(period * 1440, seconds)
            start_time = end_time - datetime.timedelta(seconds=seconds_delta)
            request_dict = {"Namespace": metric_raw["Namespace"],
                            "MetricName": metric_raw["MetricName"],
                            "Statistics": statistics,
                            "StartTime": start_time,
                            "EndTime": end_time,
                            "Dimensions": metric_raw["Dimensions"],
                            "Period": period
                            }
            for response in self.aws_api.cloud_watch_client.get_metric_statistics_raw(
                    self.region, request_dict):
                ret += response["Datapoints"]

            seconds -= seconds_delta
            end_time = start_time

        return ret

    def analyze_metric(self, metric_raw):
        """
        Graphical show results

        :param metric_raw:
        :return:
        """
        delta = datetime.timedelta(seconds=60*60*24*14)
        filters_req = {"MetricDataQueries": [{"Id": "max", "MetricStat": {"Metric": metric_raw,
                                                                           "Period": 60,
                                                                           "Stat": "Maximum"
                                                                           }},
                                             {"Id": "minimum", "MetricStat": {"Metric": metric_raw,
                                                                           "Period": 60,
                                                                           "Stat": "Minimum"
                                                                           }}
                                             ],
                       "StartTime": datetime.datetime.now() - delta,
                       "EndTime": datetime.datetime.now()}

        ret = self.aws_api.cloud_watch_client.get_metric_data_raw(self.region, filters_req)
        max_values = ret[0]["MetricDataResults"][0]["Values"]
        import matplotlib.pyplot as plt
        values_range = max(max_values) - min(max_values)
        bins = [min(max_values) + (i * values_range) / 10000 for i in range(10000)]
        ret, bins, patches = plt.hist(max_values, bins=bins)
        plt.show()


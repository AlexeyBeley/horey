import datetime
import json
import os
import pdb
import shutil
import uuid


from horey.h_logger import get_logger
from horey.common_utils.common_utils import CommonUtils
from horey.serverless.packer.packer import Packer
from horey.aws_api.aws_services_entities.aws_lambda import AWSLambda
from horey.aws_api.base_entities.region import Region
from horey.slack_api.slack_api_configuration_policy import SlackAPIConfigurationPolicy
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.aws_api.aws_services_entities.iam_role import IamRole
from horey.aws_api.aws_services_entities.iam_policy import IamPolicy

from horey.aws_api.aws_services_entities.sns_subscription import SNSSubscription
from horey.aws_api.aws_services_entities.sns_topic import SNSTopic
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm
from horey.aws_api.aws_services_entities.cloud_watch_log_group_metric_filter import CloudWatchLogGroupMetricFilter
from horey.alert_system.lambda_package.message import Message
from horey.alert_system.lambda_package.notification_channel_base import NotificationChannelBase


logger = get_logger()


class AlertSystem:
    def __init__(self, configuration):
        self.configuration = configuration
        self.packer = Packer()
        self.aws_api = AWSAPI()
        self.region = Region.get_region(self.configuration.region)

    def provision(self, tags, lambda_files):
        self.provision_sns_topic(tags)
        self.provision_lambda(lambda_files)
        self.provision_sns_subscription()

        self.provision_self_monitoring()

    def provision_lambda(self, files):
        self.create_lambda_package(files)
        return self.deploy_lambda()

    def provision_self_monitoring(self):
        self.provision_self_monitoring_log_error_alarm()
        self.provision_self_monitoring_log_timeout_alarm()
        self.provision_self_monitoring_errors_metric_alarm()
        self.provision_self_monitoring_duration_alarm()

    def provision_self_monitoring_log_error_alarm(self):
        """
        /aws/lambda/alert_system_test_deploy_lambda

        @return:
        """

        log_group_name = f"/aws/lambda/{self.configuration.lambda_name}"
        filter_text = '"[ERROR]"'
        metric_name_raw = f"{self.configuration.lambda_name}-log-error"
        message_data = {"tags": "alert_system"}
        self.provision_cloudwatch_logs_alarm(log_group_name, filter_text, metric_name_raw, message_data)

    def provision_self_monitoring_log_timeout_alarm(self):
        log_group_name = f"/aws/lambda/{self.configuration.lambda_name}"
        filter_text = "Task timed out after"
        metric_name_raw = f"{self.configuration.lambda_name}-log-timeout"
        message_data = {"tags": "alert_system"}
        self.provision_cloudwatch_logs_alarm(log_group_name, filter_text, metric_name_raw, message_data)

    def provision_self_monitoring_duration_alarm(self):
        message = Message()
        message.uuid = str(uuid.uuid4())
        message.type = "cloudwatch-metric-lambda-duration"
        message.data = {"tags": ["alert_system"]}

        alarm = CloudWatchAlarm({})
        alarm.name = f"{self.configuration.lambda_name}-metric-duration"
        alarm.actions_enabled = True
        alarm.alarm_description = json.dumps(message.convert_to_dict())
        alarm.insufficient_data_actions = []
        alarm.metric_name = "Duration"
        alarm.namespace = "AWS/Lambda"
        alarm.statistic = "Average"
        alarm.dimensions = [{"Name": "FunctionName", "Value": self.configuration.lambda_name}]
        alarm.period = 300
        alarm.evaluation_periods = 1
        alarm.datapoints_to_alarm = 1
        alarm.threshold = self.configuration.lambda_timeout * 0.6
        alarm.comparison_operator = "GreaterThanThreshold"
        alarm.treat_missing_data = "missing"
        self.provision_cloudwatch_alarm(alarm)

    def provision_self_monitoring_errors_metric_alarm(self):
        message = Message()
        message.uuid = str(uuid.uuid4())
        message.type = "cloudwatch-metric-lambda-duration"
        message.data = {"tags": ["alert_system"]}

        alarm = CloudWatchAlarm({})
        alarm.name = f"{self.configuration.lambda_name}-metric-errors"
        alarm.actions_enabled = True
        alarm.alarm_description = json.dumps(message.convert_to_dict())
        alarm.insufficient_data_actions = []
        alarm.metric_name = "Errors"
        alarm.namespace = "AWS/Lambda"
        alarm.statistic = "Average"
        alarm.dimensions = [{"Name": "FunctionName", "Value": self.configuration.lambda_name}]
        alarm.period = 300
        alarm.evaluation_periods = 1
        alarm.datapoints_to_alarm = 1
        alarm.threshold = 1.0
        alarm.comparison_operator = "GreaterThanThreshold"
        alarm.treat_missing_data = "missing"
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
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "lambda_package", "requirements.txt"),
            self.configuration.deployment_venv_path, self.configuration.horey_repo_path)

        self.packer.zip_venv_site_packages(self.configuration.lambda_zip_file_name,
                                           self.configuration.deployment_venv_path, "python3.8")

        external_files = [os.path.basename(file_path) for file_path in files]
        lambda_package_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lambda_package")
        lambda_package_files = [os.path.join(lambda_package_dir, file_name)
                                for file_name in os.listdir(lambda_package_dir) if file_name not in external_files]
        files_paths = lambda_package_files + files
        self.packer.add_files_to_zip(self.configuration.lambda_zip_file_name, files_paths)
        self.validate_lambda_package()

        # dir_paths = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "receiver_raw_lambda")]
        # pdb.set_trace()
        # self.packer.add_dirs_to_zip(f"{lambda_name}.zip", dir_paths)
        os.chdir(current_dir)

    def validate_lambda_package(self):
        validation_dir_name = os.path.splitext(self.configuration.lambda_zip_file_name)[0]
        os.makedirs(validation_dir_name)
        tmp_zip_path = os.path.join(validation_dir_name, self.configuration.lambda_zip_file_name)
        shutil.copyfile(self.configuration.lambda_zip_file_name, tmp_zip_path)
        self.packer.extract(tmp_zip_path, validation_dir_name)

        os.environ[NotificationChannelBase.NOTIFICATION_CHANNELS_ENVIRONMENT_VARIABLE] = "notification_channel_slack.py"
        current_dir = os.getcwd()
        os.chdir(validation_dir_name)
        message_dispatcher = CommonUtils.load_object_from_module("message_dispatcher_base.py", "MessageDispatcherBase")
        message_dispatcher.dispatch(None)
        os.chdir(current_dir)
        pdb.set_trace()

    def provision_lambda_role(self):
        iam_role = IamRole({})
        iam_role.description = f"alert_system lambda role"
        iam_role.name = self.configuration.lambda_role_name
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
        policy = IamPolicy({})
        policy.arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        iam_role.policies.append(policy)
        iam_role.policies.append(policy)
        iam_role.tags = [{
            "Key": "Name",
            "Value": iam_role.name
        }]
        self.aws_api.provision_iam_role(iam_role)
        return iam_role

    def deploy_lambda(self):
        topic = SNSTopic({})
        topic.name = self.configuration.sns_topic_name
        topic.region = self.region
        if not self.aws_api.sns_client.update_topic_information(topic):
            raise RuntimeError("Could not update topic information")

        role = self.provision_lambda_role()

        aws_lambda = AWSLambda({})
        aws_lambda.region = self.region
        aws_lambda.name = self.configuration.lambda_name
        aws_lambda.handler = "lambda_handler.lambda_handler"
        aws_lambda.runtime = "python3.8"
        aws_lambda.role = role.arn
        aws_lambda.timeout = self.configuration.lambda_timeout
        aws_lambda.memory_size = 512

        aws_lambda.tags = {"Name": aws_lambda.name}
        aws_lambda.policy = {"Version": "2012-10-17",
                             "Id": "default",
                             "Statement": [
                                 {"Sid": f"trigger_from_topic_{topic.name}",
                                  "Effect": "Allow",
                                  "Principal": {"Service": "sns.amazonaws.com"},
                                  "Action": "lambda:InvokeFunction",
                                  "Resource": None,
                                  "Condition": {"ArnLike": {
                                      "AWS:SourceArn": topic.arn}}}]}

        aws_lambda.environment = {
            "Variables": {
                NotificationChannelBase.NOTIFICATION_CHANNELS_ENVIRONMENT_VARIABLE: "notification_channel_slack.py",
                "DISABLE": "false"
            }
        }

        with open(os.path.join(self.configuration.deployment_directory_path, self.configuration.lambda_zip_file_name),
                  "rb") as myzip:
            aws_lambda.code = {"ZipFile": myzip.read()}

        self.aws_api.provision_aws_lambda(aws_lambda, force=True)
        return aws_lambda

    def provision_sns_topic(self, tags):
        """

        @return:
        """
        topic = SNSTopic({})
        topic.region = self.region
        topic.name = self.configuration.sns_topic_name
        topic.attributes = {"DisplayName": topic.name}
        topic.tags = tags
        topic.tags.append({
            "Key": "Name",
            "Value": topic.name})

        self.aws_api.provision_sns_topic(topic)

    def provision_sns_subscription(self):
        topic = SNSTopic({})
        topic.name = self.configuration.sns_topic_name
        topic.region = self.region
        if not self.aws_api.sns_client.update_topic_information(topic):
            raise RuntimeError("Could not update topic information")

        aws_lambda = AWSLambda({})
        aws_lambda.name = self.configuration.lambda_name
        aws_lambda.region = self.region

        if not self.aws_api.lambda_client.update_lambda_information(aws_lambda, full_information=False):
            raise RuntimeError("Could not update aws_lambda information")

        subscription = SNSSubscription({})
        subscription.region = self.region
        subscription.name = self.configuration.subscription_name
        subscription.protocol = "lambda"
        subscription.topic_arn = topic.arn
        subscription.endpoint = aws_lambda.arn
        self.aws_api.provision_sns_subscription(subscription)

    def provision_cloudwatch_alarm(self, alarm):
        topic = SNSTopic({})
        topic.name = self.configuration.sns_topic_name
        topic.region = self.region
        if not self.aws_api.sns_client.update_topic_information(topic):
            raise RuntimeError("Could not update topic information")

        alarm.region = self.region
        alarm.ok_actions = [topic.arn]
        alarm.alarm_actions = [topic.arn]
        self.aws_api.cloud_watch_client.set_cloudwatch_alarm(alarm)

    def generate_and_provision_cloudwatch_alarm(self, metric_name, dimensions, message):
        """
        ret = {'Records': [{'Eve
        print(ret["Records"][0]["Sns"]["Message"].replace('"', r'\"'))

        @param dimensions:
        @param message:
        @return:
        """
        topic = SNSTopic({})
        topic.name = self.configuration.sns_topic_name
        topic.region = self.region
        if not self.aws_api.sns_client.update_topic_information(topic):
            raise RuntimeError("Could not update topic information")

        alarm = CloudWatchAlarm({})
        alarm.region = self.region
        alarm.name = "test-alarm"
        alarm.actions_enabled = True
        alarm.alarm_description = json.dumps(message.convert_to_dict())
        alarm.ok_actions = [topic.arn]
        alarm.alarm_actions = [topic.arn]
        alarm.insufficient_data_actions = []
        alarm.metric_name = metric_name
        alarm.namespace = "AWS/SQS"
        alarm.statistic = "Average"
        alarm.dimensions = dimensions
        alarm.period = 300
        alarm.evaluation_periods = 1
        alarm.datapoints_to_alarm = 1
        alarm.threshold = 500.0
        alarm.comparison_operator = "GreaterThanThreshold"
        alarm.treat_missing_data = "missing"

        self.aws_api.cloud_watch_client.set_cloudwatch_alarm(alarm)

    def provision_cloudwatch_logs_alarm(self, log_group_name, filter_text, metric_name_raw, message_data):
        """
        Provision Cloud watch logs based alarm.

        @param message_data: dict
        @param filter_text:
        @param log_group_name:
        @param metric_name_raw:
        @return:
        """

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
                "metricValue": "1"
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


import datetime
import json
import os
import pdb

from horey.h_logger import get_logger
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

logger = get_logger()


class MessageReceiver:
    def __init__(self, configuration):
        self.configuration = configuration
        self.packer = Packer()
        self.aws_api = AWSAPI()
        self.region = Region.get_region(self.configuration.region)

    def provision_message_receiver(self):
        self.provision_sns_topic()
        self.provision_lambda()
        self.provision_sns_subscription()

    def provision_lambda(self):
        self.create_lambda_package()
        return self.deploy_lambda()

    def create_lambda_package(self):
        """
        Create the zip package to be deployed.

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

        lambda_package_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lambda_package")
        lambda_package_files = [os.path.join(lambda_package_dir, file_name) for file_name in os.listdir(lambda_package_dir)]
        pdb.set_trace()
        files_paths = lambda_package_files + [
            self.configuration.slack_api_configuration_file
            ]
        self.packer.add_files_to_zip(self.configuration.lambda_zip_file_name, files_paths)

        # dir_paths = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "receiver_raw_lambda")]
        # pdb.set_trace()
        # self.packer.add_dirs_to_zip(f"{lambda_name}.zip", dir_paths)
        os.chdir(current_dir)

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
        aws_lambda.timeout = 900
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
                "SLACK_API_CONFIGURATION_FILE": os.path.basename(self.configuration.slack_api_configuration_file),
                "DISABLE": "false",
            }
        }

        with open(os.path.join(self.configuration.deployment_directory_path, self.configuration.lambda_zip_file_name),
                  "rb") as myzip:
            aws_lambda.code = {"ZipFile": myzip.read()}

        self.aws_api.provision_aws_lambda(aws_lambda, force=True)
        return aws_lambda

    def provision_sns_topic(self):
        """

        @return:
        """

        topic = SNSTopic({})
        topic.region = self.region
        topic.name = self.configuration.sns_topic_name
        topic.attributes = {"DisplayName": topic.name}
        topic.tags = [{
            "Key": "Name",
            "Value": topic.name},
            {"Key": "Name_2",
             "Value": topic.name}]

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

    def provision_cloudwatch_alarm(self, dimensions, message):
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
        alarm.metric_name = "ApproximateNumberOfMessagesVisible"
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


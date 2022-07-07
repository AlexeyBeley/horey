import datetime
import os
import pdb

from horey.h_logger import get_logger
from horey.serverless.packer.packer import Packer
from horey.aws_api.aws_services_entities.aws_lambda import AWSLambda
from horey.slack_api.slack_api_configuration_policy import SlackAPIConfigurationPolicy
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy


logger = get_logger()


class MessageReceiver:
    def __init__(self, configuration):
        self.configuration = configuration
        self.packer = Packer()

    def provision_message_receiver(self, lambda_name):
        self.provision_lambda(lambda_name)
        self.provision_sns()

    def provision_lambda(self, lambda_name):
        self.create_lambda_package()
        self.deploy_lambda(lambda_name)

    def create_lambda_package(self):
        """
        Create the zip package to be deployed.

        :return:
        """

        self.packer.create_venv(self.configuration.deployment_venv_path)
        current_dir = os.getcwd()
        os.chdir(self.configuration.deployment_directory_path)
        self.packer.install_requirements(os.path.join(os.path.dirname(os.path.abspath(__file__)), "receiver_raw_lambda"), self.configuration.deployment_venv_path)

        self.packer.zip_venv_site_packages(self.configuration.lambda_zip_file_name, self.configuration.deployment_venv_path, "python3.8")

        files_paths = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "receiver_raw_lambda", "lambda_handler.py")]
        self.packer.add_files_to_zip(self.configuration.lambda_zip_file_name, files_paths)

        #dir_paths = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "receiver_raw_lambda")]
        #pdb.set_trace()
        #self.packer.add_dirs_to_zip(f"{lambda_name}.zip", dir_paths)
        os.chdir(current_dir)

    def deploy_lambda(self, lambda_name):
        pdb.set_trace()

        aws_lambda = AWSLambda({})
        aws_lambda.region = self.region
        aws_lambda.name = lambda_name
        aws_lambda.role = iam_role.arn
        aws_lambda.handler = "handler.handle"
        aws_lambda.runtime = "python3.8"
        aws_lambda.timeout = 900
        aws_lambda.memory_size = 512

        aws_lambda.tags = {tag["Key"]: tag["Value"] for tag in self.tags}
        aws_lambda.tags["Name"] = aws_lambda.name

        aws_lambda.environment = {
            "Variables": {
                "SLACK_WEBHOOK": slack_webhook,
                "DISABLE": "false",
            }
        }

        with open(os.path.join(self.configuration.deployment_directory_path, self.configuration.lambda_zip_file_name), "rb") as myzip:
            aws_lambda.code = {"ZipFile": myzip.read()}

        self.aws_api.provision_aws_lambda(aws_lambda, force=True)
        return aws_lambda

    def provision_sns(self):
        pdb.set_trace()

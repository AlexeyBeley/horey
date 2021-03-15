import pdb
import argparse
import json


from aws_api import AWSAPI
import logging
logger = logging.Logger(__name__)
from base_entities.aws_account import AWSAccount

from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.common_utils.actions_manager import ActionsManager

#AWSAccount.set_aws_account(ignore_me.acc_default)
action_manager = ActionsManager()
aws_api = AWSAPI()


# region cleanup
def cleanup_parser():
    description = "Cleanup AWS account"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--target", required=True, type=str, help="Tag name will be added, description and alias set")
    parser.add_argument("--accounts_file_path", required=True, type=str, help="Tag name will be added, description and alias set")

    return parser


def cleanup(arguments) -> None:
    print("hello ")


action_manager.register_action("cleanup", cleanup_parser, cleanup)
# endregion

# region init_and_cache
def init_and_cache_parser():
    description = "Init and cache elements"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--target", required=True, type=str, help="Object type to init")

    return parser


def init_and_cache(arguments) -> None:
    print("hello ")


action_manager.register_action("init_and_cache", init_and_cache_parser, init_and_cache)
# endregion

# region create_ec2_from_lambda
def create_ec2_from_lambda_parser():
    description = "Create ec2 instance like lambda"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--lambda_arn", required=True, type=str, help="Lambda arn")
    return parser


def create_ec2_from_lambda(arguments) -> None:
    aws_api.create_ec2_from_lambda(arguments.lambda_arn)


action_manager.register_action("create_ec2_from_lambda", create_ec2_from_lambda_parser, create_ec2_from_lambda)
# endregion

if __name__ == "__main__":
    action_manager.call_action()

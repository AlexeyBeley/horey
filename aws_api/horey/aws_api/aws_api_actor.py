import pdb
import argparse
import os

import logging
logger = logging.Logger(__name__)

from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.common_utils.actions_manager import ActionsManager

#AWSAccount.set_aws_account(ignore_me.acc_default)
action_manager = ActionsManager()


# region cleanup
def cleanup_parser():
    description = "Cleanup AWS account"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--target", required=True, type=str, help="Object type to cleanup")
    parser.add_argument("--configuration_file_full_path", required=True, type=str, help="Configuration file full path")

    return parser


def cleanup(arguments) -> None:
    configuration = AWSAPIConfigurationPolicy()
    configuration.configuration_file_full_path = arguments.configuration_file_full_path
    configuration.init_from_file()

    aws_api = AWSAPI(configuration)

    init_functions = {"interfaces": aws_api.init_network_interfaces}
    cache_files = {"interfaces": configuration.aws_api_ec2_network_interfaces_cache_file}
    output_files = {"interfaces": configuration.aws_api_cleanups_network_interfaces_report_file}

    init_functions[arguments.target](from_cache=True, cache_file=cache_files[arguments.target])
    aws_api.cleanup_report_network_interfaces(output_files[arguments.target])


action_manager.register_action("cleanup", cleanup_parser, cleanup)
# endregion


# region init_and_cache
def init_and_cache_parser():
    description = "Init and cache elements"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--target", required=True, type=str, help="Object type to init")
    parser.add_argument("--configuration_file_full_path", required=True, type=str, help="Configuration file full path")

    return parser


def init_and_cache(arguments) -> None:
    configuration = AWSAPIConfigurationPolicy()
    configuration.configuration_file_full_path = arguments.configuration_file_full_path
    configuration.init_from_file()

    aws_api = AWSAPI(configuration)

    init_functions = {"interfaces": aws_api.init_network_interfaces}
    cache_files = {"interfaces": configuration.aws_api_ec2_network_interfaces_cache_file}

    objects = init_functions[arguments.target]()
    aws_api.cache_objects(objects, cache_files[arguments.target])


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

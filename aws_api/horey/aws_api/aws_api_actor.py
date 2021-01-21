import pdb
import argparse
import json


from aws_api import AWSAPI
import logging
logger = logging.Logger(__name__)
from base_entities.aws_account import AWSAccount

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

if __name__ == "__main__":
    action_manager.call_action()

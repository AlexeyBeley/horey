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


# region create_key
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


if __name__ == "__main__":
    action_manager.call_action()

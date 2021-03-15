import sys
import pdb
import argparse
import json


import ignore_me
from kms_client import KMSClient
from horey.h_logger import get_logger
logger = get_logger()
from horey.aws_api.base_entities.aws_account import AWSAccount

from horey.common_utils.actions_manager import ActionsManager

AWSAccount.set_aws_account(ignore_me.acc_mgmt)
action_manager = ActionsManager()


# region create_key
def create_key_parser():
    description = "Create KMS key"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--name", required=True, type=str, help="Tag name will be added, description and alias set")
    return parser


def create_key(arguments) -> None:
    KMSClient().create_key(name=arguments.name)


action_manager.register_action("create_key", create_key_parser, create_key)
# endregion

if __name__ == "__main__":
    action_manager.call_action()

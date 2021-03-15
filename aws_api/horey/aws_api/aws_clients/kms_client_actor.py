import sys
import pdb
import argparse
import json

sys.path.insert(0, "/Users/alexeybe/private/aws_api/src/aws_clients")
sys.path.insert(0, "/Users/alexeybe/private/aws_api/ignore")

import ignore_me
from kms_client import KMSClient
import logging
logger = logging.Logger(__name__)
from horey.aws_api.base_entities.aws_account import AWSAccount

from actions_manager import ActionsManager

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

import sys
import argparse

sys.path.insert(0, "/Users/alexeybe/private/aws_api/src/aws_clients")
sys.path.insert(0, "/Users/alexeybe/private/aws_api/ignore")

import ignore_me
from route53_client import Route53Client
import logging
logger = logging.Logger(__name__)
from aws_account import AWSAccount

from actions_manager import ActionsManager

AWSAccount.set_aws_account(ignore_me.acc_mgmt)
action_manager = ActionsManager()


# region create_key
def create_record_parser():
    description = "Create codeartifact domain"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--name", required=True, type=str, help="Domain name")
    return parser


def create_record(arguments) -> None:
    Route53Client().change_resource_record_sets(arguments.name)


action_manager.register_action("create_record", create_record_parser, create_record)
# endregion

if __name__ == "__main__":
    action_manager.call_action()

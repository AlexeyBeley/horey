import sys
import argparse


from horey.aws_api.aws_clients.sns_client import SNSClient
from horey.h_logger import get_logger

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.common_utils.actions_manager import ActionsManager
from horey.common_utils.common_utils import CommonUtils

logger = get_logger()
action_manager = ActionsManager()


# region create_key
def publish_parser():
    description = "Create codeartifact domain"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--topic_arn", required=True, type=str, help="Topic Arn")
    parser.add_argument("--message", required=True, type=str, help="Message")
    parser.add_argument("--accounts_file", required=True, type=str, help="Message")
    parser.add_argument("--account", required=True, type=str, help="Message")
    return parser


def publish(arguments) -> None:
    accounts = CommonUtils.load_object_from_module(arguments.accounts_file, "main")
    AWSAccount.set_aws_account(accounts[arguments.account])
    SNSClient().raw_publish(arguments.topic_arn, arguments.message)


action_manager.register_action("publish", publish_parser, publish)
# endregion

if __name__ == "__main__":
    action_manager.call_action()

import sys
import pdb
import argparse
import json

sys.path.insert(0, "/Users/alexeybe/private/aws_api/src/aws_clients")
sys.path.insert(0, "/Users/alexeybe/private/aws_api/ignore")

import ignore_me
from ecr_client import ECRClient
import logging
logger = logging.Logger(__name__)
from aws_account import AWSAccount

from actions_manager import ActionsManager

AWSAccount.set_aws_account(ignore_me.acc_default)
action_manager = ActionsManager()


# region get_authorization_information
def get_authorization_information_parser():
    description = "Fetch authorization ECR repository information and write it to file"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--output_file_name", required=False, type=str, default="aws_auth_info.json", help="Name of the output file")
    return parser


def get_authorization_information(arguments) -> None:
    lst_info = ECRClient().get_authorization_info()

    print(f"Writing to '{arguments.output_file_name}'")
    for dict_info in lst_info:
        dict_info["expiresAt"] = str(dict_info["expiresAt"])

    with open(arguments.output_file_name, "w+") as file_handler:
        json.dump(lst_info, file_handler, indent=4)


action_manager.register_action("get_authorization_information", get_authorization_information_parser, get_authorization_information)
# endregion


# region create_repository
def create_repository_parser():
    description = "Create containers repository"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--repository_name", required=True, type=str, help="Name repository to create")
    return parser


def create_repository(arguments) -> None:
    ECRClient().create_repository(arguments.repository_name)


action_manager.register_action("create_repository", create_repository_parser, create_repository)
# endregion

if __name__ == "__main__":
    action_manager.call_action()

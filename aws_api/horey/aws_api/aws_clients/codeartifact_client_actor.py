import sys
import pdb
import argparse
import json


import ignore_me
from codeartifact_client import CodeartifactClient
import logging

logger = logging.Logger(__name__)
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.common_utils.actions_manager import ActionsManager

AWSAccount.set_aws_account(ignore_me.acc_mgmt)
action_manager = ActionsManager()


# region create_key
def create_domain_parser():
    description = "Create codeartifact domain"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--name", required=True, type=str, help="Domain name")
    parser.add_argument(
        "--encryption_key_alias", required=True, type=str, help="Key to use"
    )
    return parser


def create_domain(arguments) -> None:
    CodeartifactClient().create_domain(arguments.name, arguments.encryption_key_alias)


action_manager.register_action("create_domain", create_domain_parser, create_domain)
# endregion


# region create_repository
def create_repository_parser():
    description = "Create codeartifact repository in domain"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--domain_name", required=True, type=str, help="Domain name")
    parser.add_argument(
        "--repository_name", required=True, type=str, help="Repository name"
    )
    return parser


def create_repository(arguments) -> None:
    CodeartifactClient().create_repository(
        arguments.domain_name, arguments.repository_name
    )


action_manager.register_action(
    "create_repository", create_repository_parser, create_repository
)
# endregion


# region create_repository
def get_repository_endpoint_parser():
    description = "Get codeartifact endpoint"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--domain_name", required=True, type=str, help="Domain name")
    parser.add_argument(
        "--repository_name", required=True, type=str, help="Repository name"
    )
    parser.add_argument(
        "--format", required=True, type=str, help="Package management format"
    )
    return parser


def get_repository_endpoint(arguments) -> None:
    CodeartifactClient().get_repository_endpoint(
        arguments.domain_name, arguments.repository_name, arguments.format
    )


action_manager.register_action(
    "get_repository_endpoint", get_repository_endpoint_parser, get_repository_endpoint
)
# endregion


if __name__ == "__main__":
    action_manager.call_action()

import sys
import pdb
import argparse
import json

import logging

from actions_manager import ActionsManager
logger = logging.Logger(__name__)

action_manager = ActionsManager()


# region get_authorization_information
def extract_parser():
    description = "Fetch authorization ECR repository information and write it to file"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--path", required=True, type=str, help="Path to the element")
    parser.add_argument("--file_name", required=True, type=str, help="Json file name")
    return parser


def extract(arguments) -> None:
    with open(arguments.file_name) as file_handler:
        json_src = json.load(file_handler)

    lst_path = arguments.path.split(",")
    print(recursive_extract(json_src, lst_path))


def recursive_extract(element, path):
    if len(path) == 0:
        return element

    if isinstance(element, list):
        return recursive_extract(element[int(path[0])], path[1:])

    if isinstance(element, dict):
        return recursive_extract(element[path[0]], path[1:])

    raise RuntimeError(f"Unknown type: {type(element)}")


action_manager.register_action("extract", extract_parser, extract)
# endregion


if __name__ == "__main__":
    action_manager.call_action()

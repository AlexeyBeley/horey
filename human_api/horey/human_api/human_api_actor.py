"""
Docker api entry point script.

"""

import argparse

from horey.common_utils.actions_manager import ActionsManager
from horey.human_api.human_api import HumanAPI

action_manager = ActionsManager()

# pylint: disable= missing-function-docstring


# region login
def validate_parser():
    description = "Validate user input"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--file_path", required=True, type=str, help="Hostname to validate to")
    return parser


def validate(arguments) -> None:
    HumanAPI().validate_daily_input(arguments.file_path)


action_manager.register_action("validate", validate_parser, validate)
# endregion

if __name__ == "__main__":
    action_manager.call_action()

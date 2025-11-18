"""
Standard Horey Actor: Script entrypoint to a python package.

"""

import argparse

from horey.selenium_api.server import Server
from horey.common_utils.actions_manager import ActionsManager

action_manager = ActionsManager()


# pylint: disable= missing-function-docstring


# region start
def start_parser():
    description = "Run server"
    parser = argparse.ArgumentParser(description=description)

    return parser


def start(arguments, configs_dict) -> None:
    server = Server()
    server.run()


action_manager.register_action("start", start_parser, start)
# endregion


if __name__ == "__main__":
    action_manager.call_action(pass_unknown_args=True)

"""
Docker api entry point script.

"""

import argparse

from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.base_entities.region import Region
from horey.h_logger import get_logger

from horey.common_utils.actions_manager import ActionsManager
from horey.free_stuff_api.free_stuff_api import FreeStuffAPI, FreeStuffAPIConfigurationPolicy


logger = get_logger()
action_manager = ActionsManager()

# pylint: disable= missing-function-docstring


# region update_component
def update_component_parser():
    description = "Login to ECR repo"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--free_stuff_api_config_file_path", required=True, type=str, help="free_stuff_api_config_file_path")
    return parser


def update_component(arguments) -> None:
    free_stuff_api_config = FreeStuffAPIConfigurationPolicy()
    # free_stuff_api_config.init_from_file(arguments.free_stuff_api_config_file_path)
    free_stuff_api = FreeStuffAPI(free_stuff_api_config)
    free_stuff_api.update_component()


action_manager.register_action("update_component", update_component_parser, update_component)
# endregion


if __name__ == "__main__":
    action_manager.call_action()

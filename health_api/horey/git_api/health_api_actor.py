"""
The entry point script to run authorization.

"""

import argparse

from horey.health_api.health_api import HealthAPI
from horey.health_api.health_api_configuration_policy import HealthAPIConfigurationPolicy

from horey.common_utils.actions_manager import ActionsManager


action_manager = ActionsManager()


# region clone
def clone_parser():
    """
    clone parser.

    @return:
    """

    description = "Install package"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--health_api_configuration", type=str)
    parser.add_argument("--requirements_file_path", type=str)
    parser.add_argument("--update", type=str, default="false")
    parser.add_argument("--update_from_source", type=str, default="false")
    return parser


def clone(arguments) -> None:
    """
    Install request

    @param arguments:
    @return:
    """

    configuration = HealthAPIConfigurationPolicy()
    configuration.remote = arguments.remote
    configuration.directory_path = arguments.directory_path
    configuration.ssh_key_file_path = arguments.ssh_key_file_path

    HealthAPI(configuration=configuration).clone()


action_manager.register_action("clone", clone_parser, clone)
# endregion

if __name__ == "__main__":
    action_manager.call_action()

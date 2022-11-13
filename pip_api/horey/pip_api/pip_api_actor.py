"""
The entry point script to run authorization.

"""

import argparse

from horey.pip_api.pip_api import PipAPI
from horey.pip_api.pip_api_configuration_policy import PipAPIConfigurationPolicy

from horey.common_utils.actions_manager import ActionsManager


action_manager = ActionsManager()


# region install
def install_parser():
    """
    install parser.

    @return:
    """

    description = "Install package"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--pip_api_configuration", type=str)
    parser.add_argument("--requirements_file_path", type=str)
    parser.add_argument("--update", type=str, default="false")
    parser.add_argument("--update_from_source", type=str, default="false")
    return parser


def install(arguments) -> None:
    """
    Install request

    @param arguments:
    @return:
    """

    configuration = PipAPIConfigurationPolicy()
    configuration.configuration_file_full_path = arguments.pip_api_configuration
    configuration.init_from_file()
    update = arguments.update.lower() == "true"
    update_from_source = arguments.update_from_source.lower() == "true"

    PipAPI(configuration=configuration).install_requirements(
        arguments.requirements_file_path,
        update=update,
        update_from_source=update_from_source,
    )


action_manager.register_action("install", install_parser, install)
# endregion

if __name__ == "__main__":
    action_manager.call_action()

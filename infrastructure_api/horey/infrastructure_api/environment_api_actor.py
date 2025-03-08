"""
Docker api entry point script.

"""

import argparse
import logging

logger = logging.Logger(__name__)

from horey.common_utils.actions_manager import ActionsManager
from horey.infrastructure_api.environment_api import EnvironmentAPI
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.aws_api.aws_api import AWSAPI


action_manager = ActionsManager()

# pylint: disable= missing-function-docstring


# region cleanup
def cleanup_parser():
    description = "Cleanup report"
    parser = argparse.ArgumentParser(description=description)
    return parser


def cleanup(arguments) -> None:
    config = EnvironmentAPIConfigurationPolicy()
    config.data_directory_path = "/tmp/horey_data"
    config.region = "us-west-2"
    aws_api = AWSAPI()
    api = EnvironmentAPI(config, aws_api)
    api.generate_cleanup_report()


action_manager.register_action("cleanup", cleanup_parser, cleanup)
# endregion

if __name__ == "__main__":
    action_manager.call_action()

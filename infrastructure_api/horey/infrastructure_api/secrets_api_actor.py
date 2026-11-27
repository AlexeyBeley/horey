"""
Secrets api entry point script.

"""

import argparse
import os
import tempfile
from pathlib import Path

from horey.aws_api.aws_api import AWSAPI
from horey.common_utils.actions_manager import ActionsManager
from horey.h_logger import get_logger
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.secrets_api import SecretsAPI
from horey.infrastructure_api.secrets_api_configuration_policy import SecretsAPIConfigurationPolicy

logger = get_logger()
action_manager = ActionsManager()

# pylint: disable= missing-function-docstring


# region get_secret_file
def get_secret_file_parser():
    description = "Download AWS Secrets Manager secret to a file"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--secret_name", required=True, type=str, help="Secret name")
    parser.add_argument("--secret_file_path", required=True, type=str, help="Destination file path")
    parser.add_argument("--region", required=True, type=str, help="Secret region")
    parser.add_argument("--data_directory_path", required=False, type=str, default="/tmp/horey_data",
                        help="Environment API working directory")
    return parser


def get_secret_file(arguments) -> Path:
    environment_api_configuration = EnvironmentAPIConfigurationPolicy()
    environment_api_configuration.region = arguments.region
    environment_api_configuration.data_directory_path = Path(arguments.data_directory_path)
    environment_api = InfrastructureAPI().get_environment_api(environment_api_configuration, AWSAPI())

    secrets_api_configuration = SecretsAPIConfigurationPolicy()
    secrets_api_configuration.region = arguments.region
    secrets_api = SecretsAPI(secrets_api_configuration, environment_api)

    secret_file_path = Path(arguments.secret_file_path)
    secret_file_path.parent.mkdir(parents=True, exist_ok=True)

    # SecretsAPI.get_secret_file saves to <dir>/<secret_name>: download to a temporary directory
    # next to the destination and move the file to the requested path.
    with tempfile.TemporaryDirectory(dir=secret_file_path.parent) as tmp_dir_path:
        downloaded_file_path = secrets_api.get_secret_file(arguments.secret_name, Path(tmp_dir_path))
        if downloaded_file_path is None:
            raise RuntimeError(f"Secret '{arguments.secret_name}' was not found")
        os.replace(downloaded_file_path, secret_file_path)

    os.chmod(secret_file_path, 0o600)
    logger.info(f"Secret '{arguments.secret_name}' saved to '{secret_file_path}'")
    return secret_file_path


action_manager.register_action("get_secret_file", get_secret_file_parser, get_secret_file)
# endregion


if __name__ == "__main__":
    action_manager.call_action()

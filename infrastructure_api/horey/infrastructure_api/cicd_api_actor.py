"""
Docker api entry point script.

"""

import argparse

from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.base_entities.region import Region
from horey.h_logger import get_logger

from horey.common_utils.actions_manager import ActionsManager
from horey.infrastructure_api.build_api_configuration_policy import BuildAPIConfigurationPolicy
from horey.infrastructure_api.environment_api import EnvironmentAPI, EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.cicd_api import CICDAPI, CICDAPIConfigurationPolicy


logger = get_logger()
action_manager = ActionsManager()

# pylint: disable= missing-function-docstring


# region trigger_hagent_job
def trigger_hagent_job_parser():
    description = "Login to ECR repo"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--env_api_config_file_path", required=True, type=str, help="env_api_config_file_path")
    parser.add_argument("--cicd_api_config_file_path", required=True, type=str, help="cicd_api_config_file_path")
    return parser


def trigger_hagent_job(arguments) -> None:
    aws_api = AWSAPI()
    env_api_config = EnvironmentAPIConfigurationPolicy()
    env_api_config.init_from_file(arguments.env_api_config_file_path)

    env_api  = EnvironmentAPI(env_api_config, aws_api)
    cicd_api_config = CICDAPIConfigurationPolicy()
    cicd_api_config.init_from_file(arguments.cicd_api_config_file_path)
    cicd_api = CICDAPI(cicd_api_config, env_api)
    cicd_api.trigger_hagent_job()


action_manager.register_action("trigger_hagent_job", trigger_hagent_job_parser, trigger_hagent_job)
# endregion


if __name__ == "__main__":
    action_manager.call_action()

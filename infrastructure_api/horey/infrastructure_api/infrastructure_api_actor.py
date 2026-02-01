"""
Docker api entry point script.

"""

import argparse

from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.base_entities.region import Region
from horey.h_logger import get_logger

from horey.common_utils.actions_manager import ActionsManager
from horey.infrastructure_api.build_api_configuration_policy import BuildAPIConfigurationPolicy
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI


logger = get_logger()
action_manager = ActionsManager()

# pylint: disable= missing-function-docstring


# region ecr_login
def ecr_login_parser():
    description = "Login to ECR repo"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--region", required=True, type=str, help="AWS Region")
    parser.add_argument("--logout", required=False, type=str, help="Logout before login")
    return parser


def ecr_login(arguments) -> None:
    infrastructure_api = InfrastructureAPI()
    aws_api = AWSAPI()
    env_api_config  = EnvironmentAPIConfigurationPolicy()
    env_api_config.region = arguments.region
    env_api  = infrastructure_api.get_environment_api(env_api_config, aws_api)
    build_api = infrastructure_api.get_build_api(BuildAPIConfigurationPolicy(), env_api)

    try:
        if arguments.logout.lower() == "false":
            logout = False
        elif arguments.logout.lower() == "true":
            logout = True
        else:
            raise ValueError(f"logout must be true/false, received '{arguments.logout}'")
    except AttributeError:
        logout = True
    return build_api.login_to_ecr_registry(Region.get_region(arguments.region), logout=logout)



action_manager.register_action("ecr_login", ecr_login_parser, ecr_login)
# endregion


if __name__ == "__main__":
    action_manager.call_action()

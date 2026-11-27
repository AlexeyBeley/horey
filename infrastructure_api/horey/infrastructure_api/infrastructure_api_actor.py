"""
Docker api entry point script.

"""
import sys
from pathlib import Path
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

# region echo
def echo_parser():
    description = "echo"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--str_src", required=False, type=str, help="STR SRC")
    return parser


def echo(arguments) -> None:
    assert InfrastructureAPI()
    print(f"Echo: {arguments.str_src}")


action_manager.register_action("echo", echo_parser, echo)
# endregion


# region trigger_github_action
def trigger_github_action_parser():
    description = "Login to ECR repo"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--github_repo", required=True, type=str, help="Repo")
    parser.add_argument("--github_action", required=True, type=str, help="Action")
    parser.add_argument("--github_branch", required=True, type=str, help="Branch")
    parser.add_argument("--github_api_configuration_file_path", required=True, type=str, help="github_api_configuration_file_path")
    return parser


def trigger_github_action(arguments) -> None:
    infrastructure_api = InfrastructureAPI()
    aws_api = AWSAPI()
    env_api_config  = EnvironmentAPIConfigurationPolicy()
    env_api_config.region = "ca-central-1"
    env_api  = infrastructure_api.get_environment_api(env_api_config, aws_api)
    build_api = infrastructure_api.get_build_api(BuildAPIConfigurationPolicy(), env_api)

    if not build_api.trigger_github_action(Path(arguments.github_api_configuration_file_path), arguments.github_repo, arguments.github_action, arguments.github_branch):
        sys.exit(1)
    

action_manager.register_action("trigger_github_action", trigger_github_action_parser, trigger_github_action)
# endregion


if __name__ == "__main__":
    action_manager.call_action()

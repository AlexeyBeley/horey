"""
Alerts api entry point script.

"""

import argparse
import json

from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger

from horey.common_utils.actions_manager import ActionsManager
from horey.infrastructure_api.alerts_api import AlertsAPI, AlertsAPIConfigurationPolicy
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI


logger = get_logger()
action_manager = ActionsManager()

# pylint: disable= missing-function-docstring


# region trigger_lambda_raw_event
def trigger_lambda_raw_event_parser():
    description = "Trigger alert system lambda with raw event"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--alerts_api_configuration_file_path", required=True, type=str)
    parser.add_argument("--environment_api_configuration_file_path", required=True, type=str)
    parser.add_argument("--payload", required=True, type=str)
    return parser


def trigger_lambda_raw_event(arguments) -> None:
    infrastructure_api = InfrastructureAPI()
    aws_api = AWSAPI()
    env_api_config  = EnvironmentAPIConfigurationPolicy()
    env_api_config.init_from_file(arguments.environment_api_configuration_file_path)
    env_api  = infrastructure_api.get_environment_api(env_api_config, aws_api)
    config = AlertsAPIConfigurationPolicy()
    config.init_from_file(arguments.alerts_api_configuration_file_path)
    alerts_api = AlertsAPI(config, env_api)

    return alerts_api.trigger_lambda_raw_event(json.loads(arguments.payload))



action_manager.register_action("trigger_lambda_raw_event", trigger_lambda_raw_event_parser, trigger_lambda_raw_event)
# endregion


if __name__ == "__main__":
    action_manager.call_action()

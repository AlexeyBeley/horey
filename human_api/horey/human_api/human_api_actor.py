"""
Docker api entry point script.

"""

import argparse

from horey.common_utils.actions_manager import ActionsManager
from horey.human_api.human_api import HumanAPI
from horey.human_api.human_api_configuration_policy import HumanAPIConfigurationPolicy

action_manager = ActionsManager()

# pylint: disable= missing-function-docstring

# region generate_work_plan
def generate_work_plan_parser():
    description = "generate_work_plan"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--human_api_configuration_file_path", required=True, type=str, help="Human API Configuration")
    parser.add_argument("--work_plan_file_path", required=True, type=str, help="Work plan with items to generate")
    return parser


def generate_work_plan(arguments) -> None:
    configuration = HumanAPIConfigurationPolicy()
    configuration.configuration_file_full_path = arguments.human_api_configuration_file_path
    configuration.init_from_file()
    HumanAPI(configuration=configuration).generate_work_plan(arguments.work_plan_file_path)


action_manager.register_action("generate_work_plan", generate_work_plan_parser, generate_work_plan)
# endregion


# region daily_routine
def daily_routine_parser():
    description = "daily_routine"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--human_api_configuration_file_path", required=True, type=str, help="Human API Configuration")
    return parser


def daily_routine(arguments) -> None:
    configuration = HumanAPIConfigurationPolicy()
    configuration.configuration_file_full_path = arguments.human_api_configuration_file_path
    configuration.init_from_file()
    HumanAPI(configuration=configuration).daily_routine()


action_manager.register_action("daily_routine", daily_routine_parser, daily_routine)
# endregion


# region retrospective
def retrospective_parser():
    description = "retrospective"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--human_api_configuration_file_path", required=True, type=str, help="Human API Configuration")
    return parser


def retrospective(arguments) -> None:
    configuration = HumanAPIConfigurationPolicy()
    configuration.configuration_file_full_path = arguments.human_api_configuration_file_path
    configuration.init_from_file()
    HumanAPI(configuration=configuration).retrospective()


action_manager.register_action("retrospective", retrospective_parser, retrospective)
# endregion


if __name__ == "__main__":
    action_manager.call_action()

"""
Alert system script' entry points

"""
# pylint: disable=missing-function-docstring

import argparse
import json

from horey.common_utils.actions_manager import ActionsManager
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy
from horey.alert_system.alert_system import AlertSystem

action_manager = ActionsManager()


# region send_message_to_sns
def send_message_to_sns_parser():
    description = "Send message to sns topic"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--subject", required=True, type=str)
    parser.add_argument("--message_file_path", required=True, type=str)
    parser.add_argument("--alert_system_configuration_file_path", required=True, type=str)
    return parser


def send_message_to_sns(arguments, _) -> None:
    configuration = AlertSystemConfigurationPolicy()
    configuration.configuration_file_full_path = arguments.alert_system_configuration_file_path
    configuration.init_from_file()
    alert_system = AlertSystem(configuration)
    with open(arguments.message_file_path, encoding="utf-8") as file_handler:
        message = json.load(file_handler)

    alert_system.send_message_to_sns(message)


action_manager.register_action("send_message_to_sns", send_message_to_sns_parser, send_message_to_sns)
# endregion


if __name__ == "__main__":
    action_manager.call_action(pass_unknown_args=True)

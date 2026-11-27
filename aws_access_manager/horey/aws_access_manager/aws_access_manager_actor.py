"""
Venv entrypoints

"""

import argparse

import logging

logger = logging.Logger(__name__)

from horey.aws_access_manager.aws_access_manager import AWSAccessManager
from horey.aws_access_manager.aws_access_manager_configuration_policy import AWSAccessManagerConfigurationPolicy
from horey.common_utils.actions_manager import ActionsManager

# AWSAccount.set_aws_account(ignore_me.acc_default)
action_manager = ActionsManager()


# region user_access_report
def user_access_report_parser():
    """
    Standard.

    :return:
    """

    description = "user_access_report AWS account"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--target", required=True, type=str, help="Object type to user_access_report"
    )
    parser.add_argument(
        "--configuration_file_full_path",
        required=True,
        type=str,
        help="Configuration file full path",
    )

    return parser


def user_access_report(arguments) -> None:
    """
    Run user_access_reports.

    :param arguments:
    :return:
    """

    configuration = AWSAccessManagerConfigurationPolicy()
    configuration.configuration_file_full_path = arguments.configuration_file_full_path
    configuration.init_from_file()

    aws_access_manager = AWSAccessManager(configuration)

    aws_access_manager.generate_users_access_report()


action_manager.register_action("user_access_report", user_access_report_parser, user_access_report)
# endregion



if __name__ == "__main__":
    action_manager.call_action()

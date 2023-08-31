"""
Venv entrypoints

"""

import argparse

import logging

logger = logging.Logger(__name__)

from horey.aws_cleaner.aws_cleaner import AWSCleaner
from horey.aws_cleaner.aws_cleaner_configuration_policy import AWSCleanerConfigurationPolicy
from horey.common_utils.actions_manager import ActionsManager

# AWSAccount.set_aws_account(ignore_me.acc_default)
action_manager = ActionsManager()


# region cleanup
def cleanup_parser():
    """
    Standard.

    :return:
    """

    description = "Cleanup AWS account"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--target", required=True, type=str, help="Object type to cleanup"
    )
    parser.add_argument(
        "--configuration_file_full_path",
        required=True,
        type=str,
        help="Configuration file full path",
    )

    return parser


def cleanup(arguments) -> None:
    """
    Run cleanups.

    :param arguments:
    :return:
    """

    configuration = AWSCleanerConfigurationPolicy()
    configuration.configuration_file_full_path = arguments.configuration_file_full_path
    configuration.init_from_file()

    aws_cleaner = AWSCleaner(configuration)

    aws_cleaner.cleanup_report_ebs_volumes()


action_manager.register_action("cleanup", cleanup_parser, cleanup)
# endregion



if __name__ == "__main__":
    action_manager.call_action()

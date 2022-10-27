"""
The entry point script to run authorization.

"""

import argparse
import os.path

from horey.jenkins_manager.authorization_job.authorization_applicator import AuthorizationApplicator
from horey.jenkins_manager.authorization_job.authorization_job import AuthorizationJob
from horey.jenkins_manager.authorization_job.authorization_job_configuration_policy import AuthorizationJobConfigurationPolicy

from horey.common_utils.actions_manager import ActionsManager


action_manager = ActionsManager()


# region authorize
def authorize_parser():
    """
    Authorize parser.

    @return:
    """

    description = "Authorize user identity to run specific job."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--request_file", type=str)
    return parser


def authorize(arguments) -> None:
    """
    Authorize request.

    @param arguments:
    @return:
    """

    configuration = AuthorizationJobConfigurationPolicy()

    with open(arguments.request_file, encoding="utf-8") as file_handler:
        request = AuthorizationApplicator.Request(file_handler.read())

    configuration.authorization_map_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                             "authorization_map.json")

    AuthorizationJob(configuration).authorize(request)


action_manager.register_action("authorize", authorize_parser, authorize)
# endregion

if __name__ == "__main__":
    action_manager.call_action()

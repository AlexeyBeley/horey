"""
Standard Horey Actor: Script entrypoint to a python package.

"""

import argparse
import json

from horey.jenkins_api.jenkins_api import JenkinsAPI
from horey.jenkins_api.jenkins_api_configuration_policy import (
    JenkinsAPIConfigurationPolicy,
)
from horey.jenkins_api.jenkins_job import JenkinsJob
from horey.common_utils.actions_manager import ActionsManager

action_manager = ActionsManager()


# pylint: disable= missing-function-docstring


# region run_job
def run_job_parser():
    description = "Run single job"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--job_name", required=True, type=str, help="job name"
    )
    parser.add_argument(
        "--parameters", required=True, type=str, help="parameters"
    )
    parser.add_argument(
        "--jenkins_api_configuration_file", required=True, type=str, help="jenkins_api_configuration_file"
    )

    return parser


def run_job(arguments) -> None:
    configuration = JenkinsAPIConfigurationPolicy()
    configuration.init_from_file()

    manager = JenkinsAPI(configuration)
    with open(arguments.build_info_file, encoding="utf-8") as file_handler:
        build_info = json.load(file_handler)
    job = JenkinsJob(build_info["job_name"], build_info.get("parameters"))
    manager.execute_jobs([job])


action_manager.register_action("run_job", run_job_parser, run_job)
# endregion

if __name__ == "__main__":
    action_manager.call_action()

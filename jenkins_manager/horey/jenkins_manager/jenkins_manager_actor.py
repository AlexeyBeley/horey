import pdb
import argparse
import json

from jenkins_manager import JenkinsManager
from jenkins_configuration_policy import JenkinsConfigurationPolicy
from jenkins_job import JenkinsJob

from horey.common_utils.actions_manager import ActionsManager

action_manager = ActionsManager()


# region run_job
def run_job_parser():
    description = "Run single job"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--build_info_file", required=True, type=str, help="build_info_file")

    return parser


def run_job(arguments, configs_dict) -> None:
    configuration = JenkinsConfigurationPolicy()
    configuration.init_from_dictionary(configs_dict)
    configuration.init_from_file()

    manager = JenkinsManager(configuration)
    with open(arguments.build_info_file) as file_handler:
        build_info = json.load(file_handler)
    job = JenkinsJob(build_info["job_name"], build_info.get("parameters"))
    manager.execute_jobs([job])


action_manager.register_action("run_job", run_job_parser, run_job)
# endregion


# region backup_jobs
def backup_jobs_parser():
    description = "Backup all jobs"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--backups_dir", required=True, type=str, help="backups_dir")
    parser.add_argument("--jobs_names", required=True, type=str, help="job_names")

    return parser


def backup_jobs(arguments, configs_dict) -> None:
    configuration = JenkinsConfigurationPolicy()
    configuration.init_from_dictionary(configs_dict)
    configuration.init_from_file()

    manager = JenkinsManager(configuration)
    manager.backup_jobs(arguments.backups_dir, jobs_names=arguments.jobs_names.split(","))


action_manager.register_action("backup_jobs", backup_jobs_parser, backup_jobs)
# endregion


# region create_jobs
def create_jobs_parser():
    description = "Create jobs"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--backups_dir", required=True, type=str, help="backups_dir")
    parser.add_argument("--jobs_names", required=True, type=str, help="job_names")
    parser.add_argument("--overwrite", required=True, type=str, help="overwrite existing")

    return parser


def create_jobs(arguments, configs_dict) -> None:
    configuration = JenkinsConfigurationPolicy()
    configuration.init_from_dictionary(configs_dict)
    configuration.init_from_file()

    manager = JenkinsManager(configuration)
    manager.create_jobs(arguments.backups_dir, jobs_names=arguments.jobs_names.split(","), overwrite=arguments.overwrite.lower() == "true")


action_manager.register_action("create_jobs", create_jobs_parser, create_jobs)
# endregion

if __name__ == "__main__":
    action_manager.call_action(pass_unknown_args=True)

import pdb
import argparse
import json

from horey.jenkins_manager.jenkins_manager import JenkinsManager, JenkinsConfigurationPolicy, JenkinsJob
from horey.jenkins_manager.jenkins_configuration_policy import JenkinsConfigurationPolicy
from horey.jenkins_manager.jenkins_job import JenkinsJob
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


# region run_job
def run_jobs_parser():
    description = "Run list of jobs"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--cached_jobs_file_path", required=True, type=str, help="Json list of cached jobs")

    return parser


def run_jobs(arguments, configs_dict) -> None:
    configuration = JenkinsConfigurationPolicy()
    configuration.init_from_dictionary(configs_dict)
    configuration.init_from_file()
    manager = JenkinsManager(configuration)

    with open(arguments.cached_jobs_file_path) as file_handler:
        lst_dict_jobs = json.load(file_handler)
    lst_jobs = [JenkinsJob(None, None, cache_dict=dict_job) for dict_job in lst_dict_jobs]
    print(manager.execute_jobs(lst_jobs))


action_manager.register_action("run_jobs", run_jobs_parser, run_jobs)
# endregion

# region backup_jobs
def backup_jobs_parser():
    description = "Backup all jobs"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--backups_dir", required=True, type=str, help="backups_dir")
    parser.add_argument("--jobs_names", required=False, type=str, help="job_names", default="")

    return parser


def backup_jobs(arguments, configs_dict) -> None:
    configuration = JenkinsConfigurationPolicy()
    configuration.init_from_dictionary(configs_dict)
    configuration.init_from_file()

    manager = JenkinsManager(configuration)
    jobs_names = arguments.jobs_names.split(",") if arguments.jobs_names != "" else None
    manager.backup_jobs(arguments.backups_dir, jobs_names=jobs_names)


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


# region cleanup
def cleanup_parser():
    description = "Cleanup report"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--output_file", required=True, type=str, help="Output file")

    return parser


def cleanup(arguments, configs_dict) -> None:
    configuration = JenkinsConfigurationPolicy()
    configuration.init_from_dictionary(configs_dict)
    configuration.init_from_file()

    manager = JenkinsManager(configuration)
    manager.cleanup(arguments.output_file)


action_manager.register_action("cleanup", cleanup_parser, cleanup)
# endregion


# region disable_jobs
def disable_jobs_parser():
    usage_example = "jenkins_manager_actor.py --action disable_jobs --input_file ${ROOT_DIR}/jenkins_disable.txt" \
                    " --configuration_file_full_path ${ROOT_DIR}/jenkins_configuration_file.py"
    description = "Disable jobs"
    parser = argparse.ArgumentParser(description=description, usage=usage_example)
    parser.add_argument("--input_file", required=True, type=str, help="Input file")

    return parser


def disable_jobs(arguments, configs_dict) -> None:
    configuration = JenkinsConfigurationPolicy()
    configuration.init_from_dictionary(configs_dict)
    configuration.init_from_file()

    manager = JenkinsManager(configuration)
    manager.disable_jobs_from_file(arguments.input_file)


action_manager.register_action("disable_jobs", disable_jobs_parser, disable_jobs)
# endregion


# region delete_jobs
def delete_jobs_parser():
    usage_example = "jenkins_manager_actor.py --action delete_jobs --input_file ${ROOT_DIR}/jenkins_disable.txt" \
                    " --configuration_file_full_path ${ROOT_DIR}/jenkins_configuration_file.py"
    description = "Delete jobs"
    parser = argparse.ArgumentParser(description=description, usage=usage_example)
    parser.add_argument("--input_file", required=True, type=str, help="Input file")

    return parser


def delete_jobs(arguments, configs_dict) -> None:
    configuration = JenkinsConfigurationPolicy()
    configuration.init_from_dictionary(configs_dict)
    configuration.init_from_file()

    manager = JenkinsManager(configuration)
    manager.delete_jobs_from_file(arguments.input_file)


action_manager.register_action("delete_jobs", delete_jobs_parser, delete_jobs)
# endregion


if __name__ == "__main__":
    action_manager.call_action(pass_unknown_args=True)

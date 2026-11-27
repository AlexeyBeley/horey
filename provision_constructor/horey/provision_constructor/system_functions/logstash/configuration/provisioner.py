import os
import pdb
import sys
from system_function_common import SystemFunctionCommon


class Provisioner(SystemFunctionCommon):
    def __init__(self):
        super().__init__()

    @staticmethod
    def add_logstash_configuration_files(_):
        Provisioner.add_pipelines_yml_file()
        Provisioner.add_pipeline_conf_files()

    @staticmethod
    def add_pipelines_yml_file():
        pipelines_file = SystemFunctionCommon.current_subpath("pipelines.yml")
        return SystemFunctionCommon.provision_file(pipelines_file, "/etc/logstash")

    @staticmethod
    def add_pipeline_conf_files():
        pipeline_files_dir = SystemFunctionCommon.current_subpath("pipelines")
        for file_name in os.listdir(pipeline_files_dir):
            SystemFunctionCommon.provision_file(
                os.path.join(pipeline_files_dir, file_name), "/etc/logstash/conf.d/"
            )

    @staticmethod
    def check_configuration_files(_):
        Provisioner.check_pipelines_yml_file()
        Provisioner.check_pipeline_conf_files()

    @staticmethod
    def check_pipelines_yml_file():
        pipelines_file = SystemFunctionCommon.current_subpath("pipelines.yml")
        if not SystemFunctionCommon.compare_files(
            pipelines_file, "/etc/logstash/pipelines.yml"
        ):
            sys.exit(1)

    @staticmethod
    def check_pipeline_conf_files():
        pipeline_files_dir = SystemFunctionCommon.current_subpath("pipelines")
        for file_name in os.listdir(pipeline_files_dir):
            if not os.path.exists(os.path.join("/etc/logstash/conf.d/", file_name)):
                sys.exit(1)


Provisioner.ACTION_MANAGER.register_action(
    "add_logstash_configuration_files",
    Provisioner.empty_parser,
    Provisioner.add_logstash_configuration_files,
)


Provisioner.ACTION_MANAGER.register_action(
    "check_configuration_files",
    Provisioner.empty_parser,
    Provisioner.check_configuration_files,
)

if __name__ == "__main__":
    Provisioner.ACTION_MANAGER.call_action()

import os
import pdb
import argparse
import sys

from system_function_common import SystemFunctionCommon


class LogstashRemoteProvisioner(SystemFunctionCommon):
    def __init__(self):
        super().__init__()

    @staticmethod
    def add_logstash_configuration_files_parser():
        parser = argparse.ArgumentParser()
        return parser

    @staticmethod
    def add_logstash_configuration_files(_):
        pdb.set_trace()

        changed = LogstashRemoteProvisioner.add_pipelines_yml_file()
        return LogstashRemoteProvisioner.add_pipeline_conf_files() or changed

    @staticmethod
    def add_pipelines_yml_file():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pipelines_file = os.path.join(current_dir, "pipelines.yml")
        return SystemFunctionCommon.provision_file(pipelines_file, "/etc/logstash")

    @staticmethod
    def add_pipeline_conf_files():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pipeline_files = os.path.join(current_dir, "pipelines")
        changed = False
        for file_name in os.listdir(pipeline_files):
            changed = SystemFunctionCommon.provision_file(os.path.join(pipeline_files, file_name), "/etc/logstash/conf.d/") or changed


LogstashRemoteProvisioner.ACTION_MANAGER.register_action("add_logstash_configuration_files",
                                                      LogstashRemoteProvisioner.add_logstash_configuration_files_parser,
                                                      LogstashRemoteProvisioner.add_logstash_configuration_files)


if __name__ == "__main__":
    if LogstashRemoteProvisioner.ACTION_MANAGER.call_action():
        sys.exit(10)

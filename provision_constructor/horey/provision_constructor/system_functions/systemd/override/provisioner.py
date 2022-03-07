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


Provisioner.ACTION_MANAGER.register_action("add_logstash_configuration_files",
                                           Provisioner.empty_parser,
                                           Provisioner.add_logstash_configuration_files)


if __name__ == "__main__":
    Provisioner.ACTION_MANAGER.call_action()

import pdb
import argparse

from system_function_common import SystemFunctionCommon


class LogstashRemoteProvisioner(SystemFunctionCommon):
    def __init__(self):
        super().__init__()

    def add_logstash_configuration_files_parser(self):
        parser = argparse.ArgumentParser()
        return parser

    def add_logstash_configuration_files(self):
        pdb.set_trace()


LogstashRemoteProvisioner.ACTION_MANAGER.register_action("add_logstash_configuration_files",
                                                      LogstashProvisioner.add_logstash_configuration_files_parser,
                                                      LogstashProvisioner.add_logstash_configuration_files)


if __name__ == "__main__":
    LogstashRemoteProvisioner.ACTION_MANAGER.call_action()

import pdb
import argparse

from system_function_common import SystemFunctionCommon


class LogstashRemoteProvisioner(SystemFunctionCommon):
    def __init__(self):
        super().__init__()

    @staticmethod
    def add_logstash_configuration_files_parser():
        parser = argparse.ArgumentParser()
        return parser

    @staticmethod
    def add_logstash_configuration_files():
        pdb.set_trace()


LogstashRemoteProvisioner.ACTION_MANAGER.register_action("add_logstash_configuration_files",
                                                      LogstashRemoteProvisioner.add_logstash_configuration_files_parser,
                                                      LogstashRemoteProvisioner.add_logstash_configuration_files)


if __name__ == "__main__":
    LogstashRemoteProvisioner.ACTION_MANAGER.call_action()

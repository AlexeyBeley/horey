"""
Logstash service provisioner.

"""

import os
from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """
    Main class.

    """

    def __init__(self, deployment_dir, force, upgrade):
        super().__init__(os.path.dirname(os.path.abspath(__file__)), force, upgrade)
        self.deployment_dir = deployment_dir

    def _provision(self):
        """
        Provision all components.

        :return:
        """

        src_url = "https://artifacts.elastic.co/GPG-KEY-elasticsearch"
        dst_file_path = "/usr/share/keyrings/elastic-keyring.gpg"
        SystemFunctionFactory.REGISTERED_FUNCTIONS["gpg_key"](self.deployment_dir, self.force,
                                                              self.upgrade, src_url=src_url,
                                                              dst_file_path=dst_file_path).provision()

    def test_provisioned(self):
        """
        Test the sys_function was provisioned.

        :return:
        """

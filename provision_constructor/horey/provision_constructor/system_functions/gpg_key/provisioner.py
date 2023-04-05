"""
Provision GPG key.

"""

import os
from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """
    Main provisioner.

    """

    # pylint: disable= too-many-arguments
    def __init__(self, deployment_dir, force, upgrade, src_url=None, dst_file_path=None):
        super().__init__(os.path.dirname(os.path.abspath(__file__)), force, upgrade)
        self.deployment_dir = deployment_dir
        self.src_url = src_url
        self.dst_file_path = dst_file_path

    def _provision(self):
        """
        Provision GPG key.

        :return:
        """

        self.run_bash(f"wget -qO - {self.src_url} | sudo gpg --dearmor -o {self.dst_file_path}")

    def test_provisioned(self):
        """
        Test the sys_function was provisioned.

        :return:
        """

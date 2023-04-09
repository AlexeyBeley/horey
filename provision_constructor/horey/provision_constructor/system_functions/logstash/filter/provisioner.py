"""
Logstash filter provisioner.

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
        breakpoint()

    def test_provisioned(self):
        """
        Test the sys_function was provisioned.

        :return:
        """
        return self.apt_check_installed("logstash")

import os.path
from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.h_logger import get_logger

logger = get_logger()


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    def __init__(self, deployment_dir, force, upgrade):
        super().__init__(os.path.dirname(os.path.abspath(__file__)), force, upgrade)
        self.deployment_dir = deployment_dir

    def test_provisioned(self):
        breakpoint()
        self.init_apt_packages()
        return self.apt_check_installed("openjdk-11-jdk")

    def _provision(self):
        breakpoint()
        if not self.apt_check_repository_exists("openjdk-r"):
            self.apt_add_repository("ppa:openjdk-r/ppa")

        return self.apt_install("openjdk-11-jdk")

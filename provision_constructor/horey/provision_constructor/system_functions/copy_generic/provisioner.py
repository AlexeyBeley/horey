import os.path
import pdb
from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import SystemFunctionCommon
from horey.h_logger import get_logger

logger = get_logger()


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    def __init__(self, deployment_dir, src=None, dst=None):
        super().__init__(os.path.dirname(os.path.abspath(__file__)))
        self.deployment_dir = deployment_dir
        self.package_name = package_name
        self.horey_repo_path = horey_repo_path

    def provision(self, force=False):
        if not force:
            if self.test_provisioned():
                return

        self._provision()

        self.test_provisioned()

    def test_provisioned(self):
        return self.check_pip_installed(f"horey.{self.package_name}")

    def _provision(self):
        self.run_bash(f"cd {self.horey_repo_path} && make recursive_install_from_source-{self.package_name}")

"""
Provision horey packages from source.

"""

import os.path
from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import SystemFunctionCommon
from horey.h_logger import get_logger

logger = get_logger()


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """
    Provisioner class.

    """

    def __init__(self, deployment_dir, horey_repo_path=None, package_name=None, package_names=None):
        super().__init__(os.path.dirname(os.path.abspath(__file__)))
        self.deployment_dir = deployment_dir

        if package_name is not None:
            self.package_names = [package_name]
        elif package_names is not None:
            self.package_names = package_names
        else:
            raise ValueError("package_name/package_names not set")

        self.horey_repo_path = horey_repo_path

    def provision(self, force=False):
        """
        Provision all packages.

        @param force:
        @return:
        """

        for package_name in self.package_names:
            if not force and self.test_provisioned(package_name):
                logger.info(f"Skipping horey package installation: {package_name}")
                continue

            self._provision(package_name)

            if not self.test_provisioned(package_name):
                raise RuntimeError(f"Was not able to provision {package_name}")
            logger.info(f"Successfully installed horey package: {package_name}")

    def test_provisioned(self, package_name):
        """
        Test single package provisioned.

        @param package_name:
        @return:
        """

        return self.check_pip_installed(f"horey.{package_name}")

    def _provision(self, package_name):
        """
        Provision single packages.

        @param package_name:
        @return:
        """

        self.run_bash(f"cd {self.horey_repo_path} && make recursive_install_from_source-{package_name}")

"""
Provision horey packages from source.

"""

import os.path
from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.h_logger import get_logger

logger = get_logger()


# pylint: disable= abstract-method
@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """
    Provisioner class.

    """

    # pylint: disable= too-many-arguments
    def __init__(
        self,
        deployment_dir,
        force, upgrade,
        horey_repo_path=None,
        package_name=None,
        package_names=None,
        venv_path=None,
    ):
        super().__init__(os.path.dirname(os.path.abspath(__file__)), force, upgrade)
        self.deployment_dir = deployment_dir

        if package_name is not None:
            self.package_names = [package_name]
        elif package_names is not None:
            self.package_names = package_names
        else:
            raise ValueError("package_name/package_names not set")

        self.horey_repo_path = horey_repo_path
        self.venv_path = venv_path

    def test_provisioned(self):
        """
        Test all packages are provisioned.

        @return:
        """
        return all(self.check_pip_installed(f"horey.{package_name.replace('_', '-')}")
                   for package_name in self.package_names)

    def _provision(self):
        """
        Provision single packages.

        @return:
        """

        for package_name in self.package_names:
            command = f"cd {self.horey_repo_path} && make recursive_install_from_source-{package_name}"

            if self.venv_path is not None:
                command = self.activate + " && " + command

            self.run_bash(command)
            self.init_pip_packages()

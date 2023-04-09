"""
APT packages provisioning.

"""

import os.path
from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.h_logger import get_logger

logger = get_logger()


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """
    Main provisioner.

    """

    # pylint: disable= too-many-arguments
    def __init__(self, deployment_dir, force, upgrade, package_name=None, package_names=None):
        super().__init__(os.path.dirname(os.path.abspath(__file__)), force, upgrade)
        self.deployment_dir = deployment_dir

        if package_name is not None:
            self.package_names = [package_name]
        elif package_names is not None:
            self.package_names = package_names
        else:
            raise ValueError("package_name/package_names not set")

    def test_provisioned(self):
        """
        Test all packages provisioned.

        @return:
        """

        self.init_apt_packages()
        return all(self.apt_check_installed(package_name)
                   for package_name in self.package_names)

    def _provision(self):
        """
        Provision packages.

        @return:
        """

        for package_name in self.package_names:
            self.apt_install(package_name)

"""
Provision GPG key.

"""

from horey.common_utils.remoter import Remoter
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
    def __init__(self, deployment_dir, force, upgrade, src_url=None, dst_file_path=None, **kwargs):
        super().__init__(deployment_dir, force, upgrade, **kwargs)
        self.src_url = src_url
        self.dst_file_path = dst_file_path

    def _provision(self):
        """
        Provision GPG key.

        :return:
        """

        self.run_bash(f"wget -qO - {self.src_url} | sudo gpg --batch --yes --dearmor -o {self.dst_file_path}")
        self.update_packages()

    def test_provisioned(self):
        """
        Test the sys_function was provisioned.

        :return:
        """

        self.check_files_exist([self.dst_file_path])

    def provision_remote(self, remoter: Remoter):
        """
        Provision GPG key.

        :return:
        """

        #old:  remoter.execute(f"wget -qO - {self.src_url} | sudo gpg --batch --yes --dearmor -o {self.dst_file_path}")

        # curl is installed by default

        remoter.execute(f"curl -fsSL {self.src_url} | sudo gpg --batch --yes --dearmor -o {self.dst_file_path}")
        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, self.force, self.upgrade, action="update_packages").provision_remote(remoter)

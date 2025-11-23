"""
Copy generic file or folder

"""

import os
from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.h_logger import get_logger

logger = get_logger()


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """
    Main class

    """

    # pylint: disable= too-many-arguments
    def __init__(self, deployment_dir, force, upgrade, src=None, dst=None, sudo=False, owner=None):
        super().__init__(os.path.dirname(os.path.abspath(__file__)), force, upgrade)
        self.deployment_dir = deployment_dir
        if os.path.isfile(src):
            if os.path.isdir(dst):
                dst = os.path.join(dst, os.path.basename(src))
        else:
            raise NotImplementedError(f"Src must be a file for now: '{src}'")

        self.src = src
        self.dst = dst
        self.sudo = sudo
        self.owner = owner

    def test_provisioned(self):
        """
        Test copy generic file/dir provisioned.

        @return:
        """

        return self.check_file_provisioned(self.src, self.dst)

    def _provision(self):
        """
        Provision the copy generic file/dir

        @return:
        """

        self.provision_file(self.src, self.dst, sudo=self.sudo, owner=self.owner)

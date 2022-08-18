"""
Copy generic file or folder

"""

import os
from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import SystemFunctionCommon
from horey.h_logger import get_logger

logger = get_logger()


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """
    Main class

    """

    def __init__(self, deployment_dir, src=None, dst=None):
        super().__init__(os.path.dirname(os.path.abspath(__file__)))
        self.deployment_dir = deployment_dir
        if not os.path.isfile(src) or not os.path.isfile(dst):
            raise NotImplementedError("Src and dst must be files for now.")
        self.src = src
        self.dst = dst

    def provision(self, force=False):
        """
        Provision the copy generic file/dir

        @param force:
        @return:
        """

        if not force and self.test_provisioned():
            logger.info(f"Skipping copy generic provisioning: from {self.src} to {self.dst}")
            return False

        self._provision()

        if not self.test_provisioned():
            raise RuntimeError(f"Failed to copy generic: from {self.src} to {self.dst}")

        logger.info(f"Successfully copied generic: from {self.src} to {self.dst}")

        return True

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

        self.provision_file(self.src, self.dst)

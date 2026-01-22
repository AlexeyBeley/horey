"""
Copy generic file or folder

"""

from horey.common_utils.remoter import Remoter
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
    def __init__(self, deployment_dir, force, upgrade, **kwargs):
        super().__init__(deployment_dir, force, upgrade, **kwargs)
        self.src = kwargs["src"]
        self.dst = kwargs["dst"]
        self.sudo = kwargs["sudo"]

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

        self.provision_file(self.src, self.dst, sudo=self.sudo)

    def provision_remote(self, remoter: Remoter):
        """
        Provision remotely

        :param remoter:
        :return:
        """

        remoter.put_file(self.src, self.dst, sudo=True)

        return True

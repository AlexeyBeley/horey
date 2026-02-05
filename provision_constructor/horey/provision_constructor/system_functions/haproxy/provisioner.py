"""
Provision ntp service.

"""

import os.path
import platform
import json

from horey.common_utils.remoter import Remoter
from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.common_utils.bash_executor import BashExecutor
from horey.h_logger import get_logger

logger = get_logger()
BashExecutor.set_logger(logger, override=False)


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """
    Provision haproxy service.
    Remove all others.

    """

    def __init__(self, deployment_dir, force, upgrade, **kwargs):
        super().__init__(deployment_dir, force, upgrade, **kwargs)

    def provision_remote(self, remoter: Remoter):
        """
        Provision ntp.

        @return:
        """

        self.remoter = remoter
        self.remoter.execute("ls")

        if self.action == "check_backends":
            return self.check_backends_remote()
        raise NotImplementedError(self.action)

    def check_backends_remote(self):
        """
        Check backends have live servers

        :return:
        """
        breakpoint()
        ret = self.remoter.execute("echo \"show backend\" | sudo -u haproxy socat stdio unix-connect:/var/run/haproxy/admin.sock")
        ret = self.remoter.execute("echo \"show servers state {backend_name}\" | sudo -u haproxy socat stdio unix-connect:/var/run/haproxy/admin.sock")

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
        enable server <backend>/<server>: Enables a specific server in a backend, bringing it back into the rotation for health checks and traffic.
        disable server <backend>/<server>: Disables a specific server, useful for maintenance without stopping HAProxy.
        set server <backend>/<server> state <state>: Sets the operational state of a server (e.g., ready, maint, drain etc.).
        get weight <backend>/<server>: Retrieves the current weight of a server.
        set weight <backend>/<server> <weight>: Dynamically changes a server's weight.


        :return:
        """

        ret = self.remoter.execute("echo \"show backend\" | sudo -u haproxy socat stdio unix-connect:/var/run/haproxy/admin.sock")
        backend_names = [line.strip("\n") for line in ret[0] if not line.startswith("#") and line.strip("\n")]
        for backend_name in backend_names:
            ret = self.remoter.execute(f"echo \"show servers state {backend_name}\" | sudo -u haproxy socat stdio unix-connect:/var/run/haproxy/admin.sock")
            backend_lines = [line.strip("\n") for line in ret[0] if not line.startswith("#") and line.strip("\n")]
            for backend_line in backend_lines:
                breakpoint()
                lst_line = backend_line.split(" ")
                if lst_line[5] != "2":
                    raise self.FailedCheckError(f"Backend {backend_name} server {lst_line} is not UP")

        return True
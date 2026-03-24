"""
Provision ntp service.

"""

import threading
from pathlib import Path

from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.common_utils.bash_executor import BashExecutor
from horey.common_utils.remoter import Remoter
from horey.h_logger import get_logger

logger = get_logger()
BashExecutor.set_logger(logger, override=False)


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """
    Provision service.

    """
    LOCK = threading.Lock()

    def __init__(self, deployment_dir, force, upgrade, **kwargs):
        """

        :param deployment_dir:
        :param force:
        :param upgrade:
        :param kwargs:
        """
        super().__init__(deployment_dir, force, upgrade, **kwargs)

    def provision_remote(self, remoter: Remoter):
        """
        Provision remotely

        :param remoter:
        :return:
        """

        self.remoter = remoter
        if self.action == "install":
            return self.install_remote()
        raise NotImplemented(self.action)

    def install_remote(self):
        """
        Isntall vrrp remotely

        :return:
        """

        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, self.force, self.upgrade,
                                                                          package_names=["keepalived",
                                                                                         ]).provision_remote(
            self.remoter)

        ret = self.remoter.execute("ls /etc/keepalived")
        config_file_path = self.generate_config_file()
        breakpoint()

    def generate_config_file(self) -> Path:
        """
        Generate file

        :return:
        """

        state = self.kwargs.get("state")
        if not state:
            raise ValueError("state is required")
        priority = 110 if state == "MASTER" else 100

        lines = ["vrrp_instance VI_1 {",
        f"state {state}",
        "interface eth0",
        "virtual_router_id 51",
        f"priority {priority}",
        "advert_int 1",
        "authentication {",
        "auth_type PASS",
        "auth_pass somepass",
        "}",
        "virtual_ipaddress {",
        f"{self.kwargs.get('virtual_ipaddress')}/24",
        "}",
        "}"]

        self.deployment_dir.mkdir(exist_ok=True)
        file_path = self.deployment_dir / "keepalived.conf"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))

        return file_path

"""
Manage systemd

"""
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
    System function Provision manager
    """

    def provision_remote(self, remoter: Remoter):
        """
        Provision remotely
        Preparing to unpack influxdb_1.12.2-1_amd64.deb ...

        :param remoter:
        :return:
        """

        self.remoter = remoter

        match self.action:
            case "restart_service":
                return self.restart_service_remote()
            case "provision_service":
                return self.provision_service_remote()
            case _:
                raise NotImplementedError(f"{self.action}")

    def restart_service_remote(self):
        """
        Provision remotely

        :return:
        """

        service_name = self.kwargs.get("service_name")
        if not service_name:
            raise ValueError("service_name was not set")
        self.remoter.execute(f"sudo systemctl restart {service_name}")
        self.check_systemd_service_status_remote(service_name, 60)
        return True


    def provision_service_remote(self):
        """
        Provision service.

        @return:
        """

        service_name = self.kwargs.get("service_name")
        if not service_name:
            raise ValueError("service_name was not set")
        unit_file_path = self.kwargs.get("unit_file_path")
        if not unit_file_path:
            raise ValueError("unit_file_path was not set")

        self.remoter.put_file(unit_file_path, Path("/etc/systemd/system/") / unit_file_path.name, sudo=True)

        self.remoter.execute("sudo systemctl daemon-reload")
        self.remoter.execute(f"sudo systemctl enable {service_name}")
        self.restart_service_remote()

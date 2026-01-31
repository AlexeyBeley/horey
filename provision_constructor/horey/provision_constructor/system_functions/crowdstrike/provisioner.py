"""
Provision ntp service.

"""
import json
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

    def _provision(self):
        """
        Not implemented

        :return:
        """
        raise NotImplementedError("Not implemented")

    def test_provisioned(self):
        self.init_apt_packages()
        return (
            (not self.apt_check_installed("sntp*"))
            and (not self.apt_check_installed("chrony*"))
            and self.check_file_provisioned(
                "./timesyncd.conf", "/etc/systemd/timesyncd.conf"
            )
            and self.check_systemd_service_status(
                service_name="systemd-timesyncd", min_uptime=20
            )
        )

    def provision_remote(self, remoter: Remoter):
        """
        Provision remotely
        Preparing to unpack influxdb_1.12.2-1_amd64.deb ...

        :param remoter:
        :return:
        """

        self.remoter = remoter
        remoter.execute("pwd")

        match self.action:
            case "install_falcon_sensor":
                return self.provision_remote_install_falcon_sensor()
            case _:
                raise NotImplementedError(f"{self.action}")

    def provision_remote_install_falcon_sensor(self):
        """
        Provision remotely

        :return:
        """

        if self.storage_service is None:
            raise RuntimeError("storage_service was not set")

        if (falcon_sensor_cid:=self.kwargs.get("falcon_sensor_cid")) is None:
            raise RuntimeError("falcon_sensor_cid was not set")

        arch = self.init_cpu_data_remote()
        options = []
        if arch == "x86_64":
            for file_path in self.storage_service.list():
                if "falcon-sensor" not in file_path:
                    continue
                if "amd64"  not in file_path:
                    continue
                if not file_path.endswith(".deb"):
                    continue
                options.append(file_path)
        else:
            raise NotImplementedError(f"CPU arch '{arch}' is not supported")

        if len(options) != 1:
            raise RuntimeError(f"Found {len(options)} options:\n{options}")


        self.deployment_dir.mkdir(exist_ok=True)
        local_file_path = Path(self.deployment_dir / options[0].split("/")[-1])
        self.storage_service.download(options[0], local_file_path)

        remote_path = self.remoter.get_deployment_dir() / local_file_path.name
        self.remoter.execute(f"mkdir -p {self.remoter.get_deployment_dir()}")
        self.remoter.put_file(local_file_path, remote_path)
        self.remoter.execute(f"sudo dpkg -i {remote_path}",
                                   self.grep_validator("Unpacking falcon-sensor"),
                                   self.grep_validator("Setting up falcon-sensor"),
                                   self.grep_validator("Created symlink"),
                                   self.grep_validator("Processing triggers for libc-bin"))

        self.remoter.execute(f"sudo /opt/CrowdStrike/falconctl -sf --cid='{falcon_sensor_cid}'")
        self.remoter.execute("sudo systemctl start falcon-sensor")
        self.remoter.execute("sudo systemctl enable falcon-sensor", self.grep_validator("Executing: /lib/systemd/systemd-sysv-install enable falcon-sensor"))
        return True


    def init_cpu_data_remote(self)-> str:
        """
        Init cpu data

        :return:
        """

        cpu_data = "".join(self.remoter.execute("lscpu --json")[0])
        logger.info(f"Fetched {cpu_data=}")
        cpu_data = json.loads(cpu_data)
        cpu_arch = cpu_data["lscpu"][0]["data"]
        if cpu_arch !="x86_64":
            raise NotImplementedError(f"CPU arch '{cpu_arch}' is not supported")

        return cpu_arch

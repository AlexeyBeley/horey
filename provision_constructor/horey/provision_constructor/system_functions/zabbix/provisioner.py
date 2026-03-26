"""
Provision ntp service.

"""

import threading
from pathlib import Path

import requests

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
    Provision ntp service.
    Remove all others.

    """
    LOCK = threading.Lock()

    def provision_remote(self, remoter: Remoter):
        """
        Provision remotely

        :param remoter:
        :return:
        """

        self.remoter = remoter
        match self.action:
            case "wait_for_service_uptime":
                return self.wait_for_service_uptime_remote()
            case _:
                zabbix_server_address = self.kwargs.get("zabbix_server_address")
                hostname = self.kwargs.get("hostname")
                return self.install_remote(zabbix_server_address=zabbix_server_address, hostname=hostname, wait_for_service_uptime=self.kwargs.get("wait_for_service_uptime", True))

    def install_remote(self, zabbix_server_address=None, hostname=None, wait_for_service_uptime=True):
        """
        Install zabbix agent

        :param zabbix_server_address:
        :param hostname:
        :return:
        """

        zabbix_agent_version = "zabbix-release_latest+ubuntu24.04_all.deb"
        url = f"https://repo.zabbix.com/zabbix/8.0/release/ubuntu/pool/main/z/zabbix-release/{zabbix_agent_version}"

        if local_cache_dir_path :=self.kwargs.get("local_cache_dir_path"):
            deb_file_path = local_cache_dir_path / zabbix_agent_version

            with Provisioner.LOCK:
                if not deb_file_path.exists():
                    response = requests.get(url, timeout=180)
                    with open(deb_file_path, "wb") as file_handler:
                        file_handler.write(response.content)
                        logger.info(f"Downloaded {deb_file_path}")

            remote_deb_file_path = Path("/tmp") / zabbix_agent_version
            self.remoter.put_file(deb_file_path, remote_deb_file_path, sudo=False)
        else:
            remote_deb_file_path = Path("/tmp") / zabbix_agent_version
            self.remoter.execute(f"wget {url} -O {remote_deb_file_path}",
                            self.last_line_validator(" saved "),
                              self.last_line_validator(zabbix_agent_version))

        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, self.force, self.upgrade,
                                                                          action="unlock_dpckg").provision_remote(
            self.remoter)

        self.remoter.execute(f"sudo dpkg -i {remote_deb_file_path}", self.last_line_validator("Setting up zabbix-release "))
        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, self.force, self.upgrade,
                                                                          action="update_packages").provision_remote(
            self.remoter)
        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, self.force, self.upgrade,
                                                                          package_names=["zabbix-agent2"]).provision_remote(
            self.remoter)

        local_file_path = self.deployment_dir / "zabbix_agent2.conf"
        remote_file_path = Path("/etc/zabbix/zabbix_agent2.conf")


        self.remoter.get_file(remote_file_path, local_file_path)
        need_reconfigure = self.generate_configuration_file(local_file_path, zabbix_server_address, hostname)
        try:
            if not need_reconfigure:
                self.check_file_permissions_remote("/etc/zabbix/zabbix_agent2.conf", permissions="644", owner="root", group="root")
        except self.FailedCheckError:
            need_reconfigure = True

        if need_reconfigure:
            self.remoter.put_file(local_file_path, remote_file_path, sudo=True)

            self.remoter.execute("sudo chown root:root /etc/zabbix/zabbix_agent2.conf")
            self.remoter.execute("sudo chmod 644 /etc/zabbix/zabbix_agent2.conf")
            self.check_file_permissions_remote("/etc/zabbix/zabbix_agent2.conf", permissions="644", owner="root",
                                               group="root")

            self.remoter.execute("sudo systemctl restart zabbix-agent2")

        self.remoter.execute("sudo systemctl enable zabbix-agent2", self.grep_validator("Executing: /usr/lib/systemd/systemd-sysv-install enable zabbix-agent2"))
        if wait_for_service_uptime:
            self.wait_for_service_uptime_remote()
        return True

    def check_file_permissions_remote(self, remote_file_path, permissions=None, owner=None, group=None):
        """
        Check file permissions

        :param group:
        :param owner:
        :param permissions:
        :param remote_file_path:
        :return:
        """

        response = ""
        request = ""
        if permissions:
            response += f",{permissions}"
            request += ",%a"
        if owner:
            response += f",{owner}"
            request += ",%U"
        if group:
            response += f",{group}"
            request += ",%G"

        ret = self.remoter.execute(f"sudo stat -c '{request}' {remote_file_path}")
        if ret[0][-1].strip("\n") != response:
            raise self.FailedCheckError(f"Wrong permissions: {ret[0][-1]} vs {response}")

        return True

    def generate_configuration_file(self, local_file_path, zabbix_server_address, hostname)-> bool:
        """
        Make replacements

        :param local_file_path:
        :return: True, if replaced, False if the config is already fine and you do not need restart
        """

        if not zabbix_server_address or not hostname:
            raise RuntimeError("zabbix_server_address and hostname can not be empty")

        with open(local_file_path, encoding="utf-8") as file_handler:
            lines = file_handler.readlines()

        server_line = f"Server={zabbix_server_address}\n"
        server_active_line = f"ServerActive={zabbix_server_address}\n"
        hostname_line = f"Hostname={hostname}\n"

        for line in [server_line, server_active_line, hostname_line]:
            if line_count:= lines.count(line) == 0:
                break
            if line_count  > 1:
                raise ValueError(f"Multiple {line} lines found")
        else:
            return False

        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith("Server="):
                if found:
                    raise ValueError("Multiple Server= lines found")
                lines[i] = f"Server={zabbix_server_address}\n"
                found = True
        if not found:
            lines.append(f"Server={zabbix_server_address}\n")

        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith("ServerActive="):
                if found:
                    raise ValueError("Multiple ServerActive= lines found")
                lines[i] = f"ServerActive={zabbix_server_address}\n"
                found = True
        if not found:
            lines.append(f"ServerActive={zabbix_server_address}\n")

        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith("Hostname="):
                if found:
                    raise ValueError("Multiple Hostname= lines found")
                lines[i] = f"Hostname={hostname}\n"
                found = True

        with open(local_file_path, "w", encoding="utf-8") as file_handler:
            file_handler.writelines(lines)

        return True

    def wait_for_service_uptime_remote(self):
        """
        Wait for service to be up and running.

        :return:
        """

        SystemFunctionFactory.REGISTERED_FUNCTIONS["systemd"](self.deployment_dir, self.force,
                                                                          self.upgrade,
                                                                          action="wait_for_service_uptime",
                                                                         service_name="zabbix-agent2").provision_remote(
            self.remoter)

"""
Provision ntp service.

"""

import re
import time
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
    Provision ntp service.
    Remove all others.

    """

    def __init__(self, deployment_dir, force, upgrade, **kwargs):
        super().__init__(deployment_dir, force, upgrade, **kwargs)

        self.zabbix_server_address = self.kwargs["zabbix_server_address"]
        self.role = self.kwargs["role"]
        self.hostname = self.kwargs["hostname"]
        self.validate_input()


    def provision_remote(self, remoter: Remoter):
        """
        Provision remotely

        :param remoter:
        :return:
        """

        self.remoter = remoter

        if deb_file_path:=self.kwargs.get("deb_file_path"):
            remote_deb_file_path = Path("/tmp") / deb_file_path.name
            remoter.put_file(deb_file_path, remote_deb_file_path, sudo=False)
        else:
            zabbix_agent_version = "zabbix-release_7.0-2+ubuntu24.04_all.deb"
            remote_deb_file_path = Path("/tmp") / zabbix_agent_version
            remoter.execute(f"wget https://repo.zabbix.com/zabbix/7.0/ubuntu/pool/main/z/zabbix-release/{zabbix_agent_version} -O {remote_deb_file_path}",
                            self.last_line_validator(" saved "),
                              self.last_line_validator(zabbix_agent_version))

        remoter.execute(f"ls -la {remote_deb_file_path}")
        remoter.execute(f"sudo dpkg -i {remote_deb_file_path}", self.last_line_validator("Setting up zabbix-release "))
        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, self.force, self.upgrade,
                                                                          action="update_packages").provision_remote(
            remoter)

        remoter.execute("sudo apt install zabbix-agent2 -y")

        local_file_path = self.deployment_dir / "zabbix_agent2.conf"
        remote_file_path = Path("/etc/zabbix/zabbix_agent2.conf")


        remoter.get_file(remote_file_path, local_file_path)
        need_reconfigure = self.generate_configuration_file(local_file_path)
        try:
            if not need_reconfigure:
                self.check_file_permissions_remote("/etc/zabbix/zabbix_agent2.conf", permissions="644", owner="root", group="root")
        except self.FailedCheckError:
            need_reconfigure = True

        if need_reconfigure:
            remoter.put_file(local_file_path, remote_file_path, sudo=True)

            remoter.execute("sudo chown root:root /etc/zabbix/zabbix_agent2.conf")
            remoter.execute("sudo chmod 644 /etc/zabbix/zabbix_agent2.conf")
            self.check_file_permissions_remote("/etc/zabbix/zabbix_agent2.conf", permissions="644", owner="root",
                                               group="root")

            remoter.execute("sudo systemctl restart zabbix-agent2")

        remoter.execute("sudo systemctl enable zabbix-agent2", self.grep_validator("Executing: /usr/lib/systemd/systemd-sysv-install enable zabbix-agent2"))
        self.check_systemd_service_status_remote("zabbix-agent2")
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

    def validate_input(self):
        """
        Chec input.

        :return:
        """

        for attr in ["zabbix_server_address", "role", "hostname"]:
            if not getattr(self, attr):
                raise ValueError(f"{attr} can not be empty")

    def generate_configuration_file(self, local_file_path)-> bool:
        """
        Make replacements

        :param local_file_path:
        :return: True, if replaced, False if the config is already fine and you do not need restart
        """

        if not self.zabbix_server_address or not self.hostname:
            raise RuntimeError("zabbix_server_address and hostname can not be empty")

        with open(local_file_path, encoding="utf-8") as file_handler:
            lines = file_handler.readlines()

        server_line = f"Server={self.zabbix_server_address}\n"
        server_active_line = f"ServerActive={self.zabbix_server_address}\n"
        hostname_line = f"Hostname={self.hostname}\n"

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
                lines[i] = f"Server={self.zabbix_server_address}\n"
                found = True
        if not found:
            lines.append(f"Server={self.zabbix_server_address}\n")

        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith("ServerActive="):
                if found:
                    raise ValueError("Multiple ServerActive= lines found")
                lines[i] = f"ServerActive={self.zabbix_server_address}\n"
                found = True
        if not found:
            lines.append(f"ServerActive={self.zabbix_server_address}\n")

        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith("Hostname="):
                if found:
                    raise ValueError("Multiple Hostname= lines found")
                lines[i] = f"Hostname={self.hostname}\n"
                found = True

        with open(local_file_path, "w", encoding="utf-8") as file_handler:
            file_handler.writelines(lines)

        return True

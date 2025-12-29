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

    def _provision(self):
        """
        Provision ntp.
        wget https://repo.zabbix.com/zabbix/7.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_7.0-2+ubuntu24.04_all.deb
        sudo dpkg -i zabbix-release_7.0-2+ubuntu24.04_all.deb
        sudo apt update

        echo Y | sudo apt install zabbix-agent2 -y

        # sudo cp zabbix_agent2.conf /etc/zabbix/zabbix_agent2.conf

        sudo systemctl restart zabbix-agent2
        sudo systemctl enable zabbix-agent2
        @return:
        """
        raise NotImplementedError("todo:")

    def provision_remote(self, remoter: Remoter):
        """
        Provision remotely

        :param remoter:
        :return:
        """

        zabbix_agent_version = "zabbix-release_7.0-2+ubuntu24.04_all.deb"

        remoter.execute(f"wget https://repo.zabbix.com/zabbix/7.0/ubuntu/pool/main/z/zabbix-release/{zabbix_agent_version}",
                              self.last_line_validator(" saved "),
                              self.last_line_validator(zabbix_agent_version),
                              )

        remoter.execute(f"sudo dpkg -i {zabbix_agent_version}", self.last_line_validator("Setting up zabbix-release "))
        remoter.execute(f"sudo apt update", self.last_line_validator("All packages are up to date."))

        remoter.execute("sudo apt install zabbix-agent2 -y")

        local_file_path = Path("/tmp/zabbix_agent2.conf")
        remote_file_path = Path("/etc/zabbix/zabbix_agent2.conf")

        remoter.get_file(remote_file_path, local_file_path)
        self.generate_configuration_file(local_file_path)
        remoter.put_file(local_file_path, remote_file_path, sudo=True)

        self.check_systemd_service_status_remotely(remoter, "zabbix-agent2")
        remoter.execute("sudo systemctl restart zabbix-agent2")
        remoter.execute("sudo systemctl enable zabbix-agent2", self.last_line_validator("Executing: /usr/lib/systemd/systemd-sysv-install enable zabbix-agent2"))
        self.check_systemd_service_status_remotely(remoter, "zabbix-agent2")
        return True

    def validate_input(self):
        """
        Chec input.

        :return:
        """

        for attr in ["zabbix_server_address", "role", "hostname"]:
            if getattr(self, attr) is None:
                raise RuntimeError(attr)

    def generate_configuration_file(self, local_file_path):
        """
        Make replacements

        :param local_file_path:
        :return:
        """

        with open(local_file_path, encoding="utf-8") as file_handler:
            lines = file_handler.readlines()

        if f"ServerActive={self.zabbix_server_address}\n" in lines and \
            f"Server={self.zabbix_server_address}\n" in lines:
            return True

        self.replace_regex_line(local_file_path, f"^ServerActive={re.escape('127.0.0.1')}\n", f"ServerActive={self.zabbix_server_address}\n")
        self.replace_regex_line(local_file_path, f"^Server={re.escape('127.0.0.1')}\n", f"Server={self.zabbix_server_address}\n")
        return True

    @staticmethod
    def last_line_validator(string_to_look_for, convert_to_lower=True):
        """
        Check latest nonempty line contains the string.

        :param convert_to_lower:
        :param string_to_look_for:
        :return:
        """

        if convert_to_lower:
            string_to_look_for = string_to_look_for.lower()

        def helper(lst_stdin, lst_stderr, error_code):
            line = ""
            for line in reversed(lst_stdin):
                if not line or line == "\n":
                    continue
                if convert_to_lower:
                    line = line.lower()
                if string_to_look_for in line:
                    return True

            raise ValueError(f"Can not find '{convert_to_lower}' in the last line {line}")
        return helper

    @staticmethod
    def replace_regex_line(file_path:Path, regex_pattern: str, replacement_line: str):
        """
        Replace matching line

        :return:
        """

        with open(file_path, encoding="utf-8") as file_handler:
            lines = file_handler.readlines()

        found = False
        for i, line in enumerate(lines):
            new_line = re.sub(regex_pattern, replacement_line, line)

            if line != new_line:
                lines[i] = new_line
                found = True

        if not found:
            raise NotImplementedError(f"Can not find regex {regex_pattern} in file {file_path}")

        with open(file_path, "w", encoding="utf-8") as file_handler:
            file_handler.writelines(lines)

    @staticmethod
    def check_systemd_service_status_remotely(remoter: Remoter, service_name: str, min_uptime: int = 60):
        """
        Check the service uptime.

        :param remoter:
        :param service_name:
        :param min_uptime:
        :return:
        """

        command = f'servicestartsec=$(date -d "$(systemctl show --property=ActiveEnterTimestamp {service_name} | cut -d= -f2)" +%s) && serviceelapsedsec=$(( $(date +%s) - servicestartsec )) && echo $serviceelapsedsec'
        sleep_time = 10
        retries = (min_uptime * 2 // sleep_time)
        for i in range(retries):
            lst_stdout, _, _ = remoter.execute(command)
            str_seconds = lst_stdout[-1].strip("\n")
            int_seconds = int(str_seconds)
            if int_seconds >= min_uptime:
                return True

            logger.info(f"Service is up for {str_seconds} seconds {min_uptime=}. Going to sleep for {sleep_time} [{i}/{retries}]")

            time.sleep(sleep_time)
        raise TimeoutError(f"Waited for {min_uptime} seconds")

"""
Provision ntp service.

"""
from pathlib import Path
from typing import List

from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.common_utils.bash_executor import BashExecutor
from horey.h_logger import get_logger
from horey.common_utils.remoter import Remoter

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
        self.remoter = None

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

        @return:
        """

        breakpoint()

    def provision_remote(self, remoter: Remoter):
        """
        Provision remotely
        Preparing to unpack influxdb_1.12.2-1_amd64.deb ...

        :param remoter:
        :return:
        """

        self.remoter = remoter
        match self.action:
            case "provision_influxdb":
                return self.provision_remote_provision_influxdb()
            case "create_databases":
                return self.provision_remote_create_databases()
            case "provision_kapacitor":
                return self.provision_remote_provision_kapacitor()
            case "create_subscription":
                return self.provision_remote_create_subscription()
            case "create_user":
                return self.provision_remote_create_user()
            case _:
                raise NotImplementedError(f"{self.action}")

    def provision_remote_provision_influxdb(self):
        """
        Provision remotely.

        :return:
        """

        admin_username = self.kwargs["admin_username"]
        admin_password = self.kwargs["admin_password"]

        version = "influxdb_1.12.2-1"
        self.remoter.execute(
            f"wget https://repos.influxdata.com/packages/{version}_amd64.deb",
            self.last_line_validator(" saved "),
            self.last_line_validator(version),
        )
        # todo: check if needed: wget https://download.influxdata.com/influxdb/releases/v1.12.2/influxdb_1.12.2-1_amd64.deb.sha256

        self.remoter.execute(
            f"sudo dpkg -i {version}_amd64.deb",
            self.grep_validator(["Unpacking influxdb",
                                 "Setting up influxdb",
                                 "Synchronizing state of influxdb.service",
                                 "Executing: /usr/lib/systemd/systemd-sysv-install enable influxdb"])
        )

        remote_file_path = Path("/etc/kapacitor/kapacitor_base.conf")
        local_file_path = Path("/tmp") / remote_file_path.name

        self.remoter.get_file(remote_file_path, local_file_path)
        self.generate_influx_configuration_file(local_file_path)
        self.remoter.put_file(local_file_path, remote_file_path, sudo=True)

        ret = self.remoter.execute(
            f'curl -XPOST "http://localhost:8086/query" --data-urlencode "q=CREATE USER {admin_username} WITH PASSWORD \'{admin_password}\' WITH ALL PRIVILEGES"')

        self.systemctl_restart_service_and_wait_remotely("influxdb")
        return True

    def generate_influx_configuration_file(self, local_file_path):
        """
        Enable authorization.

        :return:
        """

    def provision_remote_create_databases(self):
        """
        Create the DBs

        :return:
        """

        databases = self.kwargs.get("databases")
        for database in databases:
            self.remoter.execute(
                f"influx -execute 'CREATE DATABASE {database}'"
            )

        return True

    def provision_remote_provision_kapacitor(self):
        """
        Install kapacitor
        wget https://dl.influxdata.com/kapacitor/releases/kapacitor_1.8.2-1_amd64.deb
        sudo dpkg -i kapacitor_1.8.2-1_amd64.deb


        Security: https://docs.influxdata.com/kapacitor/v1/administration/security/

        :return:
        """
        influx_username, influx_password = self.kwargs["influx_username"], self.kwargs["influx_password"]
        breakpoint()
        version = "kapacitor_1.8.2-1"
        self.remoter.execute(
            f"wget https://dl.influxdata.com/kapacitor/releases/{version}_amd64.deb",
            self.last_line_validator(" saved "),
            self.last_line_validator(version)
        )

        self.remoter.execute(
            f"sudo dpkg -i {version}_amd64.deb",
            self.grep_validator(["Unpacking kapacitor",
                                 "Setting up kapacitor"])
        )
        # todo: check: systemctl is-enabled kapacitor

        remote_file_path = Path("/etc/kapacitor/kapacitor_base.conf")
        local_file_path = Path("/tmp") / remote_file_path.name

        self.remoter.get_file(remote_file_path, local_file_path)
        self.generate_kapacitor_configuration_file(local_file_path, influx_username, influx_password)
        self.remoter.put_file(local_file_path, remote_file_path, sudo=True)

        self.systemctl_restart_service_and_wait_remotely("kapacitor")

        return True

    def generate_kapacitor_configuration_file(self, local_file_path, influx_username, influx_password):
        """
        Generate

        :param local_file_path:
        :return:
        """

        with open(local_file_path, encoding="utf-8") as file_handler:
            lines = file_handler.readlines()

        username_set = False
        password_set = False
        influxdb_context = False
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("[["):
                if influxdb_context:
                    raise ValueError(f"Reached block {line}")
                if line.strip() == "[[influxdb]]":
                    influxdb_context = True
                    continue
                if not influxdb_context:
                    continue
                breakpoint()
                if line.startswith("username"):
                    lines[i] = f'  username = "{influx_username}"\n'
                    username_set = True
                elif line.startswith("password"):
                    lines[i] = f'  password = "{influx_password}"\n'
                    password_set = True
                if username_set and password_set:
                    break
        else:
            raise ValueError("Reached end of file without replacing the influx credentials")

        with open(local_file_path, "w", encoding="utf-8") as file_handler:
            file_handler.writelines(lines)

    def find_configuration_context(self, lines: List[str], context: str) -> (int, int):
        """
        Find config context

        :param lines:
        :param context:
        :return:
        """

        in_context = False
        start_index = None
        context_header = f"[[{context}]]"
        end_index = None
        for end_index, line in enumerate(lines):
            line = line.strip()
            if line.startswith("[["):
                if in_context:
                    return start_index, end_index
                if line.strip() == context_header:
                    in_context = True

        if start_index is None:
            raise RuntimeError(f"Was not able to find context header {context_header}")

        if end_index is None:
            raise RuntimeError("Was not able to initialize the end index")

        return start_index, end_index

    def provision_remote_create_user(self):
        """
        Create user

        :return:
        """

        breakpoint()
        for database in self.kwargs["databases"]:
            self.remoter.execute(
                f"influx -execute 'CREATE USER {self.kwargs['user']} WITH PASSWORD {self.kwargs['password']}'",
                self.last_line_validator(" saved "),
            )
        return True

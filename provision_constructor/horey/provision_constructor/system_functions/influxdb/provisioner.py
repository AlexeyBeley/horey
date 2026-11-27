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
            case "enable_auth":
                return self.provision_remote_enable_auth()
            case "kapacitor_enable_auth":
                return self.provision_remote_kapacitor_enable_auth()
            case "create_databases":
                return self.provision_remote_create_databases()
            case "provision_kapacitor":
                return self.provision_remote_provision_kapacitor()
            case "configure_kapacitor":
                return self.provision_remote_configure_kapacitor()
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

        return True

    def provision_remote_enable_auth(self):
        """
        Enable auth with admin user
        :return:
        """

        admin_username = self.kwargs["admin_username"]
        admin_password = self.kwargs["admin_password"]

        self.remoter.execute(
            f'curl -XPOST "http://localhost:8086/query" --data-urlencode "q=CREATE USER {admin_username} WITH PASSWORD \'{admin_password}\' WITH ALL PRIVILEGES"',\
            self.last_line_validator("'{\"results\":[{\"statement_id\":0}]}'")
        )
        # '{"error":"unable to parse authentication credentials"}\n'

        remote_file_path = Path("/etc/influxdb/influxdb.conf")
        local_file_path = self.deployment_dir / remote_file_path.name

        self.remoter.get_file(remote_file_path, local_file_path)
        self.generate_influx_configuration_file(local_file_path)
        self.remoter.put_file(local_file_path, remote_file_path, sudo=True)
        self.systemctl_restart_service_and_wait_remote("influxdb")

        return True

    def provision_remote_kapacitor_enable_auth(self):
        """
        Enable auth with admin user

        curl --request POST 'http://localhost:9092/kapacitor/v1/users' \
        --data '{
        "name": "exampleUsername",
        "password": "examplePassword",
        "type":"admin"
        }'

        :return:
        """
        """
        """

        kwargs = {}
        kwargs["username"] = self.kwargs["admin_username"]
        kwargs["password"] = self.kwargs["admin_password"]

        remote_file_path = Path("/etc/kapacitor/kapacitor.conf")
        local_file_path = self.deployment_dir / remote_file_path.name
        self.generate_kapacitor_configuration_file(local_file_path, "[auth]", **kwargs)

        self.remoter.get_file(remote_file_path, local_file_path)
        self.generate_influx_configuration_file(local_file_path)
        self.remoter.put_file(local_file_path, remote_file_path, sudo=True)
        self.systemctl_restart_service_and_wait_remote("influxdb")

        return True

    def generate_influx_configuration_file(self, local_file_path):
        """
        Enable authorization.

        :return:
        """

        with open(local_file_path, encoding="utf-8") as file_handler:
            lines = file_handler.readlines()

        # todo: old style shit, use kapacitor config consept instead
        start_index, end_index = self.find_configuration_context(lines, "[http]")
        for i in range(start_index, end_index):
            if "auth-enabled" in lines[i]:
                lines[i] = "  auth-enabled = true"
                break
        else:
            raise ValueError("Was not able to find 'auth-enabled'")

        with open(local_file_path, "w", encoding="utf-8") as file_handler:
            file_handler.writelines(lines)

    def provision_remote_create_databases(self):
        """
        Create the DBs

        :return:
        """

        databases = self.kwargs.get("databases")
        admin_username = self.kwargs["admin_username"]
        admin_password = self.kwargs["admin_password"]

        for database in databases:
            self.remoter.execute(
                f"influx -username {admin_username} -password {admin_password} -execute 'CREATE DATABASE {database}'"
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
        return True

    def provision_remote_configure_kapacitor(self):
        """
        Change configuration.

        :return:
        """

        kwargs = {}
        for key in ["username", "password", "urls"]:
            try:
                kwargs[key] = self.kwargs[key]
            except KeyError:
                pass

        remote_file_path = Path("/etc/kapacitor/kapacitor.conf")
        local_file_path = self.deployment_dir / remote_file_path.name

        self.remoter.get_file(remote_file_path, local_file_path)
        self.generate_kapacitor_configuration_file(local_file_path, "[[influxdb]]", **kwargs)
        self.remoter.put_file(local_file_path, remote_file_path, sudo=True)

        self.systemctl_restart_service_and_wait_remote("kapacitor")

        return True

    def generate_kapacitor_configuration_file(self, local_file_path, context_header, **kwargs):
        """
        Generate

        :param context_header:
        :param local_file_path:
        :return:
        """

        for key in kwargs:
            if key not in ["username", "password", "urls"]:
                raise NotImplementedError(f"Kapacitor config {key}")

        with open(local_file_path, encoding="utf-8") as file_handler:
            lines = file_handler.readlines()

        start_index, end_index = self.find_configuration_context(lines, context_header)
        updated_keys = []
        for i in range(start_index, end_index):
            line = lines[i].strip()

            if line.startswith("#"):
                continue
            key = line.split("=", 1)[0].strip()
            if key in kwargs:
                lines[i] = f"  {key} = {self.conver_to_config_value(kwargs[key])}\n"
                updated_keys.append(key)
        for key in kwargs:
            if key not in updated_keys:
                lines.append(f"  {key} = {self.conver_to_config_value(kwargs[key])}\n")

        with open(local_file_path, "w", encoding="utf-8") as file_handler:
            file_handler.writelines(lines)
        return True

    def conver_to_config_value(self, obj):
        """
        Convert received value to string

        :param obj:
        :return:
        """

        if isinstance(obj, str):
            return f'"{obj}"'

        if isinstance(obj, list):
            values = '", "'.join(obj)
            return f'["{values}"]'

        raise NotImplementedError(f"Can not convert kapacitor config to string value {obj}")

    def find_configuration_context(self, lines: List[str], context_header: str) -> (int, int):
        """
        Find config context

        :param lines:
        :param context_header:
        :return:
        """

        start_index = None
        cur_index = None
        for cur_index, line in enumerate(lines):
            line_stripped = line.strip()
            if line.startswith("["):
                if start_index is not None:
                    return start_index, cur_index-1
                if line_stripped == context_header:
                    start_index = cur_index

        if start_index is None:
            raise RuntimeError(f"Was not able to find context header {context_header}")

        if cur_index is None:
            raise RuntimeError("Was not able to initialize the end index")

        return start_index, cur_index

    def provision_remote_create_user(self):
        """
        Create user
        SET PASSWORD FOR "username" = 'newpassword'
        GRANT READ ON "NOAA_water_database" TO "username"
        GRANT WRITE ON "<database_name>" TO "<username>"

        :return:
        """

        admin_username = self.kwargs["admin_username"]
        admin_password = self.kwargs["admin_password"]

        user = self.kwargs["user"]
        password = self.kwargs["password"]
        admin = self.kwargs.get("admin", False)
        if admin and admin is not True:
            raise ValueError(f"Only possible value for 'admin' is boolean 'True', received: '{admin}'")

        # Single quote only supported
        self.remoter.execute(
            f"influx -username {admin_username} -password {admin_password} -execute \"CREATE USER {user} WITH PASSWORD '{password}'\""
        )

        if admin:
            self.remoter.execute(
                f"influx -username {admin_username} -password {admin_password} -execute 'GRANT ALL PRIVILEGES TO {user}'"
            )
            return True

        read_dbs = set(self.kwargs.get("read_databases", []))
        write_dbs = set(self.kwargs.get("read_databases", []))
        read_only = read_dbs - write_dbs
        write_only = write_dbs - read_dbs
        read_and_write_dbs = read_dbs.intersection(write_dbs)

        for database in read_only:
            self.remoter.execute(
                f"influx -username {admin_username} -password {admin_password} -execute 'GRANT READ ON {database} TO {user}'"
            )

        for database in write_only:
            self.remoter.execute(
                f"influx -username {admin_username} -password {admin_password} -execute 'GRANT WRITE ON {database} TO {user}'"
            )

        for database in read_and_write_dbs:
            self.remoter.execute(
                f"influx -username {admin_username} -password {admin_password} -execute 'GRANT ALL ON {database} TO {user}'"
            )

        return True

    def provision_remote_crete_subscription(self):
        """
        kapacitor -url http://<username>:<password>@localhost:9092

        :return:
        """
        breakpoint()
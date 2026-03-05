"""
Logstash service provisioner.

"""

import os
import textwrap
from pathlib import Path

from horey.common_utils.remoter import Remoter
from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """
    Main class.

    """

    def __init__(self, deployment_dir, force, upgrade, **kwargs):
        """

        :param deployment_dir:
        :param force:
        :param upgrade:
        :param kwargs:
        run_as_root = run the service as root
        plugin_name - install plugin
        """
        super().__init__(deployment_dir, force, upgrade, **kwargs)

    def _provision(self):
        """
        Provision all components.
        wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elastic-keyring.gpg

        retry_10_times_sleep_5 apt install --upgrade default-jre -y
        retry_10_times_sleep_5 apt install --upgrade default-jdk -y
        #done
        echo "deb [signed-by=/usr/share/keyrings/elastic-keyring.gpg] https://artifacts.elastic.co/packages/9.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-9.x.list
        sudo rm  /etc/apt/sources.list.d/elastic-7.x.list
        sudo apt update
        sudo apt install --upgrade logstash -y
        sudo systemctl daemon-reload
        sudo systemctl enable logstash

        :return:
        """

        SystemFunctionFactory.REGISTERED_FUNCTIONS["java"](self.deployment_dir, self.force, self.upgrade).provision()

        src_url = "https://artifacts.elastic.co/GPG-KEY-elasticsearch"
        dst_file_path = "/usr/share/keyrings/elastic-keyring.gpg"
        SystemFunctionFactory.REGISTERED_FUNCTIONS["gpg_key"](self.deployment_dir, self.force,
                                                              self.upgrade, src_url=src_url,
                                                              dst_file_path=dst_file_path).provision()

        self.remove_file("/etc/apt/sources.list.d/elastic-7.x.list", sudo=True)

        line = f"deb [signed-by={dst_file_path}] https://artifacts.elastic.co/packages/9.x/apt stable main"
        self.add_line_to_file(line=line, file_path="/etc/apt/sources.list.d/elastic-9.x.list", sudo=True)
        self.reinit_apt_packages()
        self.apt_install("logstash")
        self.run_bash("sudo systemctl daemon-reload")
        # self.run_bash(f"sudo systemctl restart logstash")
        self.run_bash("sudo systemctl enable logstash")

    def test_provisioned(self):
        """
        Test the sys_function was provisioned.

        :return:
        """
        return self.apt_check_installed("logstash")

    def provision_remote(self, remoter: Remoter):
        """
        Provision remotely

        :param remoter:
        :return:
        """

        self.remoter = remoter
        if self.action == "install":
            return self.provision_remote_install_logstash_from_binary()

        if self.action == "install_plugin":
            return self.provision_remote_install_plugin()

        if self.action == "restart":
            return self.provision_remote_restart()

        raise NotImplementedError(self.action)

    def provision_remote_install_logstash_from_binary(self):
        """
        Provision logstash from binary.

        :return:
        """

        logstash_version = self.kwargs.get("logstash_version", "9.3.1")
        if not logstash_version:
            raise ValueError("logstash_version must be specified")

        logstash_tarball = f"logstash-oss-{logstash_version}-linux-x86_64.tar.gz"
        tarball_path = self.deployment_dir / logstash_tarball
        if not tarball_path.exists():
            logstash_url = f"https://artifacts.elastic.co/downloads/logstash/{logstash_tarball}"
            self.deployment_dir.mkdir(exist_ok=True)
            self.download_file_from_web(logstash_url, tarball_path)

        self.remoter.put_file(tarball_path, Path(f"/tmp/{logstash_tarball}"))

        # Verify file integrity before extraction
        self.remoter.execute(f"gzip -t /tmp/{logstash_tarball}")

        self.remoter.execute(f"sudo mkdir -p /opt/logstash")
        self.remoter.execute(f"sudo tar -xzf /tmp/{logstash_tarball} -C /opt/logstash --strip-components 1")
        self.remoter.execute(f"sudo chown -R root:root /opt/logstash")
        self.remoter.execute(f"sudo rm /tmp/{logstash_tarball}")

        # Create symlink
        self.remoter.execute(f"sudo ln -sf /opt/logstash/bin/logstash /usr/local/bin/logstash")

        # Create logstash user if it doesn't exist
        self.remoter.execute("id -u logstash >/dev/null 2>&1 || sudo useradd logstash -r -s /sbin/nologin")
        self.remoter.execute("sudo usermod -a -G logstash $USER")

        # Create logstash config directory
        self.remoter.execute("sudo mkdir -p /etc/logstash")

        # Create logstash service
        self.remoter.execute("sudo touch /etc/systemd/system/logstash.service")
        self.remoter.execute("sudo chmod 644 /etc/systemd/system/logstash.service")

        logstash_service_file = self.deployment_dir / "logstash.service"
        # Write logstash service file
        service_content = textwrap.dedent("""[Unit]
                                             Description=Logstash
                                             After=network.target

                                            [Service]
                                            Type=simple
                                            User=logstash
                                            Group=logstash
                                            ExecStart=/usr/local/bin/logstash "--path.settings" "/etc/logstash"
                                            Restart=always
                                            RestartSec=10

                                            [Install]
                                            WantedBy=multi-user.target
                                            """)
        if self.kwargs.get("run_as_root"):
            service_content.replace("User=logstash\n", "User=root\n")
            service_content.replace("Group=logstash\n", "Group=root\n")

        logstash_service_file.write_text(service_content)

        self.remoter.put_file(logstash_service_file, Path("/etc/systemd/system/logstash.service"), sudo=True)
        self.remoter.execute("sudo systemctl daemon-reload")
        self.remoter.execute("sudo systemctl enable logstash")

    def provision_remote_install_plugin(self):
        """
        Install plugin

        :return:
        """

        plugin_name = self.kwargs.get("plugin_name")
        if not plugin_name:
            raise ValueError("plugin_name must be specified")

        self.remoter.execute(f"sudo /opt/logstash/bin/logstash-plugin install {plugin_name}",
                             self.last_line_validator("Installation successful"))

        return True

    def provision_remote_install_logstash_from_apt(self):
        """
        Install plugin

        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, self.force, self.upgrade,
                                                                          package_names=[
                                                                              "openjdk-17-jdk"]).provision_remote(
            remoter)

        :return:
        """

        src_url = "https://artifacts.elastic.co/GPG-KEY-elasticsearch"
        dst_file_path = "/usr/share/keyrings/elastic-keyring.gpg"
        SystemFunctionFactory.REGISTERED_FUNCTIONS["gpg_key"](self.deployment_dir, self.force,
                                                              self.upgrade, src_url=src_url,
                                                              dst_file_path=dst_file_path).provision_remote(
            self.remoter)

        file_paths = self.ls_remote(Path("/etc/apt/sources.list.d/"), sudo=True)
        elastic_version = "9.x"
        elastic_file_name = f"elastic-{elastic_version}.list"

        for file_path in file_paths:
            file_name = file_path.name
            if "elastic-" in file_name:
                if file_name != elastic_file_name:
                    self.remove_file_remote(self.remoter, f"/etc/apt/sources.list.d/{file_name}", sudo=True)

        line = f"deb [signed-by={dst_file_path}] https://artifacts.elastic.co/packages/{elastic_version}/apt stable main"
        self.add_line_to_file_remote(self.remoter, line=line,
                                     file_path=Path(f"/etc/apt/sources.list.d/{elastic_file_name}"),
                                     sudo=True)

        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, True, self.upgrade,
                                                                          action="update_packages").provision_remote(
            self.remoter)

        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, self.force, self.upgrade,
                                                                          package_names=[
                                                                              "logstash"]).provision_remote(
            self.remoter)
        self.remoter.execute("sudo systemctl daemon-reload")
        self.remoter.execute("sudo systemctl enable logstash")
        # fix the memory size allowed for logstash
        self.remoter.execute("sudo sed -i '/-Xms/c\-Xms2g' /etc/logstash/jvm.options")
        self.remoter.execute("sudo sed -i '/-Xmx/c\-Xmx2g' /etc/logstash/jvm.options")

    def provision_remote_restart(self):
        """
        Restart logstash service

        :return:
        """

        ret = self.remoter.execute(
            "logstash_pid=$(ps aux | grep 'logstash' | grep 'java' | awk '{print $2}') && echo \"logstash_pid=${logstash_pid}\"")
        last_line = ret[0][-1]

        if "logstash_pid=" not in last_line:
            raise NotImplementedError(ret)

        logstash_pid = last_line.strip("\n").split("=")[1]
        if logstash_pid:
            self.remoter.execute(f"sudo kill -s 9 {int(logstash_pid)}")

        self.systemctl_restart_service_and_wait_remote("logstash")

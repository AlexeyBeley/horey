"""
Logstash service provisioner.

"""

import os
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
        super().__init__(deployment_dir, force, upgrade, **kwargs)

    def _provision(self):
        """
        Provision all components.
        wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elastic-keyring.gpg

        retry_10_times_sleep_5 apt install --upgrade default-jre -y
        retry_10_times_sleep_5 apt install --upgrade default-jdk -y
        #done
        echo "deb [signed-by=/usr/share/keyrings/elastic-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-8.x.list
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

        line = f"deb [signed-by={dst_file_path}] https://artifacts.elastic.co/packages/8.x/apt stable main"
        self.add_line_to_file(line=line, file_path="/etc/apt/sources.list.d/elastic-8.x.list", sudo=True)
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
            return self.provision_remote_install_logstash()

        if self.action == "install_plugin":
            return self.provision_remote_install_plugin()

        if self.action == "restart":
            return self.provision_remote_restart()

        raise NotImplementedError(self.action)

    def provision_remote_install_plugin(self):
        """
        Install plugin

        :return:
        """

        plugin_name = self.kwargs.get("plugin_name")
        if not plugin_name:
            raise ValueError("plugin_name must be specified")
        self.remoter.execute(f"sudo /usr/share/logstash/bin/logstash-plugin install {plugin_name}",
                        self.last_line_validator("Installation successful"))

        return True

    def provision_remote_install_logstash(self):
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
                                                              dst_file_path=dst_file_path).provision_remote(self.remoter)

        file_names = self.ls_remote(Path("/etc/apt/sources.list.d/"), sudo=True)
        elastic_version = "8.x"
        elastic_file_name = f"elastic-{elastic_version}.list"

        for file_name in file_names:
            if "elastic-" in file_name:
                if file_name != elastic_file_name:
                    self.remove_file_remote(self.remoter, f"/etc/apt/sources.list.d/{file_name}", sudo=True)

        line = f"deb [signed-by={dst_file_path}] https://artifacts.elastic.co/packages/{elastic_version}/apt stable main"
        self.add_line_to_file_remote(self.remoter, line=line, file_path=Path(f"/etc/apt/sources.list.d/{elastic_file_name}"),
                                     sudo=True)

        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, True, self.upgrade,
                                                                          action="update_packages").provision_remote(self.remoter)

        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, self.force, self.upgrade,
                                                                          package_names=[
                                                                              "logstash"]).provision_remote(
            self.remoter)
        self.remoter.execute("sudo systemctl daemon-reload")
        self.remoter.execute("sudo systemctl enable logstash")
        # fix the memory size allowed for logstash
        self.remoter.execute("sudo sed -i '/-Xms/c\-Xms2g' /etc/logstash/jvm.options")
        self.remoter.execute("sudo sed -i '/-Xmx/c\-Xmx2g' /etc/logstash/jvm.options")

    def ls_remote(self, path, sudo=False):
        """
        List remote files

        :param path:
        :param sudo:
        :return:
        """

        ret = self.remoter.execute(f"{'sudo ' if sudo else ''}ls -l {path}")
        lines = [line.strip("\n") for line in ret[0]]
        ret = []
        for line in reversed(lines):
            if line.startswith("total"):
                return ret
            ret.append(line.split(" ")[-1])
        raise ValueError(f"Was not able to find 'total <number>' in the output: '{ret}'")

    def provision_remote_restart(self):
        """
        Restart logstash service

        :return:
        """

        ret = self.remoter.execute("logstash_pid=$(ps aux | grep 'logstash' | grep 'java' | awk '{print $2}') && echo \"logstash_pid=${logstash_pid}\"")
        last_line = ret[0][-1]

        if "logstash_pid=" not in last_line:
            raise NotImplementedError(ret)

        logstash_pid = last_line.strip("\n").split("=")[1]
        if logstash_pid:
            self.remoter.execute(f"sudo kill -s 9 {int(logstash_pid)}")

        self.systemctl_restart_service_and_wait_remote("logstash")
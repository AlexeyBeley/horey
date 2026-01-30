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

        if self.action == "install":
            return self.provision_remote_install_logstash(remoter)

        if self.action == "install_plugin":
            return self.provision_remote_install_plugin(remoter)

        raise NotImplementedError(self.action)

    def provision_remote_install_plugin(self, remoter: Remoter):
        """
        Install plugin

        :param remoter:
        :return:
        """

        plugin_name = self.kwargs.get("plugin_name")
        if not plugin_name:
            raise ValueError("plugin_name must be specified")
        remoter.execute(f"sudo /usr/share/logstash/bin/logstash-plugin install {plugin_name}",
                        self.last_line_validator("Installation successful"))

        return True

    def provision_remote_install_logstash(self, remoter: Remoter):
        """
        Install plugin

        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, self.force, self.upgrade,
                                                                          package_names=[
                                                                              "openjdk-17-jdk"]).provision_remote(
            remoter)

        :param remoter:
        :return:
        """

        src_url = "https://artifacts.elastic.co/GPG-KEY-elasticsearch"
        dst_file_path = "/usr/share/keyrings/elastic-keyring.gpg"
        SystemFunctionFactory.REGISTERED_FUNCTIONS["gpg_key"](self.deployment_dir, self.force,
                                                              self.upgrade, src_url=src_url,
                                                              dst_file_path=dst_file_path).provision_remote(remoter)

        file_names = self.ls_remote(remoter, Path("/etc/apt/sources.list.d/"), sudo=True)
        elastic_version = "8.x"
        elastic_file_name = f"elastic-{elastic_version}.list"

        for file_name in file_names:
            if "elastic-" in file_name:
                if file_name != elastic_file_name:
                    self.remove_file_remote(remoter, f"/etc/apt/sources.list.d/{file_name}", sudo=True)

        line = f"deb [signed-by={dst_file_path}] https://artifacts.elastic.co/packages/{elastic_version}/apt stable main"
        self.add_line_to_file_remote(remoter, line=line, file_path=Path(f"/etc/apt/sources.list.d/{elastic_file_name}"),
                                     sudo=True)

        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, self.force, self.upgrade,
                                                                          action="update_packages").provision_rqemote(remoter)

        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, self.force, self.upgrade,
                                                                          package_names=[
                                                                              "logstash"]).provision_remote(
            remoter)
        remoter.execute("sudo systemctl daemon-reload")
        remoter.execute("sudo systemctl enable logstash")
        # fix the memory size allowed for logstash
        remoter.execute("sudo sed -i '/-Xms/c\-Xms2g' /etc/logstash/jvm.options")
        remoter.execute("sudo sed -i '/-Xmx/c\-Xmx2g' /etc/logstash/jvm.options")

    @staticmethod
    def ls_remote(remoter, path, sudo=False):
        """
        List remote files

        :param remoter:
        :param path:
        :param sudo:
        :return:
        """

        ret = remoter.execute(f"{'sudo ' if sudo else ''}ls -l {path}")
        lines = [line.strip("\n") for line in ret[0]]
        ret = []
        for line in reversed(lines):
            if line.startswith("total"):
                return ret
            ret.append(line.split(" ")[-1])
        raise ValueError(f"Was not able to find 'total <number>' in the output: '{ret}'")

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

    def test_provisioned(self):
        """
        Test the sys_function was provisioned.

        :return:
        """

    def provision_remote(self, remoter: Remoter):
        """
        Provision remotely

        :param remoter:
        :return:
        """

        if self.action == "set_dns_resolvers":
            return self.set_dns_resolvers_remote(remoter)

        raise NotImplementedError(self.action)

    def set_dns_resolvers_remote(self, remoter: Remoter):
        """
        set DNS server
        [Resolve]
        DNS=1.1.1.1 8.8.8.8
        FallbackDNS= 9.9.9.9 208.67.222.222

        sudo cp ./dns_servers.conf /etc/systemd/resolved.conf.d/dns_servers.conf
        sudo systemctl restart systemd-resolved

        :param remoter:
        :return:
        """

        primary = " ".join(self.kwargs.get("primary"))
        fallback = " ".join(self.kwargs.get("fallback"))

        file_content = ("[Resolve]\n"
                        f"DNS={primary}\n"
                        f"FallbackDNS={fallback}\n")
        local_file_path = self.deployment_dir / "dns_servers.conf"

        with open(local_file_path, "w", encoding="utf-8") as file_handle:
            file_handle.write(file_content)

        remoter.execute("sudo mkdir -p /etc/systemd/resolved.conf.d/")
        remoter.put_file(local_file_path, Path("/etc/systemd/resolved.conf.d/dns_servers.conf"), sudo=True)

        remoter.execute("sudo systemctl restart systemd-resolved")
        return True

"""
Logstash service provisioner.

"""

import os
from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """
    Main class.

    """

    def __init__(self, deployment_dir, force, upgrade):
        super().__init__(os.path.dirname(os.path.abspath(__file__)), force, upgrade)
        self.deployment_dir = deployment_dir

    def _provision(self):
        """
        Provision all components.
        wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elastic-keyring.gpg

        retry_10_times_sleep_5 apt install --upgrade default-jre -y
        retry_10_times_sleep_5 apt install --upgrade default-jdk -y
        echo "deb [signed-by=/usr/share/keyrings/elastic-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-8.x.list
        sudo rm  /etc/apt/sources.list.d/elastic-7.x.list
        sudo apt update
        sudo apt install --upgrade logstash -y
        sudo systemctl daemon-reload
        sudo systemctl enable logstash

        :return:
        """

        src_url = "https://artifacts.elastic.co/GPG-KEY-elasticsearch"
        dst_file_path = "/usr/share/keyrings/elastic-keyring.gpg"
        SystemFunctionFactory.REGISTERED_FUNCTIONS["gpg_key"](self.deployment_dir, self.force,
                                                              self.upgrade, src_url=src_url,
                                                              dst_file_path=dst_file_path).provision()

        SystemFunctionFactory.REGISTERED_FUNCTIONS["java"](self.deployment_dir, self.force, self.upgrade)

    def test_provisioned(self):
        """
        Test the sys_function was provisioned.

        :return:
        """

"""
Swap file provisioner.

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
    def __init__(
        self,
        deployment_dir, force, upgrade,
        swap_size_in_gb=None,
        ram_size_in_gb=None,
    ):
        super().__init__(os.path.dirname(os.path.abspath(__file__)), force, upgrade)
        self.deployment_dir = deployment_dir

        self.swap_size_in_gb = swap_size_in_gb
        self.ram_size_in_gb = ram_size_in_gb

        if self.swap_size_in_gb is None:
            self.swap_size_in_gb = self.ram_size_in_gb * 2

    def test_provisioned(self):
        """
        jre:
        openjdk-11-jre-headless/jammy-updates,jammy-security,now 11.0.18+10-0ubuntu1~22.04 amd64 [installed,automatic]
        openjdk-11-jre/jammy-updates,jammy-security,now 11.0.18+10-0ubuntu1~22.04 amd64 [installed,automatic]

        jdk:
        openjdk-11-jdk-headless/jammy-updates,jammy-security,now 11.0.18+10-0ubuntu1~22.04 amd64 [installed,automatic]
        openjdk-11-jdk/jammy-updates,jammy-security,now 11.0.18+10-0ubuntu1~22.04 amd64 [installed,automatic]
        :return:
        """

        ret = self.run_bash("free -m")
        breakpoint()

    def _provision(self):
        """
        :return:
        """
        breakpoint()
        ret = self.run_bash("sudo swapoff -a")
        ret = self.run_bash("sudo fallocate -l STRING_REPLACEMENT_SWAP_SIZE_IN_GBG /swapfile")
        ret = self.run_bash("sudo chmod 600 /swapfile")
        ret = self.run_bash("sudo mkswap /swapfile")
        ret = self.run_bash("sudo swapon /swapfile")
        self.add_line_to_file_sudo(line="/swapfile none swap sw 0 0", file_path="/etc/fstab")

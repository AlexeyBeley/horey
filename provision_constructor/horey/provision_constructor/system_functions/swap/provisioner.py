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
    # pylint: disable= too-many-arguments
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
                       total        used        free      shared  buff/cache   available
        Mem:           3.8Gi       1.7Gi       685Mi       3.0Mi       1.4Gi       1.8Gi
        Swap:          8.0Gi       4.0Mi       8.0Gi
        :return:
        """

        ret = self.run_bash("free -h")
        lines = ret["stdout"].split("\n")
        if lines[0].strip().split(" ")[0] != "total":
            raise RuntimeError(f"First's line first word is not 'total': {lines} ")
        for line in lines:
            if line.startswith("Swap:"):
                break
        else:
            raise RuntimeError(f"No line that starts with 'Swap:': {lines} ")

        while "  " in line:
            line = line.replace("  ", " ")

        output_total_size = line.split(" ")[1]
        if not output_total_size.endswith("Gi"):
            return False

        total_gigs_configured = int(float(output_total_size[:-2]))
        return total_gigs_configured-1 <= self.swap_size_in_gb <= total_gigs_configured+1

    def _provision(self):
        """
        :return:
        """
        self.run_bash("sudo swapoff -a")
        self.run_bash(f"sudo fallocate -l {self.swap_size_in_gb}G /swapfile")
        self.run_bash("sudo chmod 600 /swapfile")
        self.run_bash("sudo mkswap /swapfile")
        self.run_bash("sudo swapon /swapfile")
        self.add_line_to_file_sudo(line="/swapfile none swap sw 0 0", file_path="/etc/fstab")

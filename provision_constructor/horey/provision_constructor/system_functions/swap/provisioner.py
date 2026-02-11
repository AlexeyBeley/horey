"""
Swap file provisioner.

"""

from pathlib import Path

from horey.common_utils.remoter import Remoter
from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.h_logger import get_logger

logger = get_logger()


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
            **kwargs
    ):
        super().__init__(deployment_dir, force, upgrade, **kwargs)
        self.swap_size_in_gb = swap_size_in_gb
        self.ram_size_in_gb = ram_size_in_gb

        if self.swap_size_in_gb is None and self.ram_size_in_gb:
            self.swap_size_in_gb = self.calc_swap_needed(self.ram_size_in_gb)

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
        # sudo -s
        # echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

    @staticmethod
    def calc_swap_needed(ram_in_gb:int) -> int:
        """
        Less than 2 GB	2x amount of RAM
        2 GB – 8 GB	Equal to the amount of RAM
        8 GB – 64 GB	4 GB to 0.5x RAM

        :param ram_in_gb:
        :return:
        """

        if ram_in_gb < 2:
            return  max(1, ram_in_gb * 2)

        if 2< ram_in_gb < 8:
            return ram_in_gb

        return int(ram_in_gb/2)


    def provision_remote(self, remoter:Remoter):
        """
        :return:
        """

        self.remoter = remoter
        if not self.swap_size_in_gb:
            self.remoter.execute("grep MemTotal /proc/meminfo | awk '{print $2}'")
            ret = self.remoter.execute('')

            try:
                in_kb = int(ret[0][0].strip("\n"))
            except Exception:
                ret = self.remoter.execute("cat /proc/meminfo")
                logger.error(f"SWAP Memory calculation error: {ret=}")
                raise ValueError("Was not able to find instance memory size")

            self.ram_size_in_gb = int(in_kb/1024/1024) + 1
            self.swap_size_in_gb = self.calc_swap_needed(self.ram_size_in_gb)

        try:
            return self.check_provisioned_remote()
        except self.FailedCheckError:
            pass

        remoter.execute("sudo swapoff -a")
        remoter.execute(f"sudo fallocate -l {self.swap_size_in_gb}G /swapfile")
        remoter.execute("sudo chmod 600 /swapfile")
        remoter.execute("sudo mkswap /swapfile")
        remoter.execute("sudo swapon /swapfile")
        return self.add_line_to_file_remote(remoter, line="/swapfile none swap sw 0 0", file_path=Path("/etc/fstab"), sudo=True)

    def check_provisioned_remote(self):
        """
                       total        used        free      shared  buff/cache   available
        Mem:           3.8Gi       1.7Gi       685Mi       3.0Mi       1.4Gi       1.8Gi
        Swap:          8.0Gi       4.0Mi       8.0Gi
        :return:
        """

        # todo: refactor to handle new ssh connection.
        self.remoter.execute("pwd")

        ret = self.remoter.execute("free -h")
        lines = ret[0]
        if not lines[0].strip().startswith("total"):
            raise RuntimeError(f"First's line first word is not 'total': {lines} ")

        for line in lines:
            if line.startswith("Swap:"):
                break
        else:
            raise self.FailedCheckError(f"No line that starts with 'Swap:': {lines} ")

        while "  " in line:
            line = line.replace("  ", " ")

        output_total_size = line.split(" ")[1]
        if not output_total_size.endswith("Gi"):
            raise self.FailedCheckError("Swap is missing")

        total_gigs_configured = int(float(output_total_size[:-2]))
        if total_gigs_configured-1 <= self.swap_size_in_gb <= total_gigs_configured+1:
            return True
        raise self.FailedCheckError(f"Wrong swap size: {self.swap_size_in_gb}")

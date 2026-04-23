"""
Provision ntp service.

"""
import json
import threading
from pathlib import Path

from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.common_utils.bash_executor import BashExecutor
from horey.common_utils.remoter import Remoter
from horey.h_logger import get_logger

logger = get_logger()
BashExecutor.set_logger(logger, override=False)


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """
    Provision service.

    """
    LOCK = threading.Lock()

    def provision_remote(self, remoter: Remoter):
        """
        Provision remotely

        :param remoter:
        :return:
        """

        self.remoter = remoter
        match self.action:
            case "get_blockdevices":
                return self.get_blockdevices_remote()
            case "partition":
                return self.partition_remote()
            case "mount":
                return self.mount_remote()
            case _:
                raise NotImplementedError(self.action)

    def get_blockdevices_remote(self):
        """
        List status

        :return:
        """

        blockdevice = self.kwargs.get("blockdevice")
        blockdevice_path = " "+blockdevice["path"] if blockdevice else ""
        ret = self.remoter.execute(f"sudo lsblk --json --output-all --ascii{blockdevice_path}")
        output = json.loads("".join(ret[0]))
        return output["blockdevices"]

    def partition_remote(self):
        """
        List status

        :return:
        """

        blockdevice = self.kwargs.get("blockdevice")
        blockdevice_path = blockdevice["path"]
        if not blockdevice_path.startswith("/dev/nvme"):
            raise NotImplementedError(f"Only /dev/nvme is supported, got {blockdevice_path}")

        for child in blockdevice.get("children", []):
            mount_point = child.get("mount_point")

            if child.get("fstype") == "swap":
                part_id = child['path'].replace(blockdevice_path + "p", "")
                if not part_id.isdigit():
                    raise RuntimeError(f"Unexpected partition id: {part_id}")

                self.remoter.execute(f"sudo swapoff {child['path']}")
                self.remoter.execute(f"sudo parted {blockdevice_path} rm {part_id} --script")

                continue

            if mount_point:
                if self.force:
                    self.remoter.execute(f"sudo umount {mount_point}")
                else:
                    raise RuntimeError(f"Device {child['name']} is already mounted to {mount_point}")

        self.remoter.execute(f"sudo parted {blockdevice_path} mklabel gpt --script")

        parts = self.kwargs.get("parts", [("ext4", "1MiB", "100%")])
        str_parts = ""
        for part in parts:
            str_parts += f" mkpart primary {part[0]} {part[1]} {part[2]}"
        self.remoter.execute(f"sudo parted {blockdevice_path} --script --" + str_parts)

        for i, part in enumerate(parts):
            partition_path = f"{blockdevice_path}p{i+1}"
            if part[0] == "ext4":
                self.remoter.execute(f"sudo mkfs.ext4 {'-F' if self.force else ''} {partition_path}", self.last_line_validator("done"))
            if part[0] == "linux-swap":
                SystemFunctionFactory.REGISTERED_FUNCTIONS["swap"](self.deployment_dir, True,
                                                                                  self.upgrade,
                                                                                  action="init_partition",
                                                                   partition_path=partition_path).provision_remote(remoter=self.remoter)

        return True

    def mount_remote(self):
        """
        Mount remote

        :return:
        """
        src = self.kwargs.get("src")
        dst = self.kwargs.get("dst")
        chmod = self.kwargs.get("chmod")

        self.remoter.execute(f"sudo mkdir -p {dst}")
        if chmod:
            self.remoter.execute(f"sudo chmod {chmod} {dst}")
        self.remoter.execute(f"sudo mount {src} {dst}")

        line = f"{src} {dst} ext4 defaults 0 2"
        self.add_line_to_file_remote(self.remoter, line=line, file_path=Path("/etc/fstab"), sudo=True)
        return True

    def test_provisioned(self):
        """
        Test if provisioned.

        :return:
        """
        raise NotImplementedError()

    def _provision(self):
        """
        Provision local.

        :return:
        """

        raise NotImplementedError("")

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
            case "format":
                return self.format_remote()
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

    def format_remote(self):
        """
        List status

        :return:
        """

        blockdevice = self.kwargs.get("blockdevice")
        blockdevice_path = blockdevice["path"]
        if blockdevice_path != "/dev/nvme1n1":
            raise NotImplementedError(f"Only /dev/nvme1n1 is supported, got {blockdevice_path}")
        for child in blockdevice.get("children", []):
            if child['mountpoint']:
                if self.force:
                    self.remoter.execute(f"sudo umount {child['mountpoint']}")
                else:
                    raise RuntimeError(f"Device {child['name']} is already mounted to {child['mountpoint']}")

        self.remoter.execute(f"sudo parted {blockdevice_path} mklabel gpt --script")
        self.remoter.execute(f"sudo parted {blockdevice_path} mkpart primary ext4 0% 100% --script")
        self.remoter.execute(f"sudo mkfs.ext4 {'-F' if self.force else ''} {blockdevice_path}p1", self.last_line_validator("done"))
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

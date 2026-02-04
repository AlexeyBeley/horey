"""
Provision ntp service.

"""
import json
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
    System function Provision manager
    """

    def provision_remote(self, remoter: Remoter):
        """
        Provision remotely
        Preparing to unpack influxdb_1.12.2-1_amd64.deb ...

        :param remoter:
        :return:
        """

        self.remoter = remoter

        # needed to handle the Fg SSH hello message
        remoter.execute("pwd")

        match self.action:
            case "harden":
                return self.provision_harden_remote()
            case _:
                raise NotImplementedError(f"{self.action}")

    def provision_harden_remote(self):
        """
        Provision remotely

        :return:
        """

        # xccdf_org.ssgproject.content_rule_package_inetutils-telnet_removed
        ret = self.remoter.execute(f"sudo DEBIAN_FRONTEND=noninteractive apt-get remove -y \"inetutils-telnetd\" || true")
        ret = self.remoter.execute("dpkg -l inetutils-telnetd || true", self.grep_validator("no packages found matching inetutils-telnetd"))
        # check:

        #xccdf_org.ssgproject.content_rule_package_tnftp_removed
        ret = self.remoter.execute("sudo apt-get purge -y tnftp || true")
        ret = self.remoter.execute("sudo apt autoremove -y")
        #ret = self.remoter.execute("dpkg -s tnftp || true", self.grep_validator("no packages found matching tnftp"))


        #xccdf_org.ssgproject.content_rule_package_ftp_removed
        self.remoter.execute("sudo apt-get purge -y vsftpd")
        ret = self.remoter.execute("dpkg -s vsftpd || true", self.grep_validator("package 'vsftpd' is not installed"))


        # xccdf_org.ssgproject.content_rule_kernel_module_jffs2_disabled
        ret= self.remoter.execute('echo "install jffs2 /bin/true" | sudo tee /etc/modprobe.d/jffs2.conf &&'
                                  ' sudo modprobe -r jffs2', self.grep_validator("install jffs2 /bin/true"))

        ret = self.remoter.execute("sudo modprobe jffs2 && lsmod | grep jffs2 || true")
        assert len(ret[0]) == 0


        # xccdf_org.ssgproject.content_rule_kernel_module_hfs_disabled
        ret = self.remoter.execute('echo "install hfs /bin/true" | sudo tee /etc/modprobe.d/hfs.conf &&'
                                   ' sudo modprobe -r hfs', self.grep_validator("install hfs /bin/true"))

        # xccdf_org.ssgproject.content_rule_kernel_module_hfsplus_disabled
        ret = self.remoter.execute('echo "install hfsplus /bin/true" | sudo tee /etc/modprobe.d/hfsplus.conf &&'
                                   ' sudo modprobe -r hfsplus', self.grep_validator("install hfsplus /bin/true"))
        ret = self.remoter.execute("sudo modprobe hfsplus && lsmod | grep hfsplus || true")
        assert len(ret[0]) == 0


        # xccdf_org.ssgproject.content_rule_kernel_module_freevxfs_disabled
        ret= self.remoter.execute('echo "install freevxfs /bin/true" | sudo tee /etc/modprobe.d/freevxfs.conf &&'
                                  ' sudo modprobe -r freevxfs', self.grep_validator("install freevxfs /bin/true"))

        ret = self.remoter.execute("sudo modprobe freevxfs && lsmod | grep freevxfs || true")
        assert len(ret[0]) == 0

        # xccdf_org.ssgproject.content_rule_service_timesyncd_configured
        ret = self.remoter.execute("sudo touch /etc/systemd/timesyncd.conf")
        ret = self.remoter.execute("sudo sed -i 's/^#NTP=/NTP=ntp.ubuntu.com pool.ntp.org /' /etc/systemd/timesyncd.conf &&"
                                   "sudo systemctl enable --now systemd-timesyncd")
        ret = self.remoter.execute("timedatectl show-timesync --all", self.grep_validator("ServerName=pool.ntp.org"))
        return True
import os.path
import pdb
from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import SystemFunctionCommon
from horey.h_logger import get_logger

logger = get_logger()


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    def __init__(self, deployment_dir):
        super().__init__(os.path.dirname(os.path.abspath(__file__)))
        self.deployment_dir = deployment_dir

    def provision(self, force=False):
        if not force:
            if self.test_provisioned():
                return

        self._provision()

        self.test_provisioned()

    def test_provisioned(self):
        self.init_apt_packages()
        return (not self.apt_check_installed("sntp*")) and \
               (not self.apt_check_installed("chrony*")) and \
               self.check_file_provisioned("./timesyncd.conf", "/etc/systemd/timesyncd.conf") and \
               self.check_systemd_service_status(service_name="systemd-timesyncd", min_uptime=20)

    def _provision(self):
        """

        sudo systemctl restart systemd-timedated

        @return:
        """
        self.apt_purge("ntp*")
        self.apt_purge("sntp*")
        self.apt_purge("chrony*")

        ret = self.run_bash("sudo timedatectl set-ntp false")
        logger.info(ret)

        self.provision_file("./timesyncd.conf", "/etc/systemd/timesyncd.conf")

        ret = self.run_bash("sudo timedatectl set-ntp true")
        logger.info(ret)

        ret = self.run_bash("sudo systemctl restart systemd-timedated")
        logger.info(ret)

import os.path
import pdb
from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import SystemFunctionCommon


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    def __init__(self, deployment_dir):
        super().__init__(os.path.dirname(os.path.abspath(__file__)))
        self.deployment_dir = deployment_dir

    def provision(self, force=True):
        if not force:
            if self.test_provisioned():
                return

        self._provision()

    def test_provisioned(self):
        self.init_apt_packages()
        return (not self.apt_check_installed("sntp*")) and \
               (not self.apt_check_installed("chrony*")) and \
               self.check_file_provisioned("./timesyncd.conf", "/etc/systemd/timesyncd.conf")

    def _provision(self):
        pdb.set_trace()
        self.apt_purge("ntp*")
        self.apt_purge("sntp*")
        self.apt_purge("chrony*")

        self.move_file("./timesyncd.conf", "/etc/systemd/timesyncd.conf")

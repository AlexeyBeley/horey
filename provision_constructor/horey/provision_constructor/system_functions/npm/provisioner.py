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
        self.apt_check_installed("nodejs")
        ret = self.run_bash("npm -v")
        pdb.set_trace()

    def _provision(self):
        """
        curl -fsSL https://deb.nodesource.com/setup_14.x | sudo -E bash -
        sudo apt-get install -y nodejs
        curl -L https://www.npmjs.com/install.sh >> install.sh
        sudo chmod +x ./install.sh
        sudo npm_install="6.14.5" ./install.sh

        @return:
        """

        self.run_bash("curl -fsSL https://deb.nodesource.com/setup_14.x | sudo -E bash -")
        self.apt_install("nodejs")
        self.run_bash("curl -L https://www.npmjs.com/install.sh >> install.sh")
        self.run_bash("sudo chmod +x ./install.sh")
        self.run_bash('sudo npm_install="6.14.5" ./install.sh')

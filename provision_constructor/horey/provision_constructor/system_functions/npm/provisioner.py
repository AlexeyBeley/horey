"""
Provision npm
"""
import os.path
from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.common_utils.bash_executor import BashExecutor

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.h_logger import get_logger

logger = get_logger()


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """
    Main class
    """
    def __init__(self, deployment_dir, force, upgrade):
        super().__init__(os.path.dirname(os.path.abspath(__file__)), force, upgrade)
        self.deployment_dir = deployment_dir

    def test_provisioned(self):
        self.init_apt_packages()
        if not self.apt_check_installed("nodejs"):
            return False

        try:
            self.run_bash("npm -v")
            return True
        except BashExecutor.BashError as error_isntance:
            print(error_isntance)
            return False

    def _provision(self):
        """
        curl -fsSL https://deb.nodesource.com/setup_14.x | sudo -E bash -
        sudo apt-get install -y nodejs
        curl -L https://www.npmjs.com/install.sh >> install.sh
        sudo chmod +x ./install.sh
        sudo npm_install="6.14.5" ./install.sh

        @return:
        """

        self.run_bash(
            "curl -fsSL https://deb.nodesource.com/setup_14.x | sudo -E bash -"
        )
        self.apt_install("nodejs")
        self.run_bash("curl -L https://www.npmjs.com/install.sh >> install.sh")
        self.run_bash("sudo chmod +x ./install.sh")
        self.run_bash('sudo npm_install="6.14.5" ./install.sh')

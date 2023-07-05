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

    # pylint: disable=too-many-arguments
    def __init__(self, deployment_dir, force, upgrade, npm_version="8.19.4", nodejs_version="16.20.1"):
        super().__init__(os.path.dirname(os.path.abspath(__file__)), force, upgrade)
        self.deployment_dir = deployment_dir
        self.npm_version = npm_version
        self.nodejs_version = nodejs_version

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
        Provision npm and nodejs
        @return:
        """

        self.run_bash("curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash")

        command = f'NVM_DIR="$HOME/.nvm" source "$NVM_DIR/nvm.sh" && nvm install v{self.nodejs_version}'
        self.run_bash(command)

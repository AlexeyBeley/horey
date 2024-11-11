"""
GIT API module.

"""
import os
from pathlib import Path

from horey.h_logger import get_logger
from horey.health_api.health_api_configuration_policy import HealthAPIConfigurationPolicy
from horey.common_utils.bash_executor import BashExecutor

logger = get_logger()


class HealthAPI:
    """
    API to pip functionality

    """

    REQUIREMENTS = {}

    def __init__(self, configuration: HealthAPIConfigurationPolicy = None):
        self.configuration = configuration
        self.bash_executor = BashExecutor()

    def clone(self):
        """
        Clone from remote to local.

        :return:
        """
        breakpoint()
        base = f'GIT_SSH_COMMAND="ssh -i {self.configuration.ssh_key_file_path} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"'

        os.chdir(Path(self.configuration.directory_path).resolve().parent)
        ret = self.bash_executor.run_bash(f"{base} git clone {self.configuration.remote}")
        return ret

"""
Deployment target machine.

"""

import os.path
from enum import Enum


# pylint: disable=too-many-instance-attributes
class DeploymentTarget:
    """
    Single server deployment
    """
    def __init__(self):
        self.hostame = None
        self.remote_deployment_dir_path = "/tmp/remote_deployer"
        self.deployment_data_dir_name = "deployment_data"

        self.bastion_address = None
        self.bastion_user_name = None
        self.bastion_ssh_key_path = None

        self.deployment_target_ssh_key_path = None
        self.deployment_target_address = None
        self.deployment_target_user_name = None

        self.deployment_step_configuration_file_name = None

        self.deployment_code_provisioning_ended = False
        self.deployment_ended = False

        self.local_deployment_dir_path = "/tmp/remote_deployer"

        self.remote_deployer_infrastructure_provisioning_finished = False
        self.remote_deployer_infrastructure_provisioning_succeeded = None
        self.linux_distro = "ubuntu"
        self.steps = []
        self.status_code = None
        self.status = None

    @property
    def local_deployment_data_dir_path(self):
        """
        Deployment data - values, status and output.
        @return:
        """
        if self.local_deployment_dir_path is None:
            raise ValueError("local_deployment_dir_path was not set")

        return os.path.join(self.local_deployment_dir_path, self.deployment_data_dir_name)

    def add_step(self, step):
        """
        Add deployment step.

        @param step:
        @return:
        """

        self.steps.append(step)

    class StatusCode(Enum):
        """
        Deployment statuses.

        """

        SUCCESS = 0
        FAILURE = 1
        ERROR = 2

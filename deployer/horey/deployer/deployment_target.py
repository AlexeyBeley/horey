"""
Deployment target machine.

"""

import os.path
from enum import Enum
from horey.deployer.deployment_step import DeploymentStep
from horey.deployer.deployment_step_configuration_policy import DeploymentStepConfigurationPolicy


# pylint: disable=too-many-instance-attributes
class DeploymentTarget:
    """
    Single server deployment
    """
    SupportedSSHKeys = ["rsa", "ed25519key"]

    def __init__(self):
        self.hostname = None
        self.remote_deployment_dir_path = "/tmp/remote_deployer"
        self.deployment_data_dir_name = "deployment_data"

        self.bastion_address = None
        self.bastion_user_name = None
        self.bastion_ssh_key_path = None
        self.bastion_ssh_key_type = "rsa"  # or "ed25519key"

        self.deployment_target_ssh_key_path = None
        self.deployment_target_ssh_key_type = "rsa"  # or "ed25519key"
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

    def print(self):
        """
        Pretty print.

        :return:
        """

        str_ret = f"hostname: {self.hostname}\n" \
                  f"deployment_target_address: {self.deployment_target_address}\n" \
                  f"deployment_target_ssh_key_type: {self.deployment_target_ssh_key_type}\n" \
                  f"deployment_target_ssh_key_path: {self.deployment_target_ssh_key_path}"
        print(str_ret)
        return str_ret

    @property
    def local_deployment_data_dir_path(self):
        """
        Deployment data - values, status and output.
        @return:
        """
        if self.local_deployment_dir_path is None:
            raise ValueError("local_deployment_dir_path was not set")

        return os.path.join(
            self.local_deployment_dir_path, self.deployment_data_dir_name
        )

    def add_step(self, step):
        """
        Add deployment step.

        @param step:
        @return:
        """

        self.steps.append(step)

    def append_raw_step(self, script_name):
        """


        :param script_name:
        :return:
        """

        step_configuration = DeploymentStepConfigurationPolicy(script_name)
        step_configuration.deployment_dir_path = self.remote_deployment_dir_path
        step_configuration.script_name = script_name
        os.makedirs(self.local_deployment_data_dir_path, exist_ok=True)
        step_configuration.generate_configuration_file(os.path.join(self.local_deployment_data_dir_path,
                                                                    step_configuration.script_configuration_file_name))
        step = DeploymentStep(step_configuration)
        self.add_step(step)

    class StatusCode(Enum):
        """
        Deployment statuses.

        """

        SUCCESS = 0
        FAILURE = 1
        ERROR = 2

    class SSHKeyTypes(Enum):
        """
        Possible SSH Keys

        """

        RSA = "rsa"
        ED25519 = "ed25519key"

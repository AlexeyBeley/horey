"""
Deployment target machine.

"""

import os.path
from enum import Enum
from pathlib import Path
from typing import List

from horey.deployer.deployment_step import DeploymentStep
from horey.deployer.remote_deployment_step import RemoteDeploymentStep
from horey.deployer.deployment_step_configuration_policy import DeploymentStepConfigurationPolicy

# pylint: disable=too-many-instance-attributes
class DeploymentTarget:
    """
    Single server deployment
    """
    SupportedSSHKeys = ["rsa", "ed25519key"]

    def __init__(self):
        self.hostname = None
        self.remote_deployment_dir_path = Path("/tmp/remote_deployer")
        self.deployment_data_dir_name = "deployment_data"

        self.bastion_chain: List[DeploymentTarget.BastionChainLink] = []

        self.deployment_target_ssh_key_path = None
        self.deployment_target_address = None
        self.deployment_target_user_name = "ubuntu"

        self.deployment_step_configuration_file_name = None

        self.deployment_code_provisioning_ended = False
        self.deployment_ended = False

        self.local_deployment_dir_path = Path("/tmp/remote_deployer")

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
                  f"deployment_target_ssh_key_path: {self.deployment_target_ssh_key_path}"
        print(str_ret)
        return str_ret

    def copy(self):
        """
        Make a self copy

        :return: 
        """

        # todo:  implement the same for bastion_chain

        ret = DeploymentTarget()
        for key, value in self.__dict__.items():
            setattr(ret, key, value)
        return ret


    @property
    def local_deployment_data_dir_path(self):
        """
        Deployment data - values, status and output.
        @return:
        """
        if self.local_deployment_dir_path is None:
            raise ValueError("local_deployment_dir_path was not set")

        dir_path = self.local_deployment_dir_path / self.deployment_data_dir_name
        os.makedirs(dir_path, exist_ok=True)
        return dir_path

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

    def append_remote_step(self, name, entrypoint):
        """
        Add remote step

        :param name:
        :param entrypoint:
        :return:
        """

        step = RemoteDeploymentStep(name, entrypoint)
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

    def generate_step(self, step_script_path: str):
        """
        Generate step.

        :param step_script_path:
        :return:
        """

        if "/" in step_script_path:
            raise NotImplementedError(f"remove / from {step_script_path}")
        step_configuration = DeploymentStepConfigurationPolicy(step_script_path.replace(".sh", ""))
        step_configuration.local_deployment_dir_path = self.local_deployment_dir_path
        step_configuration.script_name = step_script_path

        return DeploymentStep(step_configuration)

    class BastionChainLink:
        """
        Single bastion link in a chain

        """

        def __init__(self, address, ssh_key_path, user_name="ubuntu"):
            """

            :param address:
            :param user_name:
            :param ssh_key_path:
            """

            self.address = address
            self.user_name = user_name
            self.ssh_key_path = ssh_key_path

import os.path
import pdb


class MachineDeploymentBlock:
    """
    Single server deployment
    """
    def __init__(self):
        self.remote_deployment_dir_path = None
        self.deployment_data_dir_name = None

        self.bastion_address = None
        self.bastion_user_name = None
        self.bastion_ssh_key_path = None

        self.deployment_target_ssh_key_path = None
        self.deployment_target_address = None
        self.deployment_target_user_name = None

        self.deployment_step_configuration_file_name = None

        self.deployment_code_provisioning_ended = False
        self.deployment_ended = False

        self.application_infrastructure_provision_step = None
        self.application_deploy_step = None
        self.local_deployment_dir_path = None

        self.remote_deployer_infrastructure_provisioning_finished = False
        self.remote_deployer_infrastructure_provisioning_succeeded = None

    @property
    def local_deployment_data_dir_path(self):
        if self.local_deployment_dir_path is None:
            raise ValueError("local_deployment_dir_path was not set")

        return os.path.join(self.local_deployment_dir_path, self.deployment_data_dir_name)

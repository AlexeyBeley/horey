import os.path
import pdb


class MachineDeploymentBlock:
    """
    Single server deployment
    """
    def __init__(self):
        self.local_deployment_dir_path = None
        self.remote_deployment_dir_path = None
        self.remote_scripts_dir_name = None
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

        self.string_replacements = None
        self.replacements_base_dir_path = None

    @property
    def local_deployment_remote_scripts_dir_path(self):
        if self.local_deployment_dir_path is None:
            raise ValueError()
        if self.remote_scripts_dir_name is None:
            raise ValueError()

        return os.path.join(self.local_deployment_dir_path, self.remote_scripts_dir_name)

    @property
    def local_deployment_data_dir_path(self):
        if self.local_deployment_remote_scripts_dir_path is None:
            raise ValueError()

        return os.path.join(self.local_deployment_remote_scripts_dir_path, self.deployment_data_dir_name)

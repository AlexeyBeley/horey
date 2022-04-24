import os
import pdb
from enum import Enum
from horey.deployer.deployment_step_configuration_policy import DeploymentStepConfigurationPolicy


class DeploymentStep:
    """
    Single server deployment step
    """
    def __init__(self, configuration):
        if not isinstance(configuration, DeploymentStepConfigurationPolicy):
            raise ValueError(f"configuration is not instance of DeploymentStepConfigurationPolicy: {configuration}")

        if configuration.name is None:
            raise RuntimeError("Step configuration name was not set")

        self.configuration = configuration
        self.status = None
        self.status_code = None #  "success"/"failure"/"error"
        self.output = None

    def update_finish_status(self, local_deployment_data_dir_path):
        try:
            with open(os.path.join(local_deployment_data_dir_path, self.configuration.finish_status_file_name)) as file_handler:
                status = file_handler.read()
        except FileNotFoundError:
            self.status_code = DeploymentStep.StatusCode.ERROR
            self.status = f"File '{os.path.join(local_deployment_data_dir_path, self.configuration.finish_status_file_name)}' not found"
            return

        self.status = status
        try:
            self.status_code = DeploymentStep.StatusCode.__members__[status]
        except KeyError:
            self.status_code = DeploymentStep.StatusCode.ERROR

    def update_output(self, local_deployment_data_dir_path):
        with open(os.path.join(local_deployment_data_dir_path, self.configuration.output_file_name)) as file_handler:
            self.output = file_handler.read()

    class StatusCode(Enum):
        SUCCESS = 0
        FAILURE = 1
        ERROR = 2

"""
Deployment step data class

"""

from enum import Enum
from horey.deployer.deployment_step_configuration_policy import (
    DeploymentStepConfigurationPolicy,
)


class DeploymentStep:
    """
    Single server deployment step
    """

    def __init__(self, configuration: DeploymentStepConfigurationPolicy):
        if not isinstance(configuration, DeploymentStepConfigurationPolicy):
            raise ValueError(
                f"configuration is not instance of DeploymentStepConfigurationPolicy: {configuration}"
            )

        if configuration.name is None:
            raise RuntimeError("Step configuration name was not set")

        self.name = configuration.name
        self.sleep_time = configuration.sleep_time
        self.retry_attempts = configuration.retry_attempts
        self.configuration = configuration
        self.status = None
        self.status_code = None  # "success"/"failure"/"error"
        self.output = None

    def update_finish_status(self):
        """
        Update self status from the status file.

        :return:
        """

        try:
            with open(
                    self.configuration.local_deployment_dir_path /
                    self.configuration.data_dir_name /
                        self.configuration.finish_status_file_name,
                    encoding="utf-8"
            ) as file_handler:
                status = file_handler.read()
        except FileNotFoundError:
            self.status_code = DeploymentStep.StatusCode.ERROR
            self.status = f"File '{self.configuration.local_deployment_dir_path / self.configuration.data_dir_name / self.configuration.finish_status_file_name}' not found"
            return

        self.status = status
        try:
            self.status_code = DeploymentStep.StatusCode.__members__[status]
        except KeyError:
            self.status_code = DeploymentStep.StatusCode.ERROR

    def update_output(self):
        """
        Update self output from file

        :return:
        """

        with open(
                self.configuration.local_deployment_dir_path /
                self.configuration.data_dir_name /
                self.configuration.output_file_name,
                encoding="utf-8"
        ) as file_handler:
            self.output = file_handler.read()

    class StatusCode(Enum):
        """
        Possible status codes

        """

        SUCCESS = 0
        FAILURE = 1
        ERROR = 2

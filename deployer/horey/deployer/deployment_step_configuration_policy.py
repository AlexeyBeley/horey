"""
Step configuration.

"""

import pathlib
from pathlib import Path
from uuid import uuid4
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


# pylint: disable= missing-function-docstring
class DeploymentStepConfigurationPolicy(ConfigurationPolicy):
    """
    Main class
    """

    def __init__(self, name):
        super().__init__()
        self._name = name
        self._local_deployment_dir_path = None
        self._script_name = None
        self._uuid = None
        self._data_dir_name = None
        self._remote_script_file_path = None
        self._retry_attempts = None
        self._sleep_time = None
        self._remote_deployment_dir_path = None

    @property
    def sleep_time(self):
        if self._sleep_time is None:
            self._sleep_time = 60
        return self._sleep_time

    @sleep_time.setter
    def sleep_time(self, value):
        self._sleep_time = value

    @property
    def retry_attempts(self):
        if self._retry_attempts is None:
            self._retry_attempts = 40
        return self._retry_attempts

    @retry_attempts.setter
    def retry_attempts(self, value):
        self._retry_attempts = value

    @property
    def name(self):
        if self._name is None:
            return "deployment_data"
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def data_dir_name(self):
        if self._data_dir_name is None:
            return "deployment_data"
        return self._data_dir_name

    @data_dir_name.setter
    def data_dir_name(self, value):
        self._data_dir_name = value

    @property
    def uuid(self):
        if self._uuid is None:
            self._uuid = str(uuid4())
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        if self._uuid is not None:
            raise self.StaticValueError(f"uuid: {self._uuid}")
        self._uuid = value

    @property
    def script_name(self):
        self.check_defined()
        return self._script_name

    @script_name.setter
    def script_name(self, value):
        if not isinstance(value, str):
            raise ValueError(f"script_name must be str, received: '{type(value)}'")
        self._script_name = value

    @property
    def local_deployment_dir_path(self):
        if self._local_deployment_dir_path is None:
            return Path("/tmp/remote_deployer")
        return self._local_deployment_dir_path

    @local_deployment_dir_path.setter
    def local_deployment_dir_path(self, value):
        if not isinstance(value, pathlib.Path):
            raise ValueError(
                f"local_deployment_dir_path must be pathlib.Path, received: '{type(value)}'"
            )
        self._local_deployment_dir_path= value

    @property
    def finish_status_file_name(self):
        return (
            f"{self.uuid}_finish_status"
        )

    @finish_status_file_name.setter
    def finish_status_file_name(self, _):
        raise self.StaticValueError()

    @property
    def output_file_name(self):
        return f"{self.uuid}_output"

    @output_file_name.setter
    def output_file_name(self, value):
        raise self.StaticValueError("output_file_name")

    @property
    def script_configuration_file_name(self):
        return f"{self.uuid}_configuration_values"

    @script_configuration_file_name.setter
    def script_configuration_file_name(self, value):
        raise self.StaticValueError("Don't touch it!")

    @property
    def remote_script_file_path(self):
        if self._remote_script_file_path is not None:
            return self._remote_script_file_path

        if self.script_name is None:
            raise self.UndefinedValueError("script_name")
        return self.remote_deployment_dir_path / self.script_name

    @remote_script_file_path.setter
    def remote_script_file_path(self, value):
        self._remote_script_file_path = value

    @property
    def remote_deployment_dir_path(self):
        if self._remote_deployment_dir_path is None:
            return Path("/tmp/remote_deployer")
        return self._remote_deployment_dir_path

    @remote_deployment_dir_path.setter
    def remote_deployment_dir_path(self, value):
        self._remote_deployment_dir_path = value

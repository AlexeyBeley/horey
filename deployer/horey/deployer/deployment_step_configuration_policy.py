"""
Step configuration.

"""

import os
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
        self._deployment_dir_path = None
        self._script_name = None
        self._finish_status_file_path = None
        self._output_file_path = None
        self._script_configuration_file_name = None
        self._uuid = None
        self._step_data_dir_name = None
        self._remote_script_file_path = None

    @property
    def name(self):
        if self._name is None:
            return "deployment_data"
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def step_data_dir_name(self):
        if self._step_data_dir_name is None:
            return "deployment_data"
        return self._step_data_dir_name

    @step_data_dir_name.setter
    def step_data_dir_name(self, value):
        self._step_data_dir_name = value

    @property
    def uuid(self):
        if self._uuid is None:
            self._uuid = str(uuid4())
        return self._uuid

    @uuid.setter
    def uuid(self, _):
        raise self.StaticValueError()

    @property
    def script_name(self):
        if self._script_name is None:
            raise ValueError("script_name not set")
        return self._script_name

    @script_name.setter
    def script_name(self, value):
        if not isinstance(value, str):
            raise ValueError(f"script_name must be str, received: '{type(value)}'")
        self._script_name = value

    @property
    def deployment_dir_path(self):
        if self._deployment_dir_path is None:
            return "/tmp"
        return self._deployment_dir_path

    @deployment_dir_path.setter
    def deployment_dir_path(self, value):
        if not isinstance(value, str):
            raise ValueError(f"deployment_dir_path must be str, received: '{type(value)}'")
        self._deployment_dir_path = value

    @property
    def finish_status_file_name(self):
        return f"{self.get_script_file_name_without_extension_with_uuid()}_finish_status"

    @finish_status_file_name.setter
    def finish_status_file_name(self, _):
        raise self.StaticValueError()

    @property
    def output_file_name(self):
        return f"{self.get_script_file_name_without_extension_with_uuid()}_output"

    @output_file_name.setter
    def output_file_name(self, _):
        raise self.StaticValueError()

    @property
    def finish_status_file_path(self):
        if self._finish_status_file_path is None:
            return f"{self.get_step_components_base_filename_path()}_finish_status"

        return self._finish_status_file_path

    @finish_status_file_path.setter
    def finish_status_file_path(self, value):
        if not isinstance(value, str):
            raise ValueError(f"finish_status_file_path must be str, received: '{type(value)}'")
        self._finish_status_file_path = value

    @property
    def output_file_path(self):
        if self._output_file_path is None:
            return f"{self.get_step_components_base_filename_path()}_output"

        return self._output_file_path

    @output_file_path.setter
    def output_file_path(self, value):
        if not isinstance(value, str):
            raise ValueError(f"output_file_path must be str, received: '{type(value)}'")
        self._output_file_path = value

    @property
    def step_data_dir_path(self):
        if self.deployment_dir_path is None or self.step_data_dir_name is None:
            raise ValueError()

        return os.path.join(self.deployment_dir_path, self.step_data_dir_name)

    @step_data_dir_path.setter
    def step_data_dir_path(self, _):
        raise self.StaticValueError()

    def get_step_components_base_filename_path(self):
        """
        This is the base file path+name+uid use to generate output, status and configuration files
        """
        return os.path.join(self.step_data_dir_path, self.get_script_file_name_without_extension_with_uuid())

    def get_script_file_name_without_extension_with_uuid(self):
        file_name_without_extension = os.path.splitext(self.script_name)[0]
        return f"{file_name_without_extension}_{self.uuid}"

    @property
    def script_configuration_file_name(self):
        if self._script_configuration_file_name is None:
            return f"{self.get_script_file_name_without_extension_with_uuid()}_configuration_values"
        return self._script_configuration_file_name

    @script_configuration_file_name.setter
    def script_configuration_file_name(self, value):
        if not isinstance(value, str):
            raise ValueError(f"script_configuration_file_name must be str, received: '{type(value)}'")
        self._script_configuration_file_name = value

    @property
    def script_configuration_file_path(self):
        if self.script_configuration_file_name is None:
            raise ValueError()

        if self.step_data_dir_path is None:
            raise ValueError()

        return os.path.join(self.step_data_dir_path, self.script_configuration_file_name)

    @script_configuration_file_path.setter
    def script_configuration_file_path(self, _):
        raise self.StaticValueError()

    @property
    def remote_script_file_path(self):
        if self._remote_script_file_path is not None:
            return self._remote_script_file_path

        if self.script_name is None:
            raise ValueError()
        return os.path.join(self.deployment_dir_path, self.script_name)

    @remote_script_file_path.setter
    def remote_script_file_path(self, value):
        self._remote_script_file_path = value

import os
from uuid import uuid4
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class MachineDeploymentStepConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._scripts_dir_path = None
        self._script_name = None
        self._finish_status_file_path = None
        self._output_file_path = None
        self._script_configuration_file_full_path = None
        self._uuid = None

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
        if self._script_name is None :
            raise ValueError("script_name not set")
        return self._script_name

    @script_name.setter
    def script_name(self, value):
        if not isinstance(value, str):
            raise ValueError(f"script_name must be str, received: '{type(value)}'")
        self._script_name = value

    @property
    def scripts_dir_path(self):
        if self._scripts_dir_path is None :
            raise ValueError("scripts_dir_path not set")
        return self._scripts_dir_path

    @scripts_dir_path.setter
    def scripts_dir_path(self, value):
        if not isinstance(value, str):
            raise ValueError(f"scripts_dir_path must be str, received: '{type(value)}'")
        self._scripts_dir_path = value

    @property
    def finish_status_file_path(self):
        if self._finish_status_file_path is None:
            return f"{self.get_file_path_without_extension_with_uuid()}_finish_status"

        return self._finish_status_file_path

    @finish_status_file_path.setter
    def finish_status_file_path(self, value):
        if not isinstance(value, str):
            raise ValueError(f"finish_status_file_path must be str, received: '{type(value)}'")
        self._finish_status_file_path = value

    @property
    def output_file_path(self):
        if self._output_file_path is None:
            return f"{self.get_file_path_without_extension_with_uuid()}_output"

        return self._output_file_path

    @output_file_path.setter
    def output_file_path(self, value):
        if not isinstance(value, str):
            raise ValueError(f"output_file_path must be str, received: '{type(value)}'")
        self._output_file_path = value

    @property
    def script_configuration_file_full_path(self):
        if self._script_configuration_file_full_path is None:
            return f"{self.get_file_path_without_extension_with_uuid()}_configuration"

        return self._script_configuration_file_full_path

    @script_configuration_file_full_path.setter
    def script_configuration_file_full_path(self, value):
        if not isinstance(value, str):
            raise ValueError(f"script_configuration_file_full_path must be str, received: '{type(value)}'")
        self._script_configuration_file_full_path = value

    def get_file_path_without_extension_with_uuid(self):
        file_path_without_extension = os.path.splitext(os.path.join(self.scripts_dir_path, self.script_name))[0]
        return f"{file_path_without_extension}_{self.uuid}"

    @property
    def script_configuration_file_name(self):
        return os.path.basename(self.script_configuration_file_full_path)

    @script_configuration_file_name.setter
    def script_configuration_file_name(self, _):
        raise self.StaticValueError()

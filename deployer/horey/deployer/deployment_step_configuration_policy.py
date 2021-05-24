import os
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class DeploymentStepConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._scripts_dir_path = None
        self._script_name = None
        self._finish_status_file_path = None
        self._output_file_path = None

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
            return f"{self.get_file_path_without_extension()}_finish_status"

        return self._finish_status_file_path

    @finish_status_file_path.setter
    def finish_status_file_path(self, value):
        if not isinstance(value, str):
            raise ValueError(f"finish_status_file_path must be str, received: '{type(value)}'")
        self._finish_status_file_path = value

    @property
    def output_file_path(self):
        if self._output_file_path is None:
            return f"{self.get_file_path_without_extension()}_output"

        return self._output_file_path

    @output_file_path.setter
    def output_file_path(self, value):
        if not isinstance(value, str):
            raise ValueError(f"output_file_path must be str, received: '{type(value)}'")
        self._output_file_path = value

    def get_file_path_without_extension(self):
        return os.path.splitext(os.path.join(self.scripts_dir_path, self.script_name))[0]
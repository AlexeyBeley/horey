"""
Git API config.

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy


# pylint: disable = missing-function-docstring
class GitAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._remote = None
        self._ssh_key_file_path = None
        self._directory_path = None
        self._git_directory_path = None
        self._main_branch = None

    @property
    def main_branch(self):
        return self._main_branch

    @main_branch.setter
    def main_branch(self, value):
        self._main_branch = value

    @property
    def git_directory_path(self):
        self.check_defined()
        return self._git_directory_path

    @git_directory_path.setter
    @ConfigurationPolicy.directory_property(mkdir=True, exist_ok=True)
    def git_directory_path(self, value):
        self._git_directory_path = value

    @property
    def directory_path(self):
        if self._directory_path is None:
            dir_name = self.remote.strip(".git").split("/")[-1]
            if not dir_name or any(symbol in dir_name for symbol in [".", " "]):
                raise RuntimeError(f"Invalid: '{dir_name=}' generated from remote: {self.remote}")
            self._directory_path = self.git_directory_path / dir_name

        return self._directory_path

    @directory_path.setter
    @ConfigurationPolicy.directory_property(mkdir=True, exist_ok=True)
    def directory_path(self, value):
        self._directory_path = value

    @property
    def remote(self):
        self.check_defined()
        return self._remote

    @remote.setter
    def remote(self, value):
        self._remote = value

    @property
    def ssh_key_file_path(self):
        return self._ssh_key_file_path

    @ssh_key_file_path.setter
    def ssh_key_file_path(self, value):
        self._ssh_key_file_path = value

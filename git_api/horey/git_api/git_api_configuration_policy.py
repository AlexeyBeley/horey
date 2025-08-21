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
        self._branch_name = None

    @property
    def branch_name(self):
        return self._branch_name

    @branch_name.setter
    def branch_name(self, value):
        self._branch_name = value

    @property
    def git_directory_path(self):
        return self._git_directory_path

    @git_directory_path.setter
    def git_directory_path(self, value):
        self._git_directory_path = value

    @property
    def directory_path(self):
        return self._directory_path

    @directory_path.setter
    def directory_path(self, value):
        self._directory_path = value

    @property
    def remote(self):
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

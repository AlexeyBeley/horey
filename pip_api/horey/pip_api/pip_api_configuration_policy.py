"""
Pip API config.

"""
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class PipAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._multi_package_repositories = None
        self._venv_dir_path = None
        self._git_ssh_key_file_path = None
        self._system_site_packages = None

    @property
    def multi_package_repositories(self):
        """
        Repos file paths

        @return:
        """

        return self._multi_package_repositories

    @multi_package_repositories.setter
    def multi_package_repositories(self, value):
        self._multi_package_repositories = value

    @property
    def venv_dir_path(self):
        """
        venv directory paths

        @return:
        """

        return self._venv_dir_path

    @venv_dir_path.setter
    def venv_dir_path(self, value):
        self._venv_dir_path = value

    @property
    def git_ssh_key_file_path(self):
        """
        venv directory paths

        @return:
        """

        return self._git_ssh_key_file_path

    @git_ssh_key_file_path.setter
    def git_ssh_key_file_path(self, value):
        self._git_ssh_key_file_path = value

    @property
    def system_site_packages(self):
        if self._system_site_packages is None:
            return True
        return self._system_site_packages

    @system_site_packages.setter
    def system_site_packages(self, value):
        self._system_site_packages = value

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
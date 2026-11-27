"""
GitHub UI configuration policy
"""

from pathlib import Path

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

#pylint: disable= missing-function-docstring


class GithubUIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class.

    """

    def __init__(self):
        super().__init__()
        self._github_api_configuration_file_path = None
        self._postgres_api_configuration_file_path = None

    @property
    def github_api_configuration_file_path(self):
        """
        Path to the GithubAPIConfigurationPolicy file (.json or .py): pat, owner.

        :return:
        """

        return self._github_api_configuration_file_path

    @github_api_configuration_file_path.setter
    def github_api_configuration_file_path(self, value):
        if value is not None and not isinstance(value, (str, Path)):
            raise ValueError(
                f"github_api_configuration_file_path must be str, Path or None, received {value} of type: {type(value)}"
            )
        self._github_api_configuration_file_path = value

    @property
    def postgres_api_configuration_file_path(self):
        """
        Path to the PostgresAPIConfigurationPolicy file (.json or .py): host, port, database, username, password.

        :return:
        """

        return self._postgres_api_configuration_file_path

    @postgres_api_configuration_file_path.setter
    def postgres_api_configuration_file_path(self, value):
        if value is not None and not isinstance(value, (str, Path)):
            raise ValueError(
                f"postgres_api_configuration_file_path must be str, Path or None, received {value} of type: {type(value)}"
            )
        self._postgres_api_configuration_file_path = value

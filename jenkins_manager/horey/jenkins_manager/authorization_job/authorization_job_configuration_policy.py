"""
Jenkins job, which authorizes user for a specific job with specific params.

"""
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class AuthorizationJobConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """
    def __init__(self):
        super().__init__()
        self._authorization_map_file_path = None

    @property
    def authorization_map_file_path(self):
        """
        Json file path.

        @return:
        """

        return self._authorization_map_file_path

    @authorization_map_file_path.setter
    def authorization_map_file_path(self, value):
        self._authorization_map_file_path = value

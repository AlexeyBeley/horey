"""
Alert system configuration policy.

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable=missing-function-docstring


class AWSCleanerConfigurationPolicy(ConfigurationPolicy):
    """
    Main class.

    """

    def __init__(self):
        super().__init__()
        self._clean_route_53 = None
        self._aws_api_account_name = None
        self._managed_accounts_file_path = None

    @property
    def managed_accounts_file_path(self):
        return self._managed_accounts_file_path

    @managed_accounts_file_path.setter
    def managed_accounts_file_path(self, value):
        self._managed_accounts_file_path = value

    @property
    def aws_api_account_name(self):
        return self._aws_api_account_name

    @aws_api_account_name.setter
    def aws_api_account_name(self, value):
        self._aws_api_account_name = value

    @property
    def clean_route_53(self):
        if self._clean_route_53 is None:
            self._clean_route_53 = True
        return self._clean_route_53

    @clean_route_53.setter
    def clean_route_53(self, value):
        if not isinstance(value, bool):
            raise ValueError()
        self._clean_route_53 = value

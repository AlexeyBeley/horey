"""
Alert system configuration policy.

"""
import os
from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable=missing-function-docstring, too-many-instance-attributes

class AWSAccessManagerConfigurationPolicy(ConfigurationPolicy):
    """
    Main class.

    """

    def __init__(self):
        super().__init__()
        self._cache_dir = None
        self._aws_api_accounts = None
        self._managed_accounts_file_path = None


    @property
    def managed_accounts_file_path(self):
        return self._managed_accounts_file_path

    @managed_accounts_file_path.setter
    def managed_accounts_file_path(self, value):
        self._managed_accounts_file_path = value

    @property
    def aws_api_accounts(self):
        return self._aws_api_accounts

    @aws_api_accounts.setter
    def aws_api_accounts(self, value):
        self._aws_api_accounts = value

    @property
    def cache_dir(self):
        return self._cache_dir

    @cache_dir.setter
    def cache_dir(self, value):
        if not isinstance(value, str):
            raise ValueError()
        self._cache_dir = value
        if not os.path.exists(value):
            os.makedirs(value, exist_ok=True)

    @property
    def user_reports_dir_path(self):
        ret = os.path.join(self.cache_dir, "user_reports")
        os.makedirs(ret, exist_ok=True)
        return ret

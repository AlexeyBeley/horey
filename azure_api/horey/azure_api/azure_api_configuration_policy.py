import os
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class AzureAPIConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._azure_api_regions = None
        self._accounts_file = None
        self._azure_account = None
        self._azure_api_cache_dir = None
        self._azure_api_cleanup_cache_dir = None

        self._azure_api_virtual_machine_cache_dir = None
        self._azure_api_resource_groups_cache_dir = None

    @property
    def azure_api_regions(self):
        if self._azure_api_regions is None:
            raise ValueError("azure_api_regions were not set")
        return self._azure_api_regions

    @azure_api_regions.setter
    def azure_api_regions(self, value):
        if not isinstance(value, list):
            raise ValueError(f"azure_api_regions must be a list received {value} of type: {type(value)}")

        self._azure_api_regions = value

    @property
    def azure_account(self):
        if self._azure_account is None:
            raise ValueError("azure_account was not set")
        return self._azure_account

    @azure_account.setter
    def azure_account(self, value):
        if not isinstance(value, str):
            raise ValueError(f"azure_account must be a string received {value} of type: {type(value)}")

        self._azure_account = value

    @property
    def azure_api_cache_dir(self):
        if self._azure_api_cache_dir is None:
            raise ValueError("azure_api_cache_dir was not set")
        return self._azure_api_cache_dir

    @azure_api_cache_dir.setter
    def azure_api_cache_dir(self, value):
        self._azure_api_cache_dir = value
        os.makedirs(self._azure_api_cache_dir, exist_ok=True)

    # region virtual_machine

    @property
    def azure_api_virtual_machine_cache_dir(self):
        if self._azure_api_virtual_machine_cache_dir is None:
            self._azure_api_virtual_machine_cache_dir = os.path.join(self.azure_api_cache_dir, self.azure_account, "vm")
            os.makedirs(self._azure_api_virtual_machine_cache_dir, exist_ok=True)
        return self._azure_api_virtual_machine_cache_dir

    @azure_api_virtual_machine_cache_dir.setter
    def azure_api_virtual_machine_cache_dir(self, value):
        raise ValueError(value)
    
    @property
    def azure_api_virtual_machines_cache_file(self):
        return os.path.join(self.azure_api_virtual_machine_cache_dir, "virtual_machines.json")

    @azure_api_virtual_machines_cache_file.setter
    def azure_api_virtual_machines_cache_file(self, value):
        raise ValueError(value)

    # endregion
    
    # region resource_groups

    @property
    def azure_api_resource_groups_cache_dir(self):
        if self._azure_api_resource_groups_cache_dir is None:
            self._azure_api_resource_groups_cache_dir = os.path.join(self.azure_api_cache_dir, self.azure_account,
                                                                     "resource_groups")
            os.makedirs(self._azure_api_resource_groups_cache_dir, exist_ok=True)
        return self._azure_api_resource_groups_cache_dir

    @azure_api_resource_groups_cache_dir.setter
    def azure_api_resource_groups_cache_dir(self, value):
        raise ValueError(value)

    @property
    def azure_api_resource_groups_cache_file(self):
        return os.path.join(self.azure_api_resource_groups_cache_dir, "resource_groups.json")

    @azure_api_resource_groups_cache_file.setter
    def azure_api_resource_groups_cache_file(self, value):
        raise ValueError(value)

    # endregion
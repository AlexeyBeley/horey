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

        self._azure_api_disks_cache_dir = None
        self._azure_api_load_balancers_cache_dir = None
        self._azure_api_nat_gateways_cache_dir = None
        self._azure_api_network_interfaces_cache_dir = None
        self._azure_api_public_ip_addresses_cache_dir = None
        self._azure_api_network_security_groups_cache_dir = None
        self._azure_api_ssh_keys_cache_dir = None
        self._azure_api_virtual_networks_cache_dir = None

    @property
    def azure_api_regions(self):
        if self._azure_api_regions is None:
            raise ValueError("azure_api_regions were not set")
        return self._azure_api_regions

    @azure_api_regions.setter
    def azure_api_regions(self, value):
        if not isinstance(value, list):
            raise ValueError(
                f"azure_api_regions must be a list received {value} of type: {type(value)}"
            )

        self._azure_api_regions = value

    @property
    def accounts_file(self):
        return self._accounts_file

    @accounts_file.setter
    def accounts_file(self, value):
        self._accounts_file = value

    @property
    def azure_account(self):
        if self._azure_account is None:
            raise ValueError("azure_account was not set")
        return self._azure_account

    @azure_account.setter
    def azure_account(self, value):
        if not isinstance(value, str):
            raise ValueError(
                f"azure_account must be a string received {value} of type: {type(value)}"
            )

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
            self._azure_api_virtual_machine_cache_dir = os.path.join(
                self.azure_api_cache_dir, self.azure_account, "virtual_machines"
            )
            os.makedirs(self._azure_api_virtual_machine_cache_dir, exist_ok=True)
        return self._azure_api_virtual_machine_cache_dir

    @azure_api_virtual_machine_cache_dir.setter
    def azure_api_virtual_machine_cache_dir(self, value):
        raise ValueError(value)

    @property
    def azure_api_virtual_machines_cache_file(self):
        return os.path.join(
            self.azure_api_virtual_machine_cache_dir, "virtual_machines.json"
        )

    @azure_api_virtual_machines_cache_file.setter
    def azure_api_virtual_machines_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region resource_groups

    @property
    def azure_api_resource_groups_cache_dir(self):
        if self._azure_api_resource_groups_cache_dir is None:
            self._azure_api_resource_groups_cache_dir = os.path.join(
                self.azure_api_cache_dir, self.azure_account, "resource_groups"
            )
            os.makedirs(self._azure_api_resource_groups_cache_dir, exist_ok=True)
        return self._azure_api_resource_groups_cache_dir

    @azure_api_resource_groups_cache_dir.setter
    def azure_api_resource_groups_cache_dir(self, value):
        raise ValueError(value)

    @property
    def azure_api_resource_groups_cache_file(self):
        return os.path.join(
            self.azure_api_resource_groups_cache_dir, "resource_groups.json"
        )

    @azure_api_resource_groups_cache_file.setter
    def azure_api_resource_groups_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region disks
    @property
    def azure_api_disks_cache_dir(self):
        if self._azure_api_disks_cache_dir is None:
            self._azure_api_disks_cache_dir = os.path.join(
                self.azure_api_cache_dir, self.azure_account, "disks"
            )
            os.makedirs(self._azure_api_disks_cache_dir, exist_ok=True)
        return self._azure_api_disks_cache_dir

    @azure_api_disks_cache_dir.setter
    def azure_api_disks_cache_dir(self, value):
        raise ValueError(value)

    @property
    def azure_api_disks_cache_file(self):
        return os.path.join(self.azure_api_disks_cache_dir, "disks.json")

    @azure_api_disks_cache_file.setter
    def azure_api_disks_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region load_balancers
    @property
    def azure_api_load_balancers_cache_dir(self):
        if self._azure_api_load_balancers_cache_dir is None:
            self._azure_api_load_balancers_cache_dir = os.path.join(
                self.azure_api_cache_dir, self.azure_account, "load_balancers"
            )
            os.makedirs(self._azure_api_load_balancers_cache_dir, exist_ok=True)
        return self._azure_api_load_balancers_cache_dir

    @azure_api_load_balancers_cache_dir.setter
    def azure_api_load_balancers_cache_dir(self, value):
        raise ValueError(value)

    @property
    def azure_api_load_balancers_cache_file(self):
        return os.path.join(
            self.azure_api_load_balancers_cache_dir, "load_balancers.json"
        )

    @azure_api_load_balancers_cache_file.setter
    def azure_api_load_balancers_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region nat_gateways
    @property
    def azure_api_nat_gateways_cache_dir(self):
        if self._azure_api_nat_gateways_cache_dir is None:
            self._azure_api_nat_gateways_cache_dir = os.path.join(
                self.azure_api_cache_dir, self.azure_account, "nat_gateways"
            )
            os.makedirs(self._azure_api_nat_gateways_cache_dir, exist_ok=True)
        return self._azure_api_nat_gateways_cache_dir

    @azure_api_nat_gateways_cache_dir.setter
    def azure_api_nat_gateways_cache_dir(self, value):
        raise ValueError(value)

    @property
    def azure_api_nat_gateways_cache_file(self):
        return os.path.join(self.azure_api_nat_gateways_cache_dir, "nat_gateways.json")

    @azure_api_nat_gateways_cache_file.setter
    def azure_api_nat_gateways_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region network_interfaces
    @property
    def azure_api_network_interfaces_cache_dir(self):
        if self._azure_api_network_interfaces_cache_dir is None:
            self._azure_api_network_interfaces_cache_dir = os.path.join(
                self.azure_api_cache_dir, self.azure_account, "network_interfaces"
            )
            os.makedirs(self._azure_api_network_interfaces_cache_dir, exist_ok=True)
        return self._azure_api_network_interfaces_cache_dir

    @azure_api_network_interfaces_cache_dir.setter
    def azure_api_network_interfaces_cache_dir(self, value):
        raise ValueError(value)

    @property
    def azure_api_network_interfaces_cache_file(self):
        return os.path.join(
            self.azure_api_network_interfaces_cache_dir, "network_interfaces.json"
        )

    @azure_api_network_interfaces_cache_file.setter
    def azure_api_network_interfaces_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region public_ip_addresses
    @property
    def azure_api_public_ip_addresses_cache_dir(self):
        if self._azure_api_public_ip_addresses_cache_dir is None:
            self._azure_api_public_ip_addresses_cache_dir = os.path.join(
                self.azure_api_cache_dir, self.azure_account, "public_ip_addresses"
            )
            os.makedirs(self._azure_api_public_ip_addresses_cache_dir, exist_ok=True)
        return self._azure_api_public_ip_addresses_cache_dir

    @azure_api_public_ip_addresses_cache_dir.setter
    def azure_api_public_ip_addresses_cache_dir(self, value):
        raise ValueError(value)

    @property
    def azure_api_public_ip_addresses_cache_file(self):
        return os.path.join(
            self.azure_api_public_ip_addresses_cache_dir, "public_ip_addresses.json"
        )

    @azure_api_public_ip_addresses_cache_file.setter
    def azure_api_public_ip_addresses_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region network_security_groups
    @property
    def azure_api_network_security_groups_cache_dir(self):
        if self._azure_api_network_security_groups_cache_dir is None:
            self._azure_api_network_security_groups_cache_dir = os.path.join(
                self.azure_api_cache_dir, self.azure_account, "network_security_groups"
            )
            os.makedirs(
                self._azure_api_network_security_groups_cache_dir, exist_ok=True
            )
        return self._azure_api_network_security_groups_cache_dir

    @azure_api_network_security_groups_cache_dir.setter
    def azure_api_network_security_groups_cache_dir(self, value):
        raise ValueError(value)

    @property
    def azure_api_network_security_groups_cache_file(self):
        return os.path.join(
            self.azure_api_network_security_groups_cache_dir,
            "network_security_groups.json",
        )

    @azure_api_network_security_groups_cache_file.setter
    def azure_api_network_security_groups_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region ssh_keys
    @property
    def azure_api_ssh_keys_cache_dir(self):
        if self._azure_api_ssh_keys_cache_dir is None:
            self._azure_api_ssh_keys_cache_dir = os.path.join(
                self.azure_api_cache_dir, self.azure_account, "ssh_keys"
            )
            os.makedirs(self._azure_api_ssh_keys_cache_dir, exist_ok=True)
        return self._azure_api_ssh_keys_cache_dir

    @azure_api_ssh_keys_cache_dir.setter
    def azure_api_ssh_keys_cache_dir(self, value):
        raise ValueError(value)

    @property
    def azure_api_ssh_keys_cache_file(self):
        return os.path.join(self.azure_api_ssh_keys_cache_dir, "ssh_keys.json")

    @azure_api_ssh_keys_cache_file.setter
    def azure_api_ssh_keys_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region virtual_networks
    @property
    def azure_api_virtual_networks_cache_dir(self):
        if self._azure_api_virtual_networks_cache_dir is None:
            self._azure_api_virtual_networks_cache_dir = os.path.join(
                self.azure_api_cache_dir, self.azure_account, "virtual_networks"
            )
            os.makedirs(self._azure_api_virtual_networks_cache_dir, exist_ok=True)
        return self._azure_api_virtual_networks_cache_dir

    @azure_api_virtual_networks_cache_dir.setter
    def azure_api_virtual_networks_cache_dir(self, value):
        raise ValueError(value)

    @property
    def azure_api_virtual_networks_cache_file(self):
        return os.path.join(
            self.azure_api_virtual_networks_cache_dir, "virtual_networks.json"
        )

    @azure_api_virtual_networks_cache_file.setter
    def azure_api_virtual_networks_cache_file(self, value):
        raise ValueError(value)

    # endregion

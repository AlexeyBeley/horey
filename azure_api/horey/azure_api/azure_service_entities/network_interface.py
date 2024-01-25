"""
Azure network interface.

"""

# pylint: disable= no-name-in-module
from horey.azure_api.azure_service_entities.azure_object import AzureObject


class NetworkInterface(AzureObject):
    """
    Main class.

    """
    def __init__(self, dict_src, from_cache=False):
        self.name = None
        self.resource_group_name = None
        self.id = None
        self.location = None
        self.tags = {}
        self.ip_configurations = None
        self.network_security_group = None

        super().__init__(dict_src, from_cache=from_cache)

        if from_cache:
            self.init_network_interface_from_cache(dict_src)
            return

        init_options = {
            "id": self.init_default_attr,
            "name": self.init_default_attr,
            "type": self.init_default_attr,
            "location": self.init_default_attr,
            "tags": self.init_default_attr,
            "etag": self.init_default_attr,
            "resource_guid": self.init_default_attr,
            "provisioning_state": self.init_default_attr,
            "virtual_machine": self.init_default_attr,
            "network_security_group": self.init_default_attr,
            "ip_configurations": self.init_default_attr,
            "tap_configurations": self.init_default_attr,
            "dns_settings": self.init_default_attr,
            "mac_address": self.init_default_attr,
            "primary": self.init_default_attr,
            "enable_accelerated_networking": self.init_default_attr,
            "enable_ip_forwarding": self.init_default_attr,
            "hosted_workloads": self.init_default_attr,
            "nic_type": self.init_default_attr,
            "vnet_encryption_supported": self.init_default_attr,
            "auxiliary_mode": self.init_default_attr,
            "auxiliary_sku": self.init_default_attr,
            "disable_tcp_state_tracking": self.init_default_attr
        }

        self.init_attrs(dict_src, init_options)

    def init_network_interface_from_cache(self, dict_src):
        """
        Init from cache

        :param dict_src:
        :return:
        """

        options = {}
        self._init_from_cache(dict_src, options)

    def generate_create_request(self):
        """
        Standard.

        :return:
        """

        return [
            self.resource_group_name,
            self.name,
            {
                "location": self.location,
                "ip_configurations": self.ip_configurations,
                "network_security_group": self.network_security_group,
                "tags": self.tags,
            }
        ]

    def update_after_creation(self, network_interface):
        """
        Initialize.

        :param network_interface:
        :return:
        """

        self.ip_configurations = [
            config.as_dict() for config in network_interface.ip_configurations
        ]
        self.id = network_interface.id

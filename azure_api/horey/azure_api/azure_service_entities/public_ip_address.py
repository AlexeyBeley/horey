"""
Public IP representation.

"""

# pylint: disable= no-name-in-module
from horey.azure_api.azure_service_entities.azure_object import AzureObject


class PublicIpAddress(AzureObject):
    """
    Main class

    """
    def __init__(self, dict_src, from_cache=False):
        self.name = None
        self.id = None
        self.location = None
        self.tags = {}
        self.resource_group_name = None
        self.sku = None
        self.public_ip_allocation_method = None
        self.public_ip_address_version = None
        self.ip_address = None
        self.ip_configuration = None
        self.nat_gateway = None

        super().__init__(dict_src, from_cache=from_cache)

        if from_cache:
            self.init_public_ip_address_from_cache(dict_src)
            return

        init_options = {
            "id": self.init_default_attr,
            "name": self.init_default_attr,
            "type": self.init_default_attr,
            "location": self.init_default_attr,
            "tags": self.init_default_attr,
            "sku": self.init_default_attr,
            "etag": self.init_default_attr,
            "public_ip_allocation_method": self.init_default_attr,
            "public_ip_address_version": self.init_default_attr,
            "ip_configuration": self.init_default_attr,
            "ip_tags": self.init_default_attr,
            "ip_address": self.init_default_attr,
            "idle_timeout_in_minutes": self.init_default_attr,
            "resource_guid": self.init_default_attr,
            "provisioning_state": self.init_default_attr,
            "nat_gateway": self.init_default_attr,
            "ddos_settings": self.init_default_attr
        }

        self.init_attrs(dict_src, init_options)

    def init_public_ip_address_from_cache(self, dict_src):
        """
        Init from cache
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def generate_create_request(self):
        """
        RESOURCE_GROUP_NAME,
        IP_NAME,
        {
            "location": LOCATION,
            "sku": { "name": "Standard" },
            "public_ip_allocation_method": "Static",
            "public_ip_address_version" : "IPV4"
        }
        """
        if self.resource_group_name is None:
            raise ValueError()

        ret = [
            self.resource_group_name,
            self.name,
            {
                "location": self.location,
                "sku": self.sku,
                "public_ip_allocation_method": self.public_ip_allocation_method,
                "public_ip_address_version": self.public_ip_address_version,
                "tags": self.tags,
            },
        ]
        return ret

    def update_after_creation(self, public_ip_address):
        """
        Update runtime info.

        :param public_ip_address:
        :return:
        """

        self.id = public_ip_address.id
        self.ip_address = public_ip_address.ip_address

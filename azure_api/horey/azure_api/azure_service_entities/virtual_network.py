import pdb

from horey.azure_api.azure_service_entities.azure_object import AzureObject


class VirtualNetwork(AzureObject):
    def __init__(self, dict_src, from_cache=False):
        self.name = None
        self.resource_group_name = None
        self.address_space = None
        self.id = None
        self.location = None
        self.tags = {}
        self.resource_guid = None
        self.etag = None

        super().__init__(dict_src, from_cache=from_cache)

        if from_cache:
            self.init_vnet_from_cache(dict_src)
            return

        init_options = {
            "id": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def init_vnet_from_cache(self, dict_src):
        raise NotImplementedError()

    def generate_create_request(self):
        """
        RESOURCE_GROUP_NAME,
        VNET_NAME,
        {
            "location": LOCATION,
            "address_space": {
                "address_prefixes": ["10.0.0.0/16"]
            }
        }
        """
        return [self.resource_group_name,
                self.name,
                {"location": self.location,
                 "address_space": {"address_prefixes": [ip.str_address_slash_short_mask() for ip in self.address_space["address_prefixes"] ]},
                 "tags": self.tags
                 }
                ]

    def update_after_creation(self, async_waiter):
        async_waiter.wait()
        virtual_network = async_waiter.result()
        if virtual_network.provisioning_state != "Succeeded":
            raise ValueError()
        self.id = virtual_network.id
        self.resource_guid = virtual_network.resource_guid
        self.etag = virtual_network.etag

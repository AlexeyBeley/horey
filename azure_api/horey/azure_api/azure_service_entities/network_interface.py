import pdb

from horey.azure_api.azure_service_entities.azure_object import AzureObject


class NetworkInterface(AzureObject):
    def __init__(self, dict_src, from_cache=False):
        self.name = None
        self.id = None
        self.location = None
        self.tags = {}
        self.properties = None

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
            "sku": self.init_default_attr,
            "etag": self.init_default_attr,
            "idle_timeout_in_minutes": self.init_default_attr,
            "public_ip_addresses": self.init_default_attr,
            "subnets": self.init_default_attr,
            "resource_guid": self.init_default_attr,
            "provisioning_state": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def init_network_interface_from_cache(self, dict_src):
        raise NotImplementedError()

    def generate_create_request(self):
        """
            return list:


            "PythonAzureExample-rg",
            {
             "location": "centralus"
             "tags": { "environment":"test", "department":"tech" }
            }
        """
        return [self.name,
                {"location": self.location,
                 "tags": self.tags
                 }
                ]

    def update_after_creation(self, network_interface):
        self.id = network_interface.id
        self.properties = network_interface.properties.__dict__

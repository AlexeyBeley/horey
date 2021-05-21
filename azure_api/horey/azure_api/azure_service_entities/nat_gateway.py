import pdb

from horey.azure_api.azure_service_entities.azure_object import AzureObject


class NatGateway(AzureObject):
    def __init__(self, dict_src, from_cache=False):
        self.name = None
        self.resource_group_name = None
        self.id = None
        self.location = None
        self.tags = {}
        self.public_ip_addresses = None
        self.subnets = None
        self.sku = None

        super().__init__(dict_src, from_cache=from_cache)

        if from_cache:
            self.init_nat_gateway_from_cache(dict_src)
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

    def init_nat_gateway_from_cache(self, dict_src):
        raise NotImplementedError()

    def generate_create_request(self):
        return [self.resource_group_name,
                self.name,
                {"location": self.location,
                 "public_ip_addresses": self.public_ip_addresses,
                 "sku": self.sku,
                 "tags": self.tags
                 }
                ]

    def update_after_creation(self, nat_gateway):
        pdb.set_trace()
        self.id = nat_gateway.id

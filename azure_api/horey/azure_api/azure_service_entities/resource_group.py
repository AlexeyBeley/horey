import pdb

from horey.azure_api.azure_service_entities.azure_object import AzureObject


class ResourceGroup(AzureObject):
    def __init__(self, dict_src, from_cache=False):
        self.name = None
        self.id = None
        self.location = None
        self.tags = {}
        self.properties = None

        super().__init__(dict_src, from_cache=from_cache)

        if from_cache:
            self.init_resource_group_from_cache(dict_src)
            return

        init_options = {
            "id": self.init_default_attr,
            "name": self.init_default_attr,
            "type": self.init_default_attr,
            "properties": self.init_default_attr,
            "location": self.init_default_attr,
            "managed_by": self.init_default_attr,
            "tags": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def init_resource_group_from_cache(self, dict_src):
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

    def update_after_creation(self, resource_group):
        self.id = resource_group.id
        self.properties = resource_group.properties.__dict__

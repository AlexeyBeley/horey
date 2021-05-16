import pdb

from horey.azure_api.azure_service_entities.azure_object import AzureObject


class SSHKey(AzureObject):
    def __init__(self, dict_src, from_cache=False):
        self.name = None
        self.resource_group_name = None
        self.id = None
        self.location = None
        self.tags = {}
        self.properties = None

        super().__init__(dict_src, from_cache=from_cache)

        if from_cache:
            self.init_ssh_key_from_cache(dict_src)
            return

        init_options = {
            "id": self.init_default_attr,
            "name": self.init_default_attr,
            "location": self.init_default_attr,
            "tags": self.init_default_attr,
            "public_key": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def init_ssh_key_from_cache(self, dict_src):
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
        return [self.resource_group_name,
                self.name,
                {"location": self.location,
                 "tags": self.tags
                 }
                ]

    def update_after_creation(self, ssh_key):
        self.id = ssh_key.id

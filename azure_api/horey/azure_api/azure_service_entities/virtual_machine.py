import pdb

from horey.azure_api.azure_service_entities.azure_object import AzureObject


class VirtualMachine(AzureObject):
    def __init__(self, dict_src, from_cache=False):
        self.name = None
        self.resource_group_name = None
        self.id = None
        self.location = None
        self.tags = {}
        self.hardware_profile = None
        self.storage_profile = None
        self.os_profile = None
        self.network_profile = None

        super().__init__(dict_src, from_cache=from_cache)

        if from_cache:
            self.init_virtual_machine_from_cache(dict_src)
            return

        init_options = {
            "id": self.init_default_attr,
            "name": self.init_default_attr,
            "type": self.init_default_attr,
            "location": self.init_default_attr,
            "hardware_profile": self.init_default_attr,
            "storage_profile": self.init_default_attr,
            "os_profile": self.init_default_attr,
            "network_profile": self.init_default_attr,
            "diagnostics_profile": self.init_default_attr,
            "provisioning_state": self.init_default_attr,
            "vm_id": self.init_default_attr,
            "tags": self.init_default_attr,
            "zones": self.init_default_attr,
            "time_created": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def init_virtual_machine_from_cache(self, dict_src):
        """
        Init from cache
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

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
                 "hardware_profile": self.hardware_profile,
                 "storage_profile": self.storage_profile,
                 "os_profile": self.os_profile,
                 "network_profile": self.network_profile,
                 "tags": self.tags
                 }
                ]

    def update_after_creation(self, virtual_machine):
        self.id = virtual_machine.id

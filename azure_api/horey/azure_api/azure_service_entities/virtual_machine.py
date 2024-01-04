"""
Azure VM object.

"""

from horey.azure_api.azure_service_entities.azure_object import AzureObject


class VirtualMachine(AzureObject):
    """
    Main class

    """

    def __init__(self, dict_src, from_cache=False):
        self.name = None
        self._resource_group_name = None
        self.id = None
        self.location = None
        self.tags = {}
        self.hardware_profile = None
        self.storage_profile = None
        self.os_profile = None
        self.network_profile = {}

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

    @property
    def resource_group_name(self):
        """
        Generate or use one explicitly set.

        :return:
        """

        if self._resource_group_name is None:
            if self.network_profile:
                lst_id = self.network_profile["network_interfaces"][0]["id"].split("/")
                if lst_id[3] != "resourceGroups":
                    raise RuntimeError(f"Can not parse ID: {lst_id}")
                self._resource_group_name = lst_id[4]

        return self._resource_group_name

    @resource_group_name.setter
    def resource_group_name(self, value):
        """
        Setter.

        :param value:
        :return:
        """

        self._resource_group_name = value

    def init_virtual_machine_from_cache(self, dict_src):
        """
        Init from cache
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def generate_create_request(self, tags_only=False):
        """
        return list:


        "PythonAzureExample-rg",
        {
         "location": "centralus"
         "tags": { "environment":"test", "department":"tech" }
        }
        """
        if not tags_only:
            dict_options = {
                "location": self.location,
                "hardware_profile": self.hardware_profile,
                "storage_profile": self.storage_profile,
                "os_profile": self.os_profile,
                "network_profile": self.network_profile,
                "tags": self.tags,
            }
        else:
            dict_options = {
                "location": self.location,
                "tags": self.tags,
            }

        return [
            self.resource_group_name,
            self.name,
            dict_options
        ]

    def update_after_creation(self, virtual_machine):
        """
        Update self from existing object.

        :param virtual_machine:
        :return:
        """

        self.id = virtual_machine.id

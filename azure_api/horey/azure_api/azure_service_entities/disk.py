"""
Azure Disk obj.

"""

from azure.mgmt.compute.models import DiskCreateOption
from horey.azure_api.azure_service_entities.azure_object import AzureObject


class Disk(AzureObject):
    """
    Main Class

    """

    def __init__(self, dict_src, from_cache=False):
        self.name = None
        self.id = None
        self.location = None
        self.tags = {}
        self._resource_group_name = None
        self.disk_size_gb = None
        self.unique_id = None

        super().__init__(dict_src, from_cache=from_cache)

        if from_cache:
            self.init_disk_from_cache(dict_src)
            return

        init_options = {
            "id": self.init_default_attr,
            "name": self.init_default_attr,
            "type": self.init_default_attr,
            "location": self.init_default_attr,
            "tags": self.init_default_attr,
            "managed_by": self.init_default_attr,
            "sku": self.init_default_attr,
            "time_created": self.init_default_attr,
            "creation_data": self.init_default_attr,
            "disk_size_gb": self.init_default_attr,
            "disk_size_bytes": self.init_default_attr,
            "unique_id": self.init_default_attr,
            "provisioning_state": self.init_default_attr,
            "disk_iops_read_write": self.init_default_attr,
            "disk_m_bps_read_write": self.init_default_attr,
            "disk_state": self.init_default_attr,
            "encryption": self.init_default_attr,
            "network_access_policy": self.init_default_attr,
            "tier": self.init_default_attr,
            "os_type": self.init_default_attr,
            "hyper_v_generation": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    @property
    def resource_group_name(self):
        """
        Generate or use one explicitly set.

        :return:
        """

        if self._resource_group_name is None:
            if self.id is not None:
                lst_id = self.id.split("/")
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

    def init_disk_from_cache(self, dict_src):
        """
        Standard.

        :param dict_src:
        :return:
        """

        raise NotImplementedError()

    def generate_create_request(self):
        """
        return list:


        'my_resource_group',
        'my_disk_name',
        {
            'location': 'eastus',
            'disk_size_gb': 20,
            'creation_data': {
                'create_option': DiskCreateOption.empty
            }
        }
        """
        return [
            self.resource_group_name,
            self.name,
            {
                "location": self.location,
                "disk_size_gb": self.disk_size_gb,
                "creation_data": {"create_option": DiskCreateOption.empty},
                "tags": self.tags,
            }
        ]

    def update_after_creation(self, disk):
        """
        Update self from existing object.

        :param disk:
        :return:
        """

        self.id = disk.id
        self.unique_id = disk.unique_id

import pdb

from horey.azure_api.azure_service_entities.azure_object import AzureObject
from azure.mgmt.compute.models import DiskCreateOption


class Bucket(AzureObject):
    def __init__(self, dict_src, from_cache=False):
        self.name = None

        super().__init__(dict_src, from_cache=from_cache)

        if from_cache:
            self.init_disk_from_cache(dict_src)
            return

        init_options = {
            "name": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def init_disk_from_cache(self, dict_src):
        raise NotImplementedError()

    def generate_create_request(self):
        raise NotImplementedError()
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
            },
        ]

    def update_after_creation(self, disk):
        self.id = disk.id
        self.unique_id = disk.unique_id

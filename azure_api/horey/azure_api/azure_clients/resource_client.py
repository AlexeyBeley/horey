import pdb

from azure.mgmt.resource import ResourceManagementClient
from horey.azure_api.azure_clients.azure_client import AzureClient
from horey.azure_api.azure_service_entities.resource_group import ResourceGroup

from horey.h_logger import get_logger

logger = get_logger()


class ResourceClient(AzureClient):
    CLIENT_CLASS = ResourceManagementClient

    def __init__(self):
        """
        https://learn.microsoft.com/en-us/python/api/azure-mgmt-resource/azure.mgmt.resource.resourcemanagementclient?view=azure-python
        """
        super().__init__()

    def get_all_resource_groups(self):
        return [
            ResourceGroup(obj.as_dict()) for obj in self.client.resource_groups.list()
        ]

    def raw_create_resource_group(self, lst_args):
        response = self.client.resource_groups.create_or_update(*lst_args)
        return response

    def raw_delete_resource_group(self, name):
        logger.info(f"Begin resource group deletion: '{name}'")
        response = self.client.resource_groups.begin_delete(name)
        response.wait()
        return response.status() == "Succeeded"

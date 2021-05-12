import pdb

from azure.mgmt.resource import ResourceManagementClient
from horey.azure_api.azure_clients.azure_client import AzureClient
from horey.azure_api.azure_service_entities.resource_group import ResourceGroup


class ResourceGroupsClient(AzureClient):
    CLIENT_CLASS = ResourceManagementClient

    def __init__(self):
        super().__init__()

    def get_all_resoure_groups(self):
        return [ResourceGroup(obj.as_dict()) for obj in self.client.resource_groups.list()]

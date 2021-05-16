import pdb

from azure.mgmt.resource import ResourceManagementClient
from horey.azure_api.azure_clients.azure_client import AzureClient
from horey.azure_api.azure_service_entities.resource_group import ResourceGroup


class ResourceClient(AzureClient):
    CLIENT_CLASS = ResourceManagementClient

    def __init__(self):
        super().__init__()

    def get_all_resource_groups(self):
        return [ResourceGroup(obj.as_dict()) for obj in self.client.resource_groups.list()]

    def raw_create_resource_group(self, lst_args):
        response = self.client.resource_groups.create_or_update(*lst_args)
        return response

    def raw_delete_resource_group(self, name):
        delete_async_operation = self.client.resource_groups.begin_delete(name)
        return delete_async_operation


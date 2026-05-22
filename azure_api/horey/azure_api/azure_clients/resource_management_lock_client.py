"""
Manage locks.

"""

from azure.mgmt.resource import ManagementLockClient
from horey.azure_api.azure_clients.azure_client import AzureClient


from horey.h_logger import get_logger

logger = get_logger()


class ResourceManagementLockClient(AzureClient):
    """
    Main class.
    """
    CLIENT_CLASS = ManagementLockClient

    def get_public_ip_resource_locks(self, resource_group_name, public_ip_name):
        """
        Shows any management locks applied to a specific public IP address resource.

        Args:
            resource_group_name (str): The name of the resource group.
            public_ip_name (str): The name of the public IP address resource.

        Returns:
            list: A list of dictionaries containing lock details, or an empty list if no locks found.
        """

        locks = self.client.management_locks.list_at_resource_level(
                resource_group_name=resource_group_name,
                resource_provider_namespace="Microsoft.Network",
                parent_resource_path="",
                resource_type="publicIPAddresses",
                resource_name=public_ip_name
            )

        return list(locks)

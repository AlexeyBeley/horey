import pdb

from azure.mgmt.compute import ComputeManagementClient
from horey.azure_api.azure_clients.azure_client import AzureClient


class ComputeClient(AzureClient):
    CLIENT_CLASS = ComputeManagementClient

    def __init__(self):
        super().__init__()



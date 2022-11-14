import pdb

from azure.mgmt.compute import ComputeManagementClient
from horey.azure_api.base_entities.azure_account import AzureAccount
from azure.identity import ClientSecretCredential


class AzureClient:
    CLIENT_CLASS = None

    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self.connect()
        return self._client

    @client.setter
    def client(self, _):
        raise ValueError("Can not explicitly set client")

    def connect(self):
        account = AzureAccount.get_azure_account()
        for connection_step in account.connection_steps:
            credential = ClientSecretCredential(
                tenant_id=connection_step.tenant_id,
                client_id=connection_step.client_id,
                client_secret=connection_step.secret,
            )
            self._client = self.CLIENT_CLASS(
                credential, connection_step.subscription_id
            )

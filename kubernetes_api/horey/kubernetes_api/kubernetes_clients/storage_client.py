import pdb

from google.cloud.storage import Client
from horey.kubernetes_api.kubernetes_clients.kubernetes_client import KubernetesClient
from horey.kubernetes_api.base_entities.kubernetes_account import KubernetesAccount

from horey.h_logger import get_logger

logger = get_logger()


class StorageClient(KubernetesClient):
    CLIENT_CLASS = Client

    def __init__(self):
        super().__init__()

    def provision_bucket(self, bucket):
        pdb.set_trace()
        request_args = [bucket.name]
        request_kwargs = {"location": self.location}

        self.execute(
            self.client.create_bucket, args=request_args, kwargs=request_kwargs
        )
        bucket = self.client.create_bucket(bucket.name)

import pdb

from google.cloud.storage import Client
from horey.gcp_api.gcp_clients.gcp_client import GCPClient
from horey.gcp_api.base_entities.gcp_account import GCPAccount

from horey.h_logger import get_logger

logger = get_logger()


class StorageClient(GCPClient):
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

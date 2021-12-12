import pdb
from oci.identity import IdentityClient
from oci.core.compute_client import ComputeClient

from horey.oci_api.oci_clients.oci_client import OCIClient
from horey.oci_api.base_entities.oci_account import OCIAccount

from horey.h_logger import get_logger

logger = get_logger()


class ComputeClient(OCIClient):
    CLIENT_CLASS = ComputeClient

    def __init__(self):
        super().__init__()

    def provision_bucket(self, bucket):
        pdb.set_trace()
        request_args = [bucket.name]
        request_kwargs = {"location": self.location}

        self.execute(self.client.create_dedicated_vm_host_details, args=request_args, kwargs=request_kwargs)
        bucket = self.client.create_bucket(bucket.name)

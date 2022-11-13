import pdb
from oci.core.compute_client import ComputeClient

from horey.oci_api.oci_clients.oci_client import OCIClient
from horey.oci_api.oci_service_entities.vm_host import VMHost
from horey.oci_api.base_entities.oci_account import OCIAccount


from horey.h_logger import get_logger

logger = get_logger()


class OCIComputeClient(OCIClient):
    CLIENT_CLASS = ComputeClient

    def __init__(self):
        super().__init__()

    def provision_dedicated_vm_host(self, host):
        pdb.set_trace()

        self.provision_dedicated_vm_host_raw(*host.generate_create_request())

    def provision_dedicated_vm_host_raw(self, args, kwargs):
        self.execute(
            self.client.create_dedicated_vm_host_details, args=args, kwargs=kwargs
        )

    def get_all_vm_hosts(self, region=None):
        """
        Get all vm_hosts in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_vm_hosts(region)

        final_result = list()
        pdb.set_trace()
        for region in OCIAccount.get_oci_account().regions.values():
            final_result += self.get_region_vm_hosts(region)

        return final_result

    def get_region_vm_hosts(self, region, filters=None):
        final_result = list()
        pdb.set_trace()
        OCIAccount.set_oci_region(region)

        for dict_src in self.execute(
            self.client.list_dedicated_vm_hosts, None, args=args
        ):
            obj = VMHost(dict_src)
            final_result.append(obj)

        return final_result

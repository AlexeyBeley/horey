import pdb

from horey.oci_api.oci_service_entities.oci_object import OCIObject
from oci.core.models import CreateDedicatedVmHostDetails


class VMHost(OCIObject):
    def __init__(self, dict_src, from_cache=False):
        self.name = None

        super().__init__(dict_src, from_cache=from_cache)

        if from_cache:
            self.init_disk_from_cache(dict_src)
            return

        init_options = {
            "name": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def init_disk_from_cache(self, dict_src):
        raise NotImplementedError()

    def generate_create_request(self):
        """
        availability_domain 	[Required] Gets the availability_domain of this CreateDedicatedVmHostDetails.
        compartment_id 	[Required] Gets the compartment_id of this CreateDedicatedVmHostDetails.
        dedicated_vm_host_shape 	[Required] Gets the dedicated_vm_host_shape of this CreateDedicatedVmHostDetails.
        defined_tags 	Gets the defined_tags of this CreateDedicatedVmHostDetails.
        display_name 	Gets the display_name of this CreateDedicatedVmHostDetails.
        fault_domain 	Gets the fault_domain of this CreateDedicatedVmHostDetails.
        freeform_tags 	Gets the freeform_tags of this CreateDedicatedVmHostDetails.
        @return:
        """
        pdb.set_trace()
        create_dedicated_vm_host_details = CreateDedicatedVmHostDetails()
        kwargs = {}
        return create_dedicated_vm_host_details, kwargs

    def update_after_creation(self, disk):
        self.id = disk.id
        self.unique_id = disk.unique_id


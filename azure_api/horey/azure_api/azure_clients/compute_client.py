import pdb

from azure.mgmt.compute import ComputeManagementClient
from horey.azure_api.azure_clients.azure_client import AzureClient
from horey.azure_api.azure_service_entities.disk import Disk
from horey.azure_api.azure_service_entities.ssh_key import SSHKey
from horey.azure_api.azure_service_entities.virtual_machine import VirtualMachine
from horey.h_logger import get_logger

logger = get_logger()


class ComputeClient(AzureClient):
    CLIENT_CLASS = ComputeManagementClient

    def __init__(self):
        super().__init__()

    def raw_create_virtual_machines(self, lst_args):
        logger.info(f"Begin virtual machine creation: '{lst_args[1]}'")
        try:
            response = self.client.virtual_machines.begin_create_or_update(*lst_args)
        except Exception as inst:
            print(inst)
            ret = inst
            pdb.set_trace()

        response.wait()
        return response.result()

    def raw_create_ssh_key(self, lst_args):
        response = self.client.ssh_public_keys.create(*lst_args)
        return response

    def get_all_disks(self):
        return [Disk(obj.as_dict()) for obj in self.client.disks.list()]

    def get_all_ssh_keys(self, resource_group):
        return [SSHKey(obj.as_dict()) for obj in self.client.ssh_public_keys.list_by_resource_group(resource_group.name)]

    def get_all_virtual_machines(self, resource_group):
        return [VirtualMachine(obj.as_dict()) for obj in self.client.virtual_machines.list(resource_group.name)]

    def raw_create_disk(self, lst_args):
        logger.info(f"Begin disk creation: '{lst_args[1]}'")
        response = self.client.disks.begin_create_or_update(*lst_args)
        response.wait()
        return response.result()

    def raw_delete_disk(self, resource_group_name, disk_name):
        logger.info(f"Begin disk deletion: '{disk_name}'")
        response = self.client.disks.begin_delete(resource_group_name, disk_name)
        response.wait()
        return response.status() == "Succeeded"

    def raw_delete_virtual_machine(self, obj_repr):
        logger.info(f"Begin virtual machine deletion: '{obj_repr.resource_group_name} {obj_repr.name}'")
        response = self.client.virtual_machines.begin_delete(obj_repr.resource_group_name, obj_repr.name)
        pdb.set_trace()
        response.wait()
        return response.status() == "Succeeded"

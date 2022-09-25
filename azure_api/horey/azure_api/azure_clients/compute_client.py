"""
Compute service API.

"""

from azure.mgmt.compute import ComputeManagementClient
from horey.azure_api.azure_clients.azure_client import AzureClient
from horey.azure_api.azure_service_entities.disk import Disk
from horey.azure_api.azure_service_entities.ssh_key import SSHKey
from horey.azure_api.azure_service_entities.virtual_machine import VirtualMachine
from horey.h_logger import get_logger

logger = get_logger()


class ComputeClient(AzureClient):
    """
    Main class - implements the compute client API
    """
    CLIENT_CLASS = ComputeManagementClient

    def provision_virtual_machine(self, virtual_machine):
        """
        Provision VM.

        @param virtual_machine:
        @return:
        """
        all_machines = self.get_all_virtual_machines(virtual_machine.resource_group_name)
        for existing_machine in all_machines:
            if existing_machine.name == virtual_machine.name:
                virtual_machine.update_after_creation(existing_machine)
                return virtual_machine

        return self.raw_create_virtual_machines(virtual_machine.generate_create_request())

    def raw_create_virtual_machines(self, lst_args):
        """
        Create a vm.

        @param lst_args:
        @return:
        """

        logger.info(f"Begin virtual machine creation: '{lst_args[1]}'")
        response = self.client.virtual_machines.begin_create_or_update(*lst_args)
        response.wait()
        return response.result()

    def raw_create_ssh_key(self, lst_args):
        """
        Standard.

        @param lst_args:
        @return:
        """
        response = self.client.ssh_public_keys.create(*lst_args)
        return response

    def get_all_disks(self):
        """
        Standard.

        @return:
        """
        return [Disk(obj.as_dict()) for obj in self.client.disks.list()]

    def get_all_ssh_keys(self, resource_group):
        """
        Standard.

        @param resource_group:
        @return:
        """
        return [SSHKey(obj.as_dict()) for obj in self.client.ssh_public_keys.list_by_resource_group(resource_group.name)]

    def get_all_virtual_machines(self, resource_group_name):
        """
        Standard.

        @param resource_group_name:
        @return:
        """
        return [VirtualMachine(obj.as_dict()) for obj in self.client.virtual_machines.list(resource_group_name)]

    def raw_create_disk(self, lst_args):
        """
        Standard.

        @param lst_args:
        @return:
        """
        logger.info(f"Begin disk creation: '{lst_args[1]}'")
        response = self.client.disks.begin_create_or_update(*lst_args)
        response.wait()
        return response.result()

    def raw_delete_disk(self, resource_group_name, disk_name):
        """
        Delete disk.

        @param resource_group_name:
        @param disk_name:
        @return:
        """
        logger.info(f"Begin disk deletion: '{disk_name}'")
        response = self.client.disks.begin_delete(resource_group_name, disk_name)
        response.wait()
        return response.status() == "Succeeded"

    def raw_delete_virtual_machine(self, obj_repr):
        """
        Delete the vm

        @param obj_repr:
        @return:
        """
        logger.info(f"Begin virtual machine deletion: '{obj_repr.resource_group_name} {obj_repr.name}'")
        response = self.client.virtual_machines.begin_delete(obj_repr.resource_group_name, obj_repr.name)
        response.wait()
        return response.status() == "Succeeded"

    def get_available_vm_sizes(self, region):
        """
        Get list of vm sizes available in the region

        @return:
        """

        return list(self.client.virtual_machine_sizes.list(region))

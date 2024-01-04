"""
Compute service API.

"""
import datetime

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

    def provision_virtual_machine(self, virtual_machine, tags_only=False):
        """
        Provision VM.

        @param virtual_machine:
        @param tags_only: only change the tags
        @return:
        """
        all_machines = self.get_all_virtual_machines(
            virtual_machine.resource_group_name
        )

        if not tags_only:
            for existing_machine in all_machines:
                if existing_machine.name == virtual_machine.name:
                    virtual_machine.update_after_creation(existing_machine)
                    return virtual_machine

        return self.raw_create_virtual_machines(
            virtual_machine.generate_create_request(tags_only=tags_only)
        )

    def provision_virtual_machine_tags(self, virtual_machine):
        """
        Provision VM tags

        @param virtual_machine:
        @return:
        """

        return self.provision_virtual_machine(virtual_machine, tags_only=True)

    def get_vm(self, resource_group_name, name):
        """
        Get VM object.

        :param resource_group_name:
        :param name:
        :return:
        """

        for vm in self.get_all_virtual_machines(resource_group_name):
            if vm.name == name:
                return vm

        return None

    def stop_vm(self, vm: VirtualMachine):
        """
        Stop VM.

        :param vm:
        :return:
        """

        logger.info(f"Stopping VM {vm.resource_group_name}/{vm.name}")

        start_time = datetime.datetime.now()

        response = self.client.virtual_machines.begin_power_off(vm.resource_group_name, vm.name)
        response.wait()

        end_time = datetime.datetime.now()

        logger.info(f"Stopped VM {vm.resource_group_name}/{vm.name}, took: {end_time - start_time}")

        return response.result()

    def start_vm(self, vm: VirtualMachine):
        """
        Start VM.

        :param vm:
        :return:
        """

        response = self.client.virtual_machines.begin_start(vm.resource_group_name, vm.name)
        response.wait()
        return response.result()

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

    def get_all_disks(self, resource_group):
        """
        Standard.

        @return:
        """
        return [Disk(obj.as_dict()) for obj in self.client.disks.list_by_resource_group(resource_group.name)]

    def get_disk(self, resource_group_name, disk_name):
        """
        Get object.

        :param resource_group_name:
        :param disk_name:
        :return:
        """

        for obj in self.client.disks.list_by_resource_group(resource_group_name):
            disk = Disk(obj.as_dict())
            if disk.name == disk_name:
                return disk
        return None

    def get_all_ssh_keys(self, resource_group):
        """
        Standard.

        @param resource_group:
        @return:
        """
        return [
            SSHKey(obj.as_dict())
            for obj in self.client.ssh_public_keys.list_by_resource_group(
                resource_group.name
            )
        ]

    def get_all_virtual_machines(self, resource_group_name):
        """
        Standard.

        @param resource_group_name:
        @return:
        """
        return [
            VirtualMachine(obj.as_dict())
            for obj in self.client.virtual_machines.list(resource_group_name)
        ]

    def provision_disk(self, disk: Disk):
        """
        Create or update

        :param disk:
        :return:
        """

        response = self.raw_create_disk(disk.generate_create_request())
        disk.update_after_creation(response)

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

    def dispose_disk(self, obj_disk: Disk, asynchronous=False):
        """
        Dispose disk.

        :param obj_disk:
        :param asynchronous:
        :return:
        """

        response = self.raw_delete_disk(obj_disk.resource_group_name, obj_disk.name)
        if not asynchronous:
            response.wait()
        return response

    def raw_delete_disk(self, resource_group_name, disk_name):
        """
        Delete disk.

        @param resource_group_name:
        @param disk_name:
        @return:
        """
        logger.info(f"Begin disk deletion: '{disk_name}'")
        return self.client.disks.begin_delete(resource_group_name, disk_name)

    def dispose_virtual_machine(self, obj_repr, asynchronous=False):
        """
        Delete the vm

        @param obj_repr:
        @param asynchronous:
        @return:
        """
        logger.info(
            f"Begin virtual machine deletion: '{obj_repr.resource_group_name} {obj_repr.name}'"
        )
        response = self.client.virtual_machines.begin_delete(
            obj_repr.resource_group_name, obj_repr.name
        )

        if not asynchronous:
            response.wait()
        return response

    def get_available_vm_sizes(self, region):
        """
        Get list of vm sizes available in the region

        @return:
        """

        return list(self.client.virtual_machine_sizes.list(region))

    def get_available_images(self, region):
        """
        Get list of vm sizes available in the region
        https://dev.to/holger/azure-sdk-for-python-retrieve-vm-image-details-30do
        #ret = list(self.client.virtual_machine_images.list_publishers(location=region))
        #offers = list(self.client.virtual_machine_images.list_offers(location=region, publisher_name="Canonical"))

        @return:
        """
        offer_name = "0001-com-ubuntu-pro-jammy"
        offer_name = "0001-com-ubuntu-server-jammy"
        skus = list(self.client.virtual_machine_images.list_skus(location=region,
                                                                 publisher_name="Canonical",
                                                                 offer=offer_name))
        ret = []
        for sku in skus:
            # 0001-com-ubuntu-server-jammy
            #
            ret += list(self.client.virtual_machine_images.list(location=region,
                                                                publisher_name="Canonical",
                                                                offer=offer_name, skus=sku.name))
        return ret

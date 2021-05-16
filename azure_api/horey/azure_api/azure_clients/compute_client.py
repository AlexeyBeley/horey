import pdb

from azure.mgmt.compute import ComputeManagementClient
from horey.azure_api.azure_clients.azure_client import AzureClient
from horey.azure_api.azure_service_entities.disk import Disk
from horey.azure_api.azure_service_entities.ssh_key import SSHKey
from horey.azure_api.azure_service_entities.virtual_machine import VirtualMachine


class ComputeClient(AzureClient):
    CLIENT_CLASS = ComputeManagementClient

    def __init__(self):
        super().__init__()

    def raw_create_virtual_machines(self, lst_args):
        """
        RESOURCE_GROUP_NAME, VM_NAME,
        {
            "location": LOCATION,
            "storage_profile": {
                "image_reference": {
                    "publisher": 'Canonical',
                    "offer": "UbuntuServer",
                    "sku": "16.04.0-LTS",
                    "version": "latest"
                }
            },
            "hardware_profile": {
                "vm_size": "Standard_DS1_v2"
            },
            "os_profile": {
                "computer_name": VM_NAME,
                "admin_username": USERNAME,
                "admin_password": PASSWORD
            },
            "network_profile": {
                "network_interfaces": [{
                    "id": nic_result.id,
                }]
            }
        }
        """
        response = self.client.virtual_machines.begin_create_or_update(*lst_args)
        return response

    def raw_create_subnet(self, lst_args):
        """

        """

        response = self.client.disks.begin_create_or_update(*lst_args)
        pdb.set_trace()
        return response

    def raw_create_ssh_key(self, lst_args):
        """

        """

        response = self.client.ssh_public_keys.create(*lst_args)
        return response

    def get_all_disks(self):
        return [Disk(obj.as_dict()) for obj in self.client.disks.list()]

    def get_all_ssh_keys(self, resource_group):
        return [SSHKey(obj.as_dict()) for obj in self.client.ssh_public_keys.list_by_resource_group(resource_group.name)]

    def get_all_virtual_machines(self, resource_group):
        return [VirtualMachine(obj.as_dict()) for obj in self.client.virtual_machines.list(resource_group.name)]

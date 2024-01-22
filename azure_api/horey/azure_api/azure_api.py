"""
Azure API

"""
# pylint: disable= too-many-instance-attributes, no-name-in-module
import json
from horey.azure_api.azure_clients.compute_client import ComputeClient
from horey.azure_api.azure_clients.resource_client import ResourceClient
from horey.azure_api.azure_clients.network_client import NetworkClient

from horey.common_utils.common_utils import CommonUtils
from horey.azure_api.base_entities.azure_account import AzureAccount
from horey.azure_api.azure_service_entities.resource_group import ResourceGroup
from horey.azure_api.azure_service_entities.virtual_network import VirtualNetwork
from horey.azure_api.azure_service_entities.ssh_key import SSHKey
from horey.azure_api.azure_service_entities.disk import Disk
from horey.azure_api.azure_service_entities.public_ip_address import PublicIpAddress
from horey.azure_api.azure_service_entities.nat_gateway import NatGateway
from horey.azure_api.azure_service_entities.network_interface import NetworkInterface
from horey.azure_api.azure_service_entities.network_security_group import (
    NetworkSecurityGroup,
)
from horey.azure_api.azure_service_entities.virtual_machine import VirtualMachine
from horey.azure_api.azure_service_entities.load_balancer import LoadBalancer


class AzureAPI:
    """
    Main class.

    """

    def __init__(self, configuration=None):
        self.compute_client = ComputeClient()
        self.resource_client = ResourceClient()
        self.network_client = NetworkClient()

        self.resource_groups = []
        self.virtual_machines = []
        self.disks = []
        self.nat_gateways = []
        self.load_balancers = []
        self.network_interfaces = []
        self.public_ip_addresses = []
        self.network_security_groups = []
        self.ssh_keys = []
        self.virtual_networks = []

        self.configuration = configuration
        self.init_configuration()

    def init_configuration(self):
        """
        Sets current active account from configuration
        """
        if self.configuration is None:
            return
        accounts = CommonUtils.load_object_from_module(
            self.configuration.accounts_file, "main"
        )
        AzureAccount.set_azure_account(accounts[self.configuration.azure_account])

    def init_disks(self, resource_group):
        """
        Request from API and init objects.

        :return:
        """

        objects = self.compute_client.get_all_disks(resource_group)
        self.disks = objects

    def init_nat_gateways(self, resource_group=None):
        """
        Request from API and init objects.

        :return:
        """
        self.nat_gateways = []
        if resource_group is not None:
            objects = self.network_client.get_all_nat_gateways(resource_group)
            self.nat_gateways = objects
            return

        if len(self.resource_groups) == 0:
            raise RuntimeError(
                "resource_groups must be inited before running init_nat_gateways"
            )

        for _resource_group in self.resource_groups:
            objects = self.network_client.get_all_nat_gateways(_resource_group)
            self.nat_gateways += objects

    def init_load_balancers(self):
        """
        Request from API and init objects.

        :return:
        """
        self.load_balancers = []
        if len(self.resource_groups) == 0:
            raise RuntimeError(
                "resource_groups must be inited before running init_load_balancers"
            )

        for resource_group in self.resource_groups:
            objects = self.network_client.get_all_load_balancers(resource_group)
            self.load_balancers += objects

    def init_network_interfaces(self, resource_group=None):
        """
        Request from API and init objects.

        :return:
        """

        self.network_interfaces = []
        if resource_group is not None:
            self.network_interfaces = self.network_client.get_all_network_interfaces(resource_group)
            return

        if len(self.resource_groups) == 0:
            raise RuntimeError(
                "resource_groups must be inited before running init_network_interfaces"
            )

        for _resource_group in self.resource_groups:
            objects = self.network_client.get_all_network_interfaces(_resource_group)
            self.network_interfaces += objects

    def init_public_ip_addresses(self, resource_group=None):
        """
        Request from API and init objects.

        :return:
        """
        self.public_ip_addresses = []
        if resource_group is not None:
            objects = self.network_client.get_all_public_ip_addresses(resource_group)
            self.public_ip_addresses += objects
            return

        if len(self.resource_groups) == 0:
            raise RuntimeError(
                "resource_groups must be inited before running init_public_ip_addresses"
            )

        for _resource_group in self.resource_groups:
            objects = self.network_client.get_all_public_ip_addresses(_resource_group)
            self.public_ip_addresses += objects

    def init_network_security_groups(self, resource_group=None):
        """
        Request from API and init objects.

        :return:
        """

        self.network_security_groups = []
        if resource_group is not None:
            self.network_security_groups = self.network_client.get_all_network_security_groups(
                resource_group
            )
            return

        if len(self.resource_groups) == 0:
            raise RuntimeError(
                "resource_groups must be inited before running init_network_security_groups"
            )

        for _resource_group in self.resource_groups:
            objects = self.network_client.get_all_network_security_groups(
                _resource_group
            )
            self.network_security_groups += objects

    def init_virtual_machines(self, resource_group=None):
        """
        Request from API and init objects.

        :return:
        """
        self.virtual_machines = []
        if resource_group is not None:
            self.virtual_machines = self.compute_client.get_all_virtual_machines(resource_group.name)
            return

        if len(self.resource_groups) == 0:
            raise RuntimeError(
                "resource_groups must be inited before running init_virtual_machines"
            )

        for _resource_group in self.resource_groups:
            objects = self.compute_client.get_all_virtual_machines(_resource_group.name)
            self.virtual_machines += objects

    def init_virtual_networks(self, resource_group=None):
        """
        Request from API and init objects.

        :return:
        """
        self.virtual_networks = []
        if resource_group is not None:
            self.virtual_networks = self.network_client.get_all_virtual_networks(resource_group)
            return

        if len(self.resource_groups) == 0:
            raise RuntimeError(
                "resource_groups must be inited before running init_virtual_networks"
            )

        for _resource_group in self.resource_groups:
            objects = self.network_client.get_all_virtual_networks(_resource_group)
            self.virtual_networks += objects

    def init_ssh_keys(self, resource_group=None):
        """
        Request from API and init objects.

        :return:
        """
        self.ssh_keys = []
        if resource_group is not None:
            self.ssh_keys = self.compute_client.get_all_ssh_keys(resource_group)
            return

        if len(self.resource_groups) == 0:
            raise RuntimeError(
                "resource_groups must be inited before running init_ssh_keys"
            )

        for _resource_group in self.resource_groups:
            objects = self.compute_client.get_all_ssh_keys(_resource_group)
            self.ssh_keys += objects

    def init_resource_groups(self):
        """
        Request from API and init objects.

        :return:
        """

        objects = self.resource_client.get_all_resource_groups()
        self.resource_groups = objects

    def cache_objects(self, objects, cache_file_path):
        """
        Save objects as serialized dicts.

        :param objects:
        :param cache_file_path:
        :return:
        """

        lst_dicts = [obj.convert_to_dict() for obj in objects]
        with open(cache_file_path, "w+", encoding="utf-8") as file_handler:
            json.dump(lst_dicts, file_handler, indent=4)

    def provision_resource_group(self, resource_group):
        """
        Create or update

        :param resource_group:
        :return:
        """

        response = self.resource_client.raw_create_resource_group(
            resource_group.generate_create_request()
        )
        resource_group.update_after_creation(response)

    def provision_virtual_network(self, virtual_network):
        """
        Create or update

        :param virtual_network:
        :return:
        """

        response = self.network_client.raw_create_virtual_networks(
            virtual_network.generate_create_request()
        )
        virtual_network.update_after_creation(response)

    def provision_ssh_key(self, ssh_key):
        """
        Create or update

        :param ssh_key:
        :return:
        """

        response = self.compute_client.raw_create_ssh_key(
            ssh_key.generate_create_request()
        )
        ssh_key.update_after_creation(response)

    def provision_disk(self, disk: Disk):
        """
        Create or update

        :param disk:
        :return:
        """

        response = self.compute_client.raw_create_disk(disk.generate_create_request())
        disk.update_after_creation(response)

    def delete_disk(self, disk):
        """
        Dispose the resource.

        :param disk:
        :return:
        """

        return self.compute_client.raw_delete_disk(disk.resource_group_name, disk.name)

    def dispose_virtual_machine(self, object_repr):
        """
        Dispose the resource.

        :param object_repr:
        :return:
        """

        return self.compute_client.dispose_virtual_machine(object_repr)

    def delete_network_interface(self, object_repr):
        """
        Dispose the resource.

        :param object_repr:
        :return:
        """

        return self.network_client.dispose_network_interface(object_repr)

    def delete_load_balancer(self, object_repr):
        """
        Dispose the resource.

        :param object_repr:
        :return:
        """

        return self.network_client.raw_delete_load_balancer(object_repr)

    def provision_public_ip_address(self, public_ip_address):
        """
        Create or update

        :param public_ip_address:
        :return:
        """
        response = self.network_client.raw_create_public_ip_addresses(
            public_ip_address.generate_create_request()
        )
        public_ip_address.update_after_creation(response)

    def dispose_public_ip_address(self, public_ip_address):
        """
        Delete if exists.

        :param public_ip_address:
        :return:
        """
        return self.network_client.dispose_public_ip_addresses(
            public_ip_address
        )

    def provision_nat_gateway(self, building_block):
        """
        Create or update

        :param building_block:
        :return:
        """

        response = self.network_client.raw_create_nat_gateway(
            building_block.generate_create_request()
        )
        building_block.update_after_creation(response)
        nat_gateways = self.network_client.get_all_nat_gateways(
            None, resource_group_name=building_block.resource_group_name
        )
        for nat_gateway in nat_gateways:
            if nat_gateway.id == building_block.id:
                return

    def provision_network_interface(self, network_interface):
        """
        Create or update

        :param network_interface:
        :return:
        """

        self.network_client.provision_network_interface(network_interface)

    def provision_network_security_group(self, building_block):
        """
        Create or update

        :param building_block:
        :return:
        """

        response = self.network_client.raw_create_network_security_group(
            building_block.generate_create_request()
        )
        building_block.update_after_creation(response)

    def provision_load_balancer(self, building_block):
        """
        Create or update

        :param building_block:
        :return:
        """

        response = self.network_client.raw_create_load_balancer(
            building_block.generate_create_request()
        )
        building_block.update_after_creation(response)

    def provision_virtual_machine(self, building_block):
        """
        Create or update

        :param building_block:
        :return:
        """

        self.compute_client.provision_virtual_machine(building_block)

    def provision(self, building_block):
        """
        Create or update

        :param building_block:
        :return:
        """

        if isinstance(building_block, ResourceGroup):
            self.provision_resource_group(building_block)
        elif isinstance(building_block, VirtualNetwork):
            self.provision_virtual_network(building_block)
        elif isinstance(building_block, SSHKey):
            self.provision_ssh_key(building_block)
        elif isinstance(building_block, Disk):
            self.provision_disk(building_block)
        elif isinstance(building_block, PublicIpAddress):
            self.provision_public_ip_address(building_block)
        elif isinstance(building_block, NatGateway):
            self.provision_nat_gateway(building_block)
        elif isinstance(building_block, NetworkInterface):
            self.provision_network_interface(building_block)
        elif isinstance(building_block, NetworkSecurityGroup):
            self.provision_network_security_group(building_block)
        elif isinstance(building_block, VirtualMachine):
            self.provision_virtual_machine(building_block)
        elif isinstance(building_block, LoadBalancer):
            self.provision_load_balancer(building_block)
        else:
            raise NotImplementedError(
                f"Not yet implemented deployment for {type(building_block)}"
            )

    def delete_resource_group(self, resource_group):
        """
        Dispose resource

        :param resource_group:
        :return:
        """

        self.resource_client.raw_delete_resource_group(resource_group.name)

    def delete(self, building_block):
        """
        Dispose resource.

        :param building_block:
        :return:
        """

        if isinstance(building_block, ResourceGroup):
            self.delete_resource_group(building_block)
        elif isinstance(building_block, Disk):
            self.delete_disk(building_block)
        elif isinstance(building_block, VirtualMachine):
            self.delete_virtual_machine(building_block)
        elif isinstance(building_block, LoadBalancer):
            self.delete_load_balancer(building_block)
        elif isinstance(building_block, NetworkInterface):
            self.delete_network_interface(building_block)
        else:
            raise NotImplementedError(
                f"Not yet implemented deployment for {type(building_block)}"
            )

    def resize_vm_disk(self, vm, disk_size_gb):
        """
        Resize VM managed disk
        vm.storage_profile["os_disk"]["disk_size_gb"]
        objects[0].storage_profile["os_disk"]["managed_disk"]["id"]

        :param vm:
        :return:
        """

        self.compute_client.stop_vm(vm)
        disk_id = vm.storage_profile["os_disk"]["managed_disk"]["id"]
        lst_disk_id = disk_id.split("/")
        if lst_disk_id[3] != "resourceGroups":
            raise RuntimeError(lst_disk_id)
        resource_group_name = lst_disk_id[4]
        disk_name = lst_disk_id[-1]
        disk = self.compute_client.get_disk(resource_group_name, disk_name)
        disk.disk_size_gb = disk_size_gb
        self.provision_disk(disk)
        self.compute_client.start_vm(vm)

    def print_vm_disk_sizes(self, resource_group):
        """
        All OS-disK sizes.

        :return:
        """

        for disk in self.compute_client.get_all_disks(resource_group):
            print(f"{disk.name} - {disk.disk_size_gb} GB")

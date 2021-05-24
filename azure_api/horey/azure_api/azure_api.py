import json
import pdb
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
from horey.azure_api.azure_service_entities.network_security_group import NetworkSecurityGroup
from horey.azure_api.azure_service_entities.virtual_machine import VirtualMachine
from horey.azure_api.azure_service_entities.load_balancer import LoadBalancer


class AzureAPI:
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
        accounts = CommonUtils.load_object_from_module(self.configuration.accounts_file, "main")
        AzureAccount.set_azure_account(accounts[self.configuration.azure_account])
    
    def init_disks(self):
        objects = self.compute_client.get_all_disks()
        self.disks += objects
    
    def init_nat_gateways(self):
        if len(self.resource_groups) == 0:
            raise RuntimeError(f"resource_groups must be inited before running init_nat_gateways")

        for resource_group in self.resource_groups:
            objects = self.network_client.get_all_nat_gateways(resource_group)
            self.nat_gateways += objects
  
    def init_load_balancers(self):
        if len(self.resource_groups) == 0:
            raise RuntimeError(f"resource_groups must be inited before running init_load_balancers")

        for resource_group in self.resource_groups:
            objects = self.network_client.get_all_load_balancers(resource_group)
            self.load_balancers += objects
        
    def init_network_interfaces(self):
        if len(self.resource_groups) == 0:
            raise RuntimeError(f"resource_groups must be inited before running init_network_interfaces")

        for resource_group in self.resource_groups:
            objects = self.network_client.get_all_network_interfaces(resource_group)
            self.network_interfaces += objects
        
    def init_public_ip_addresses(self):
        if len(self.resource_groups) == 0:
            raise RuntimeError(f"resource_groups must be inited before running init_public_ip_addresses")

        for resource_group in self.resource_groups:
            objects = self.network_client.get_all_public_ip_addresses(resource_group)
            self.public_ip_addresses += objects
    
    def init_network_security_groups(self):
        if len(self.resource_groups) == 0:
            raise RuntimeError(f"resource_groups must be inited before running init_network_security_groups")

        for resource_group in self.resource_groups:
            objects = self.network_client.get_all_network_security_groups(resource_group)
            self.network_security_groups += objects
        
    def init_virtual_machines(self):
        if len(self.resource_groups) == 0:
            raise RuntimeError(f"resource_groups must be inited before running init_virtual_machines")

        for resource_group in self.resource_groups:
            objects = self.compute_client.get_all_virtual_machines(resource_group)
            self.virtual_machines += objects
    
    def init_virtual_networks(self):
        if len(self.resource_groups) == 0:
            raise RuntimeError(f"resource_groups must be inited before running init_virtual_networks")

        for resource_group in self.resource_groups:
            objects = self.network_client.get_all_virtual_networks(resource_group)
            self.virtual_networks += objects
            
    def init_ssh_keys(self):
        if len(self.resource_groups) == 0:
            raise RuntimeError(f"resource_groups must be inited before running init_ssh_keys")

        for resource_group in self.resource_groups:
            objects = self.compute_client.get_all_ssh_keys(resource_group)
            self.ssh_keys += objects
    
    def init_resource_groups(self):
        objects = self.resource_client.get_all_resource_groups()
        self.resource_groups += objects

    def cache_objects(self, objects, cache_file_path):
        lst_dicts = [obj.convert_to_dict() for obj in objects]
        with open(cache_file_path, "w+") as file_handler:
            json.dump(lst_dicts, file_handler, indent=4)

    def deploy_resource_group(self, resource_group):
        response = self.resource_client.raw_create_resource_group(resource_group.generate_create_request())
        resource_group.update_after_creation(response)

    def deploy_virtual_network(self, virtual_network):
        response = self.network_client.raw_create_virtual_networks(virtual_network.generate_create_request())
        virtual_network.update_after_creation(response)

    def deploy_ssh_key(self, ssh_key):
        response = self.compute_client.raw_create_ssh_key(ssh_key.generate_create_request())
        ssh_key.update_after_creation(response)

    def deploy_disk(self, disk):
        response = self.compute_client.raw_create_disk(disk.generate_create_request())
        disk.update_after_creation(response)

    def delete_disk(self, disk):
        return self.compute_client.raw_delete_disk(disk.resource_group_name, disk.name)

    def delete_virtual_machine(self, object_repr):
        return self.compute_client.raw_delete_virtual_machine(object_repr)

    def delete_network_interface(self, object_repr):
        return self.network_client.raw_delete_network_interface(object_repr)

    def delete_load_balancer(self, object_repr):
        return self.network_client.raw_delete_load_balancer(object_repr)

    def deploy_public_ip_address(self, public_ip_address):
        response = self.network_client.raw_create_public_ip_addresses(public_ip_address.generate_create_request())
        public_ip_address.update_after_creation(response)

    def deploy_nat_gateway(self, building_block):
        response = self.network_client.raw_create_nat_gateway(building_block.generate_create_request())
        building_block.update_after_creation(response)

    def deploy_network_interface(self, building_block):
        response = self.network_client.raw_create_network_interfaces(building_block.generate_create_request())
        building_block.update_after_creation(response)

    def deploy_network_security_group(self, building_block):
        response = self.network_client.raw_create_network_security_group(building_block.generate_create_request())
        building_block.update_after_creation(response)

    def deploy_load_balancer(self, building_block):
        response = self.network_client.raw_create_load_balancer(building_block.generate_create_request())
        building_block.update_after_creation(response)

    def deploy_virtual_machine(self, building_block):
        response = self.compute_client.raw_create_virtual_machines(building_block.generate_create_request())
        building_block.update_after_creation(response)

    def deploy(self, building_block):
        if isinstance(building_block, ResourceGroup):
            self.deploy_resource_group(building_block)
        elif isinstance(building_block, VirtualNetwork):
            self.deploy_virtual_network(building_block)
        elif isinstance(building_block, SSHKey):
            self.deploy_ssh_key(building_block)
        elif isinstance(building_block, Disk):
            self.deploy_disk(building_block)
        elif isinstance(building_block, PublicIpAddress):
            self.deploy_public_ip_address(building_block)
        elif isinstance(building_block, NatGateway):
            self.deploy_nat_gateway(building_block)
        elif isinstance(building_block, NetworkInterface):
            self.deploy_network_interface(building_block)
        elif isinstance(building_block, NetworkSecurityGroup):
            self.deploy_network_security_group(building_block)
        elif isinstance(building_block, VirtualMachine):
            self.deploy_virtual_machine(building_block)
        elif isinstance(building_block, LoadBalancer):
            self.deploy_load_balancer(building_block)
        else:
            raise NotImplementedError(f"Not yet implemented deployment for {type(building_block)}")

    def delete_resource_group(self, resource_group):
        self.resource_client.raw_delete_resource_group(resource_group.name)

    def delete(self, building_block):
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
            raise NotImplementedError(f"Not yet implemented deployment for {type(building_block)}")
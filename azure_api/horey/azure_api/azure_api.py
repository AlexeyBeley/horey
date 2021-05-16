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
            json.dump(lst_dicts, file_handler)

    def deploy_resource_group(self, resource_group):
        response = self.resource_client.raw_create_resource_group(resource_group.generate_create_request())
        resource_group.update_after_creation(response)

    def deploy_virtual_network(self, virtual_network):
        response = self.network_client.raw_create_virtual_networks(virtual_network.generate_create_request())
        virtual_network.update_after_creation(response)

    def deploy_ssh_key(self, ssh_key):
        response = self.compute_client.raw_create_ssh_key(ssh_key.generate_create_request())
        ssh_key.update_after_creation(response)

    def deploy(self, building_block):
        if isinstance(building_block, ResourceGroup):
            self.deploy_resource_group(building_block)
        elif isinstance(building_block, VirtualNetwork):
            self.deploy_virtual_network(building_block)
        elif isinstance(building_block, SSHKey):
            self.deploy_ssh_key(building_block)
        else:
            raise NotImplementedError(f"Not yet implemented deployment for {type(building_block)}")

    def delete_resource_group(self, resource_group):
        delete_async_operation = self.resource_client.raw_delete_resource_group(resource_group.name)
        delete_async_operation.wait()

    def delete(self, building_block):
        if isinstance(building_block, ResourceGroup):
            self.delete_resource_group(building_block)
        else:
            raise NotImplementedError(f"Not yet implemented deployment for {type(building_block)}")
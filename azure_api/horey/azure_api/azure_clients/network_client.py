import pdb

from azure.mgmt.network import NetworkManagementClient
from horey.azure_api.azure_clients.azure_client import AzureClient
from horey.azure_api.azure_service_entities.load_balancer import LoadBalancer
from horey.azure_api.azure_service_entities.nat_gateway import NatGateway
from horey.azure_api.azure_service_entities.network_interface import NetworkInterface
from horey.azure_api.azure_service_entities.public_ip_address import PublicIpAddress
from horey.azure_api.azure_service_entities.network_security_group import NetworkSecurityGroup


class NetworkClient(AzureClient):
    CLIENT_CLASS = NetworkManagementClient

    def __init__(self):
        super().__init__()

    def raw_create_virtual_networks(self, lst_args):
        """
        RESOURCE_GROUP_NAME,
        VNET_NAME,
        {
            "location": LOCATION,
            "address_space": {
                "address_prefixes": ["10.0.0.0/16"]
            }
        }
        """
        response = self.client.virtual_networks.begin_create_or_update(*lst_args)
        return response

    def raw_create_subnet(self, lst_args):
        """
        RESOURCE_GROUP_NAME,
        VNET_NAME, SUBNET_NAME,
        { "address_prefix": "10.0.0.0/24" }
        """
        response = self.client.subnet.begin_create_or_update(*lst_args)
        return response

    def raw_create_public_ip_addresses(self, lst_args):
        """
        RESOURCE_GROUP_NAME,
        IP_NAME,
        {
            "location": LOCATION,
            "sku": { "name": "Standard" },
            "public_ip_allocation_method": "Static",
            "public_ip_address_version" : "IPV4"
        }
        """
        response = self.client.public_ip_addresses.begin_create_or_update(*lst_args)
        return response

    def raw_create_network_interfaces(self, lst_args):
        """
        RESOURCE_GROUP_NAME,
        NIC_NAME,
        {
            "location": LOCATION,
            "ip_configurations": [ {
                "name": IP_CONFIG_NAME,
                "subnet": { "id": subnet_result.id },
                "public_ip_address": {"id": ip_address_result.id }
            }]
        }}
        """
        response = self.client.network_interfaces.begin_create_or_update(*lst_args)
        return response

    def raw_create_nat_gateway(self, lst_args):
        """
        RESOURCE_GROUP_NAME,
        NIC_NAME,
        {
            "location": LOCATION,
            "ip_configurations": [ {
                "name": IP_CONFIG_NAME,
                "subnet": { "id": subnet_result.id },
                "public_ip_address": {"id": ip_address_result.id }
            }]
        }}
        """
        response = self.client.nat_gateway.begin_create_or_update(*lst_args)
        return response

    def raw_create_load_balancer(self, lst_args):
        """

        """
        pdb.set_trace()
        response = self.client.load_balancers.begin_create_or_update(*lst_args)
        return response

    def raw_create_security_groups(self, lst_args):
        """
        #nsg = network_client.network_security_groups.begin_create_or_update(resource_group_name, "testnsg", parameters=nsg_params)
        """
        pdb.set_trace()
        response = self.client.network_security_groups.begin_create_or_update(*lst_args)
        return response

    def get_all_load_balancers(self, resource_group):
        return [LoadBalancer(obj.as_dict()) for obj in self.client.load_balancers.list(resource_group.name)]

    def get_all_nat_gateways(self, resource_group):
        return [NatGateway(obj.as_dict()) for obj in self.client.nat_gateways.list(resource_group.name)]

    def get_all_network_interfaces(self, resource_group):
        return [NetworkInterface(obj.as_dict()) for obj in self.client.nat_gateways.list(resource_group.name)]

    def get_all_public_ip_addresses(self, resource_group):
        return [PublicIpAddress(obj.as_dict()) for obj in self.client.public_ip_addresses.list(resource_group.name)]

    def get_all_network_security_groups(self, network_resource_group):
        return [NetworkSecurityGroup(obj.as_dict()) for obj in self.client.network_security_groups.list(network_resource_group.name)]

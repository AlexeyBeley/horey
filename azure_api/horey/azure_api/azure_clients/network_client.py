"""
Azure API CLient
"""

from azure.mgmt.network import NetworkManagementClient
from horey.azure_api.azure_clients.azure_client import AzureClient
from horey.azure_api.azure_service_entities.load_balancer import LoadBalancer
from horey.azure_api.azure_service_entities.nat_gateway import NatGateway
from horey.azure_api.azure_service_entities.network_interface import NetworkInterface
from horey.azure_api.azure_service_entities.public_ip_address import PublicIpAddress
from horey.azure_api.azure_service_entities.network_security_group import (
    NetworkSecurityGroup,
)
from horey.azure_api.azure_service_entities.virtual_network import VirtualNetwork

from horey.h_logger import get_logger

logger = get_logger()


class NetworkClient(AzureClient):
    """
    Main class
    """

    CLIENT_CLASS = NetworkManagementClient

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
        logger.info(f"Begin subnet creation: '{lst_args[0]} {lst_args[1]}'")
        # pylint: disable = no-member
        response = self.client.subnet.begin_create_or_update(*lst_args)
        return response

    def provision_public_ip_addresses(self, public_ip_address):
        """
        Standard.

        :param public_ip_address:
        :return:
        """

        response = self.raw_create_public_ip_addresses(
            public_ip_address.generate_create_request()
        )
        public_ip_address.update_after_creation(response)

    def raw_create_public_ip_addresses(self, lst_args):
        """
        Update/create ip address

        :param lst_args:
        :return:
        """
        logger.info(f"Public ip address create/update: '{lst_args[0]} {lst_args[1]}'")
        response = self.client.public_ip_addresses.begin_create_or_update(*lst_args)
        response.wait()
        return response.result()

    def dispose_public_ip_addresses(self, public_ip, asynchronous=False):
        """
        resource_group_name: str, public_ip_address_name

        :param public_ip:
        :param asynchronous:
        :return:
        """

        logger.info(f"Begin public ip address deletion: '{public_ip.resource_group_name} {public_ip.name}'")
        response = self.client.public_ip_addresses.begin_delete(public_ip.resource_group_name, public_ip.name)
        if not asynchronous:
            response.wait()
        return response

    def provision_network_interface(self, network_interface: NetworkInterface):
        """
        Standard.

        :param network_interface:
        :return:
        """

        request = network_interface.generate_create_request()
        response = self.raw_create_network_interfaces(request)
        network_interface.update_after_creation(response)

    def raw_create_network_interfaces(self, lst_args):
        """
        Standard.

        :param lst_args:
        :return:
        """

        logger.info(f"Network interface create/update: '{lst_args[0]} {lst_args[1]}'")
        response = self.client.network_interfaces.begin_create_or_update(*lst_args)
        response.wait()
        return response.result()

    def raw_create_nat_gateway(self, lst_args):
        """
        Standard.

        :param lst_args:
        :return:
        """
        logger.info(f"Begin nat gateway creation: '{lst_args[0]} {lst_args[1]}'")
        response = self.client.nat_gateways.begin_create_or_update(*lst_args)
        return response.result()

    def raw_create_load_balancer(self, lst_args):
        """
        Standard.

        :param lst_args:
        :return:
        """
        logger.info(f"Begin load balancer creation: '{lst_args[0]} {lst_args[1]}'")
        response = self.client.load_balancers.begin_create_or_update(*lst_args)
        response.wait()
        return response.result()

    def raw_delete_load_balancer(self, obj_repr):
        """
        Standard.

        :param obj_repr:
        :return:
        """

        logger.info(
            f"Begin load balancer deletion: '{obj_repr.resource_group_name} {obj_repr.name}'"
        )
        response = self.client.load_balancers.begin_delete(
            obj_repr.resource_group_name, obj_repr.name
        )
        response.wait()
        return response.status() == "Succeeded"

    def dispose_network_interface(self, obj_repr, asynchronous=False):
        """
        Delete interfaces.

        :param obj_repr:
        :param asynchronous:
        :return:
        """
        logger.info(
            f"Begin network interface deletion: '{obj_repr.resource_group_name} {obj_repr.name}'"
        )
        response = self.client.network_interfaces.begin_delete(
            obj_repr.resource_group_name, obj_repr.name
        )
        if not asynchronous:
            response.wait()
        return response

    def raw_create_network_security_group(self, lst_args):
        """
        #nsg = network_client.network_security_groups.begin_create_or_update(resource_group_name, "testnsg", parameters=nsg_params)
        """
        logger.info(
            f"Begin network security group creation: '{lst_args[0]} {lst_args[1]}'"
        )
        response = self.client.network_security_groups.begin_create_or_update(*lst_args)
        response.wait()
        return response.result()

    def get_all_load_balancers(self, resource_group):
        """
        Standard

        :param resource_group:
        :return:
        """

        return [
            LoadBalancer(obj.as_dict())
            for obj in self.client.load_balancers.list(resource_group.name)
        ]

    def get_all_nat_gateways(self, resource_group, resource_group_name=None):
        """
        Standard

        :param resource_group:
        :param resource_group_name:
        :return:
        """

        if resource_group_name is None:
            resource_group_name = resource_group.name

        return [
            NatGateway(obj.as_dict())
            for obj in self.client.nat_gateways.list(resource_group_name)
        ]

    def get_all_network_interfaces(self, resource_group, resource_group_name=None):
        """
        Standard

        :param resource_group:
        :param resource_group_name:
        :return:
        """

        if resource_group_name is None:
            resource_group_name = resource_group.name

        return [
            NetworkInterface(obj.as_dict())
            for obj in self.client.network_interfaces.list(resource_group_name)
        ]

    def get_all_public_ip_addresses(self, resource_group, resource_group_name=None):
        """
        Standard

        :param resource_group_name:
        :param resource_group:
        :return:
        """

        resource_group_name = resource_group_name or resource_group.name

        return [
            PublicIpAddress(obj.as_dict())
            for obj in self.client.public_ip_addresses.list(resource_group_name)
        ]

    def get_all_network_security_groups(self, network_resource_group):
        """
        Standard

        :param network_resource_group:
        :return:
        """

        return [
            NetworkSecurityGroup(obj.as_dict())
            for obj in self.client.network_security_groups.list(
                network_resource_group.name
            )
        ]

    def get_all_virtual_networks(self, resource_group):
        """
        Standard

        :param resource_group:
        :return:
        """
        return [
            VirtualNetwork(obj.as_dict())
            for obj in self.client.virtual_networks.list(resource_group.name)
        ]

"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""

import sys

sys.path.insert(0, "/Users/alexey.beley/private/horey/azure_api")

import pytest
from horey.azure_api.azure_api import AzureAPI
from horey.h_logger import get_logger
from horey.azure_api.azure_api_configuration_policy import AzureAPIConfigurationPolicy


logger = get_logger()


configuration = AzureAPIConfigurationPolicy()


azure_api = AzureAPI()

# pylint: disable= missing-function-docstring


# region done
@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_init_and_cache_resource_groups():
    azure_api.init_resource_groups()
    azure_api.cache_objects(
        azure_api.resource_groups, configuration.azure_api_resource_groups_cache_file
    )
    logger.info(f"len(iam_policies) = {len(azure_api.resource_groups)}")
    assert isinstance(azure_api.resource_groups, list)


@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_init_and_cache_disks():
    azure_api.init_disks()
    azure_api.cache_objects(azure_api.disks, configuration.azure_api_disks_cache_file)
    logger.info(f"len(disks) = {len(azure_api.disks)}")
    assert isinstance(azure_api.disks, list)


@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_init_and_cache_load_balancers():
    azure_api.init_resource_groups()
    azure_api.init_load_balancers()
    azure_api.cache_objects(
        azure_api.load_balancers, configuration.azure_api_load_balancers_cache_file
    )
    logger.info(f"len(load_balancers) = {len(azure_api.load_balancers)}")
    assert isinstance(azure_api.load_balancers, list)


@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_init_and_cache_nat_gateways():
    azure_api.init_resource_groups()
    azure_api.init_nat_gateways()
    azure_api.cache_objects(
        azure_api.nat_gateways, configuration.azure_api_nat_gateways_cache_file
    )
    logger.info(f"len(nat_gateways) = {len(azure_api.nat_gateways)}")
    assert isinstance(azure_api.nat_gateways, list)


@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_init_and_cache_network_interfaces():
    azure_api.init_resource_groups()
    azure_api.init_network_interfaces()
    azure_api.cache_objects(
        azure_api.network_interfaces,
        configuration.azure_api_network_interfaces_cache_file,
    )
    logger.info(f"len(network_interfaces) = {len(azure_api.network_interfaces)}")
    assert isinstance(azure_api.network_interfaces, list)


@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_init_and_cache_public_ip_addresses():
    azure_api.init_resource_groups()
    azure_api.init_public_ip_addresses()
    azure_api.cache_objects(
        azure_api.public_ip_addresses,
        configuration.azure_api_public_ip_addresses_cache_file,
    )
    logger.info(f"len(public_ip_addresss) = {len(azure_api.public_ip_addresses)}")
    assert isinstance(azure_api.public_ip_addresses, list)


@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_init_and_cache_network_security_groups():
    azure_api.init_resource_groups()
    azure_api.init_network_security_groups()
    azure_api.cache_objects(
        azure_api.network_security_groups,
        configuration.azure_api_network_security_groups_cache_file,
    )
    logger.info(
        f"len(network_security_groups) = {len(azure_api.network_security_groups)}"
    )
    assert isinstance(azure_api.network_security_groups, list)


@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_init_and_cache_ssh_keys():
    azure_api.init_resource_groups()
    azure_api.init_ssh_keys()
    azure_api.cache_objects(
        azure_api.ssh_keys, configuration.azure_api_ssh_keys_cache_file
    )
    logger.info(f"len(ssh_keys) = {len(azure_api.ssh_keys)}")
    assert isinstance(azure_api.ssh_keys, list)


@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_init_and_cache_virtual_machines():
    azure_api.init_resource_groups()
    azure_api.init_virtual_machines()
    azure_api.cache_objects(
        azure_api.virtual_machines, configuration.azure_api_virtual_machines_cache_file
    )
    logger.info(f"len(virtual_machines) = {len(azure_api.virtual_machines)}")
    assert isinstance(azure_api.virtual_machines, list)


@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_init_and_cache_virtual_networks():
    azure_api.init_resource_groups()
    azure_api.init_virtual_networks()
    azure_api.cache_objects(
        azure_api.virtual_networks, configuration.azure_api_virtual_networks_cache_file
    )
    logger.info(f"len(virtual_networks) = {len(azure_api.virtual_networks)}")
    assert isinstance(azure_api.virtual_networks, list)


if __name__ == "__main__":
    # test_init_and_cache_resource_groups()
    # test_init_and_cache_disks()
    #test_init_and_cache_load_balancers()
    # test_init_and_cache_nat_gateways()
    #test_init_and_cache_network_interfaces()
    test_init_and_cache_public_ip_addresses()
    #test_init_and_cache_network_security_groups()
    # test_init_and_cache_ssh_keys()
    #test_init_and_cache_virtual_machines()
    # test_init_and_cache_virtual_networks()

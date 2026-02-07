"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""

import pytest
from horey.azure_api.azure_clients.network_client import NetworkClient
from horey.azure_api.base_entities.azure_account import AzureAccount
from horey.azure_api.base_entities.region import Region
from horey.azure_api.azure_api_configuration_policy import AzureAPIConfigurationPolicy


configuration = AzureAPIConfigurationPolicy()

network_client = NetworkClient()


@pytest.mark.done
def test_get_all_virtual_machines():
    ret = network_client.get_all_nat_gateways(None, resource_group_name=mock_values["network_client_resource_group_name"])
    assert len(ret) > 0


@pytest.mark.done
def test_get_all_public_ip_addresses():
    ret = network_client.get_all_public_ip_addresses(None, resource_group_name=mock_values["network_client_resource_group_name"])
    assert len(ret) > 0


@pytest.mark.done
def test_get_all_network_interfaces():
    ret = network_client.get_all_network_interfaces(None, resource_group_name=mock_values["network_client_resource_group_name"])
    assert len(ret) > 0

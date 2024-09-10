"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""

import os
import pytest
from horey.azure_api.azure_clients.network_client import NetworkClient
from horey.azure_api.base_entities.azure_account import AzureAccount
from horey.azure_api.base_entities.region import Region
from horey.azure_api.azure_api_configuration_policy import AzureAPIConfigurationPolicy
from horey.common_utils.common_utils import CommonUtils


mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "azure_api_mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

configuration = AzureAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "..",
        "ignore",
        "azure_api_configuration_values.py",
    )
)
configuration.init_from_file()

network_client = NetworkClient()
accounts = CommonUtils.load_object_from_module(
            configuration.accounts_file, "main"
        )
AzureAccount.set_azure_account(accounts[configuration.azure_account])
region = Region.get_region("centralus")
# pylint: disable= missing-function-docstring


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

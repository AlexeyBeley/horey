"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""

import os
import pytest
from horey.azure_api.azure_clients.compute_client import ComputeClient
from horey.azure_api.azure_service_entities.virtual_machine import VirtualMachine
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

compute_client = ComputeClient()
accounts = CommonUtils.load_object_from_module(
            configuration.accounts_file, "main"
        )
AzureAccount.set_azure_account(accounts[configuration.azure_account])
region = Region.get_region("uaenorth")
# pylint: disable= missing-function-docstring


@pytest.mark.done
def test_get_available_vm_sizes():
    ret = compute_client.get_available_vm_sizes(region)
    assert ret is not None


@pytest.mark.done
def test_get_available_images():
    ret = compute_client.get_available_images(region)
    assert ret is not None


@pytest.mark.done
def test_get_all_virtual_machines():
    ret = compute_client.get_all_virtual_machines(mock_values["resource_group_name"])
    assert len(ret) > 0


@pytest.mark.done
def test_update_virtual_machine_information():
    vm = VirtualMachine({})
    vm.name = mock_values["compute_client_vm_name"]
    vm.resource_group_name = mock_values["resource_group_name"]
    assert compute_client.update_virtual_machine_information(vm)
    assert vm.provisioning_state == "Succeeded"

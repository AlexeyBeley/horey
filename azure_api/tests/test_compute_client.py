"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""

import pytest
from horey.azure_api.azure_service_entities.disk import Disk
from horey.azure_api.azure_service_entities.virtual_machine import VirtualMachine
from horey.azure_api.base_entities.region import Region
from horey.azure_api.azure_api import AzureAPI, AzureAPIConfigurationPolicy
from pathlib import Path
from horey.common_utils.common_utils import CommonUtils
mock_values_file_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_azure_api_mocks.py"
mock_values = CommonUtils.load_module(mock_values_file_path)

# pylint: disable= missing-function-docstring

@pytest.fixture(name="azure_api_configuration")
def fixture_azure_api_configuration():
    config = AzureAPIConfigurationPolicy()
    config.accounts_file = mock_values.azure_api_configuration_file_path
    config.azure_account = "test"
    config.azure_api_cache_dir = "/tmp/azure_api"
    yield config

@pytest.fixture(name="azure_api")
def fixture_azure_api(azure_api_configuration):
    azure_api = AzureAPI(configuration=azure_api_configuration)
    yield azure_api

@pytest.fixture(name="compute_client")
def compute_client_fixture(azure_api):
    return azure_api.compute_client

@pytest.mark.unit
def test_get_available_vm_sizes(compute_client):
    ret = compute_client.get_available_vm_sizes(Region.get_region("uksouth"))
    print(f"# Available vm sizes: {ret}")
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


@pytest.mark.unit
def test_provision_disk(compute_client):
    disk = Disk({})
    disk.name = "test_disk"
    disk.resource_group_name = mock_values.network_client_resource_group_name
    disk.disk_size_gb = 30
    disk.location = mock_values.location
    disk.sku = {"name": "Standard_LRS"}
    disk.tags = {"test": "tes"}
    ret = compute_client.provision_disk(disk)
    print(f"# Available vm sizes: {ret}")
    assert ret is not None


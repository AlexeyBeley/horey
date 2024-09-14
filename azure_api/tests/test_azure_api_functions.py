"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""

import os
import pytest
from horey.azure_api.azure_api import AzureAPI
from horey.h_logger import get_logger
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

azure_api = AzureAPI(configuration=configuration)

# pylint: disable= missing-function-docstring


@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_init_virtual_machines():
    azure_api.init_resource_groups()
    azure_api.init_virtual_machines()
    logger.info(f"len(virtual_machines) = {len(azure_api.virtual_machines)}")
    assert isinstance(azure_api.virtual_machines, list)


def test_resize_vm_disk():
    vm = azure_api.compute_client.get_vm(mock_values["resize_vm_rg_name"], mock_values["resize_vm_name"])
    disk_size_gb = 200
    azure_api.resize_vm_disk(vm, disk_size_gb)


def test_print_vm_disk_sizes():
    azure_api.print_vm_disk_sizes()


if __name__ == "__main__":
    #test_init_virtual_machines()
    test_print_vm_disk_sizes()

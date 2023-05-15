"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""

import os
from horey.azure_api.azure_clients.compute_client import ComputeClient
from horey.azure_api.base_entities.azure_account import AzureAccount
from horey.azure_api.base_entities.region import Region
from horey.h_logger import get_logger
from horey.azure_api.azure_api_configuration_policy import AzureAPIConfigurationPolicy
from horey.common_utils.common_utils import CommonUtils


mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "azure_api_mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


# Uncomment next line to save error lines to /tmp/error.log
# configuration_values_file_full_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py")
configuration_values_file_full_path = None
logger = get_logger(
    configuration_values_file_full_path=configuration_values_file_full_path
)

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


def test_get_available_vm_sizes():
    ret = compute_client.get_available_vm_sizes(region)
    assert ret is not None


def test_get_available_images():
    ret = compute_client.get_available_images(region)
    assert ret is not None


if __name__ == "__main__":
    #test_get_available_vm_sizes()
    test_get_available_images()

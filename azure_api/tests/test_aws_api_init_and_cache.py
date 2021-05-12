"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""

import sys
sys.path.insert(0, "/Users/alexey.beley/private/horey/azure_api")
import pdb

import pytest
import os
from horey.azure_api.azure_api import AzureAPI
from horey.h_logger import get_logger
from horey.azure_api.azure_api_configuration_policy import AzureAPIConfigurationPolicy
#Uncomment next line to save error lines to /tmp/error.log
#configuration_values_file_full_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py")
configuration_values_file_full_path = None
logger = get_logger(configuration_values_file_full_path=configuration_values_file_full_path)

configuration = AzureAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "azure_api_configuration_values.py"))
configuration.init_from_file()

azure_api = AzureAPI(configuration=configuration)


# region done
@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_init_and_cache_resource_groups():
    azure_api.init_resource_groups()
    azure_api.cache_objects(azure_api.resource_groups, configuration.azure_api_resource_groups_cache_file)
    logger.info(f"len(iam_policies) = {len(azure_api.resource_groups)}")
    assert isinstance(azure_api.resource_groups, list)




if __name__ == "__main__":
    test_init_and_cache_resource_groups()

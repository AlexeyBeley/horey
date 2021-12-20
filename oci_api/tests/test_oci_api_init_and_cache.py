"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""

import sys
import pdb

import pytest
import os
from horey.oci_api.oci_api import OCIAPI
from horey.h_logger import get_logger
from horey.oci_api.oci_api_configuration_policy import OCIAPIConfigurationPolicy
#Uncomment next line to save error lines to /tmp/error.log
#configuration_values_file_full_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py")
configuration_values_file_full_path = None
logger = get_logger(configuration_values_file_full_path=configuration_values_file_full_path)

configuration = OCIAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "oci_api_configuration_values.py"))
configuration.init_from_file()

oci_api = OCIAPI(configuration=configuration)


# region done
@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_init_and_cache_vm_hosts():

    oci_api.init_vm_hosts()
    oci_api.cache_objects(oci_api.vm_hosts, configuration.oci_api_vm_hosts_cache_file)
    logger.info(f"len(iam_policies) = {len(oci_api.vm_hosts)}")
    assert isinstance(oci_api.vm_hosts, list)


if __name__ == "__main__":
    test_init_and_cache_vm_hosts()


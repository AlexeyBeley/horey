"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""
import pdb

import pytest
import os
from horey.oci_api.oci_clients.compute_client import ComputeClient
from horey.h_logger import get_logger
from horey.oci_api.oci_api_configuration_policy import OCIAPIConfigurationPolicy
logger = get_logger()

configuration = OCIAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "oci_api_configuration_values.py"))
configuration.init_from_file()


# region done
@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_provision_vm():
    client = ComputeClient()
    pdb.set_trace()
    client.provision_bucket()


if __name__ == "__main__":
    test_provision_vm()


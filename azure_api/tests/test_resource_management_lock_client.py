"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""

import pytest
from horey.azure_api.azure_clients.resource_management_lock_client import ResourceManagementLockClient


# pylint: disable= missing-function-docstring


@pytest.mark.wip
def test_client():
    assert ResourceManagementLockClient()


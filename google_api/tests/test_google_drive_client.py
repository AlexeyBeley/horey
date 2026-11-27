"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""
import pdb

import pytest
import os
from horey.google_api.google_clients.google_drive_client import GoogleDriveClient
from horey.h_logger import get_logger
from horey.google_api.google_api_configuration_policy import (
    GoogleAPIConfigurationPolicy,
)

logger = get_logger()

configuration = GoogleAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "..",
        "ignore",
        "google_api_configuration_values.py",
    )
)
configuration.init_from_file()


# region done
@pytest.mark.skip(reason="")
def test_list_files():
    client = GoogleDriveClient()
    client.list_files()


if __name__ == "__main__":
    test_list_files()

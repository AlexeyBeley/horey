"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""

import os

import pytest
from horey.kubernetes_api.kubernetes_api import KubernetesAPI
from horey.h_logger import get_logger
from horey.kubernetes_api.kubernetes_api_configuration_policy import KubernetesAPIConfigurationPolicy

#pylint: disable= missing-function-docstring


configuration_values_file_full_path = None
logger = get_logger(
    configuration_values_file_full_path=configuration_values_file_full_path
)

configuration = KubernetesAPIConfigurationPolicy()
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
#configuration.init_from_file()

kube_api = KubernetesAPI(configuration=configuration)


# region done
@pytest.mark.skip(reason="")
def test_init_pods():
    kube_api.init_pods()
    logger.info(f"len(pods) = {len(kube_api.pods)}")
    assert isinstance(kube_api.pods, list)


if __name__ == "__main__":
    test_init_pods()

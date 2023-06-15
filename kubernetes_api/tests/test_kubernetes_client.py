import pytest
import os
from horey.h_logger import get_logger
from horey.kubernetes_api.kubernetes_api_configuration_policy import (
    KubernetesAPIConfigurationPolicy,
)

from horey.kubernetes_api.kubernetes_clients.kubernetes_client import KubernetesClient
from horey.kubernetes_api.kubernetes_api import KubernetesAPI

logger = get_logger()

configuration = KubernetesAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "..",
        "ignore",
        "kubernetes_api_configuration_values.py",
    )
)
configuration.init_from_file()
KubernetesAPI(configuration)


# region done
@pytest.mark.skip(reason="")
def test_get_pods():
    KubernetesClient()


if __name__ == "__main__":
    test_get_pods()

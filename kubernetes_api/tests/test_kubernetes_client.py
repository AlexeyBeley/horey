import pytest
import os
from horey.h_logger import get_logger
from horey.kubernetes_api.kubernetes_api_configuration_policy import (
    KubernetesAPIConfigurationPolicy,
)
from horey.kubernetes_api.base_entities.kubernetes_account import KubernetesAccount

from horey.kubernetes_api.kubernetes_clients.kubernetes_client import KubernetesClient
from horey.kubernetes_api.kubernetes_api import KubernetesAPI
from horey.aws_api.k8s import K8S
import horey.aws_api.base_entities.region

logger = get_logger()

#configuration = KubernetesAPIConfigurationPolicy()
#configuration.configuration_file_full_path = os.path.abspath(
#    os.path.join(
#        os.path.dirname(os.path.abspath(__file__)),
#        "..",
#        "..",
#        "..",
#        "ignore",
#        "kubernetes_api_configuration_values.py",
#    )
#)
#configuration.init_from_file()
#KubernetesAPI(configuration=configuration)

client = KubernetesClient()


@pytest.mark.skip(reason="")
def test_get_pods():
    ret = client.get_pods()
    print(ret)
    assert isinstance(ret, list)


@pytest.mark.skip(reason="")
def test_connect_aws_api():
    k8s = K8S()
    cluster_name = "test-aws-example"
    region = horey.aws_api.base_entities.region.Region.get_region("us-west-2")
    endpoint, cadata, token = k8s.get_cluster_login_credentials(cluster_name, region)
    account = KubernetesAccount(endpoint=endpoint, token=token, cadata=cadata)
    KubernetesAccount.set_kubernetes_account(account)

    client.connect()


if __name__ == "__main__":
    test_connect_aws_api()
    test_get_pods()

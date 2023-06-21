"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""

import os

import pytest
from horey.kubernetes_api.kubernetes_api import KubernetesAPI
from horey.h_logger import get_logger
from horey.kubernetes_api.kubernetes_api_configuration_policy import KubernetesAPIConfigurationPolicy
from horey.aws_api.k8s import K8S
import horey.aws_api.base_entities.region

#pylint: disable= missing-function-docstring


configuration_values_file_full_path = None
logger = get_logger(
    configuration_values_file_full_path=configuration_values_file_full_path
)

configuration = KubernetesAPIConfigurationPolicy()
k8s = K8S()
cluster_name = "test-aws-example"
region = horey.aws_api.base_entities.region.Region.get_region("us-west-2")
configuration.endpoint, configuration.cadata, configuration.token = k8s.get_cluster_login_credentials(cluster_name, region)
kube_api = KubernetesAPI(configuration=configuration)


@pytest.mark.skip(reason="")
def test_init_pods():
    kube_api.init_pods()
    logger.info(f"len(pods) = {len(kube_api.pods)}")
    assert isinstance(kube_api.pods, list)


@pytest.mark.skip(reason="")
def test_init_namespaces():
    kube_api.init_namespaces()
    logger.info(f"len(namespaces) = {len(kube_api.namespaces)}")
    assert isinstance(kube_api.namespaces, list)


@pytest.mark.skip(reason="")
def test_init_pods_and_print_names():
    kube_api.init_pods()
    logger.info(f"len(pods) = {len(kube_api.pods)}")
    names = [obj.name for obj in kube_api.pods]
    print(names)

    assert isinstance(names, list)


@pytest.mark.skip(reason="")
def test_init_namespaces_and_print_names():
    kube_api.init_namespaces()
    logger.info(f"len(namespaces) = {len(kube_api.namespaces)}")
    names = [obj.name for obj in kube_api.namespaces]
    print(names)

    assert isinstance(names, list)


if __name__ == "__main__":
    # test_init_pods()
    # test_init_namespaces()
    test_init_pods_and_print_names()
    test_init_namespaces_and_print_names()


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
from horey.kubernetes_api.service_entities.deployment import Deployment
from horey.kubernetes_api.service_entities.ingress import Ingress
from horey.kubernetes_api.service_entities.service import Service

# pylint: disable= missing-function-docstring


configuration_values_file_full_path = None
logger = get_logger(
    configuration_values_file_full_path=configuration_values_file_full_path
)

configuration = KubernetesAPIConfigurationPolicy()
k8s = K8S()
configuration.cluster_name = "test-aws-example"
namespace = "game-2048"
region = horey.aws_api.base_entities.region.Region.get_region("us-west-2")
configuration.endpoint, configuration.cadata, configuration.token = k8s.get_cluster_login_credentials(configuration.cluster_name,
                                                                                                      region)
configuration.kubernetes_api_cache_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "kubernetes"))
kube_api = KubernetesAPI(configuration=configuration)


@pytest.mark.skip(reason="")
def test_init_pods():
    kube_api.init_pods()
    logger.info(f"len(pods) = {len(kube_api.pods)}")
    assert isinstance(kube_api.pods, list)


@pytest.mark.skip(reason="")
def test_init_services():
    kube_api.init_services()
    logger.info(f"len(services) = {len(kube_api.services)}")
    assert isinstance(kube_api.services, list)


@pytest.mark.skip(reason="")
def test_init_ingresses():
    kube_api.init_ingresses()
    logger.info(f"len(ingresses) = {len(kube_api.ingresses)}")
    assert isinstance(kube_api.ingresses, list)


@pytest.mark.skip(reason="")
def test_init_namespaces():
    kube_api.init_namespaces()
    logger.info(f"len(namespaces) = {len(kube_api.namespaces)}")
    assert isinstance(kube_api.namespaces, list)


@pytest.mark.skip(reason="")
def test_init_deployments():
    kube_api.init_deployments()
    logger.info(f"len(deployments) = {len(kube_api.deployments)}")
    assert isinstance(kube_api.deployments, list)


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


@pytest.mark.skip(reason="")
def test_provision_deployment_raw():
    dict_req = {
        "metadata": {
            "name": "nginx-deployment",
            "labels": {
                "app": "nginx"
            }
        },
        "spec": {
            "replicas": 3,
            "selector": {
                "match_labels": {
                    "app": "nginx"
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": "nginx"
                    }
                },
                "spec": {
                    "containers": [
                        {
                            "name": "nginx",
                            "image": "nginx:latest",
                            "ports": [
                                {
                                    "container_port": 80
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
    kube_api.client.provision_deployment_raw(namespace, dict_req)


@pytest.mark.skip(reason="")
def test_provision_deployment():
    """
    Deployment.

    :return:
    """

    dict_src = {
        "metadata": {
            "name": "nginx-deployment",
            "labels": {
                "app": "nginx"
            }
        },
        "spec": {
            "replicas": 3,
            "selector": {
                "match_labels": {
                    "app": "nginx"
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": "nginx"
                    }
                },
                "spec": {
                    "containers": [
                        {
                            "name": "nginx",
                            "image": "nginx:latest",
                            "ports": [
                                {
                                    "container_port": 80
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
    deployment = Deployment(dict_src=dict_src)
    kube_api.client.provision_deployment(namespace, deployment)


def test_provision_ingress():
    dict_src = {
        "metadata": {
            "name": "nginx-ingress",
            "annotations": {
                "kubernetes.io/ingress.class": "alb",
                "alb.ingress.kubernetes.io/scheme": "internet-facing"
            }
        },
        "spec": {
            "rules": [
                {
                    "http": {
                        "paths": [
                            {
                                "path": "/",
                                "path_type": "Exact",
                                "backend": {
                                    "service":
                                        {"name": "nginx-service",
                                            "port": {
                                            "name": None,
                                            "number": 80
                                        }}
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }
    ingress = Ingress(dict_src=dict_src)
    kube_api.client.provision_ingress(namespace, ingress)


def test_provision_ingress_game_2048():
    dict_src = {"metadata": {
            "annotations": {
                "alb.ingress.kubernetes.io/ip-address-type": "dualstack",
                "alb.ingress.kubernetes.io/scheme": "internet-facing",
                "alb.ingress.kubernetes.io/target-type": "ip",
                "kubectl.kubernetes.io/last-applied-configuration": "{\"apiVersion\":\"networking.k8s.io/v1\",\"kind\":\"Ingress\",\"metadata\":{\"annotations\":{\"alb.ingress.kubernetes.io/ip-address-type\":\"dualstack\",\"alb.ingress.kubernetes.io/scheme\":\"internet-facing\",\"alb.ingress.kubernetes.io/target-type\":\"ip\"},\"name\":\"ingress-2048\",\"namespace\":\"game-2048\"},\"spec\":{\"ingressClassName\":\"alb\",\"rules\":[{\"http\":{\"paths\":[{\"backend\":{\"service\":{\"name\":\"service-2048\",\"port\":{\"number\":80}}},\"path\":\"/\",\"pathType\":\"Prefix\"}]}}]}}\n"
            },
            "labels": {
            "app": "game-2048"
            },
            "creation_timestamp": {
                "horey_cached_type": "datetime",
                "value": "2023-06-09 12:13:43.000000+0000"
            },
            "deletion_grace_period_seconds": None,
            "deletion_timestamp": None,
            "finalizers": [
                "ingress.k8s.aws/resources"
            ],
            "generate_name": None,
            "generation": 1,
            "managed_fields": [
                {
                    "api_version": "networking.k8s.io/v1",
                    "fields_type": "FieldsV1",
                    "fields_v1": {
                        "f:metadata": {
                            "f:finalizers": {
                                ".": {},
                                "v:\"ingress.k8s.aws/resources\"": {}
                            }
                        }
                    },
                    "manager": "controller",
                    "operation": "Update",
                    "subresource": None,
                    "time": {
                        "horey_cached_type": "datetime",
                        "value": "2023-06-09 12:13:43.000000+0000"
                    }
                },
                {
                    "api_version": "networking.k8s.io/v1",
                    "fields_type": "FieldsV1",
                    "fields_v1": {
                        "f:metadata": {
                            "f:annotations": {
                                ".": {},
                                "f:alb.ingress.kubernetes.io/ip-address-type": {},
                                "f:alb.ingress.kubernetes.io/scheme": {},
                                "f:alb.ingress.kubernetes.io/target-type": {},
                                "f:kubectl.kubernetes.io/last-applied-configuration": {}
                            }
                        },
                        "f:spec": {
                            "f:ingressClassName": {},
                            "f:rules": {}
                        }
                    },
                    "manager": "kubectl-client-side-apply",
                    "operation": "Update",
                    "subresource": None,
                    "time": {
                        "horey_cached_type": "datetime",
                        "value": "2023-06-09 12:59:02.000000+0000"
                    }
                }
            ],
            "name": "ingress-2048",
            "namespace": "game-2048",
            "owner_references": None,
            "resource_version": "5633238",
            "self_link": None,
            "uid": "1fcd8969-2896-4062-b8bf-b816fcc320d0"
        },
        "spec": {
            "default_backend": None,
            "ingress_class_name": "alb",
            "rules": [
                {
                    "http": {
                        "paths": [
                            {
                                "backend": {
                                    "resource": None,
                                    "service": {
                                        "name": "service-2048",
                                        "port": {
                                            "name": None,
                                            "number": 80
                                        }
                                    }
                                },
                                "path": "/",
                                "path_type": "Prefix"
                            }
                        ]
                    }
                }
            ],
            "tls": None
        }}
    ingress = Ingress(dict_src=dict_src)
    kube_api.client.provision_ingress(namespace, ingress)


def test_provision_service():
    dict_src = {
        "metadata": {
            "name": "nginx-service"
        },
        "spec": {
            "type": "NodePort",
            "ports": [
                {
                    "port": 80,
                    "target_port": 80,
                    "protocol": "TCP"
                }
            ],
            "selector": {
                "app": "nginx"
            }
        }
    }
    service = Service(dict_src=dict_src)
    kube_api.client.provision_service(namespace, service)


def test_dispose_service():
    dict_src = {
        "metadata": {
            "name": "nginx-service"
        },
        "spec": {
            "type": "NodePort",
            "ports": [
                {
                    "port": 80,
                    "target_port": 80,
                    "protocol": "TCP"
                }
            ],
            "selector": {
                "app": "nginx"
            }
        }
    }
    service = Service(dict_src=dict_src)
    kube_api.client.dispose_service(namespace, service)


@pytest.mark.skip(reason="")
def test_get_ingresses():
    """
    kubectl get ingress/ingress-2048 -n game-2048
    :return:
    """
    breakpoint()


if __name__ == "__main__":
    # test_init_services()
    # test_init_pods()
    # test_init_ingresses()
    # test_init_namespaces()
    # test_init_pods_and_print_names()
    # test_init_namespaces_and_print_names()
    # test_provision_deployment_raw()
    # test_provision_deployment()
    # test_provision_ingress()
    # test_provision_service()
    # test_dispose_service()
    test_provision_ingress_game_2048()

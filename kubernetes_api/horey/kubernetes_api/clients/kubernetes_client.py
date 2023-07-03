"""
Client to work with kube claster

"""
import base64
import tempfile

from horey.kubernetes_api.base_entities.kubernetes_account import KubernetesAccount
from horey.kubernetes_api.service_entities.namespace import Namespace
from horey.kubernetes_api.service_entities.deployment import Deployment
from horey.kubernetes_api.service_entities.pod import Pod
from horey.kubernetes_api.service_entities.service import Service
from horey.kubernetes_api.service_entities.ingress import Ingress
from horey.h_logger import get_logger
import kubernetes

logger = get_logger()

# Configs can be set in Configuration class directly or using helper utility


class KubernetesClient:
    """
    Main class

    """

    def __init__(self):
        self._client = None
        self._apps_v1_api_client = None
        self._networking_v1_api_client = None

    @property
    def client(self):
        """
        Connect to client.

        :return:
        """

        if self._client is None:
            self.connect()
        return self._client

    @property
    def apps_v1_api_client(self):
        """
        Connect to client.

        :return:
        """

        if self._apps_v1_api_client is None:
            self.connect()
        return self._apps_v1_api_client

    @property
    def networking_v1_api_client(self):
        """
        Connect to client.

        :return:
        """

        if self._networking_v1_api_client is None:
            self.connect()
        return self._networking_v1_api_client

    @staticmethod
    def _write_cafile(data: str) -> tempfile.NamedTemporaryFile:
        # protect yourself from automatic deletion
        cafile = tempfile.NamedTemporaryFile(delete=False)
        cadata_b64 = data
        cadata = base64.b64decode(cadata_b64)
        cafile.write(cadata)
        cafile.flush()
        return cafile

    def init_k8s_api_clients(self, endpoint: str, token: str, cafile: str) -> (kubernetes.client.CoreV1Api, kubernetes.client.AppsV1Api):
        kconfig = kubernetes.config.kube_config.Configuration(
            host=endpoint,
            api_key={"authorization": "Bearer " + token}
        )
        kconfig.ssl_ca_cert = cafile
        kclient = kubernetes.client.ApiClient(configuration=kconfig)
        self._client = kubernetes.client.CoreV1Api(api_client=kclient)
        self._apps_v1_api_client = kubernetes.client.AppsV1Api(api_client=kclient)
        self._networking_v1_api_client = kubernetes.client.NetworkingV1Api(api_client=kclient)

    def connect(self):
        """
        Config
        :return:
        """
        account = KubernetesAccount.get_kubernetes_account()
        my_cafile = KubernetesClient._write_cafile(account.cadata)

        my_token = account.token

        self.init_k8s_api_clients(
            endpoint=account.endpoint,
            token=my_token["status"]["token"],
            cafile=my_cafile.name
        )

    def get_pods(self):
        """
        Get pods

        :return:
        """
        ret = [Pod(pod) for pod in self.client.list_pod_for_all_namespaces(watch=False).items]
        return ret

    def get_services(self, namespace=None):
        """
        Get services

        :return:
        """

        if namespace:
            ret = [Service(service) for service in self.client.list_namespaced_service(namespace, watch=False).items]
        else:
            ret = [Service(service) for service in self.client.list_service_for_all_namespaces(watch=False).items]
        return ret

    def get_namespaces(self):
        """
        Get pods

        :return:
        """
        ret = [Namespace(namespace) for namespace in self.client.list_namespace(watch=False).items]
        return ret

    def get_deployments(self, namespace=None):
        """
        Get deployments
        NetworkingV1Api

        :return:
        """
        if namespace:
            ret = [Deployment(obj) for obj in self.apps_v1_api_client.list_namespaced_deployment(namespace, watch=False).items]
        else:
            ret = [Deployment(obj) for obj in self.apps_v1_api_client.list_deployment_for_all_namespaces(watch=False).items]
        return ret

    def get_ingresses(self, namespace=None):
        """
        Get ingresses

        :return:
        """

        if namespace:
            ret = [Ingress(obj) for obj in self.networking_v1_api_client.list_namespaced_ingress(namespace, watch=False).items]
        else:
            ret = [Ingress(obj) for obj in self.networking_v1_api_client.list_ingress_for_all_namespaces(watch=False).items]
        return ret

    def provision_deployment(self, namespace, deployment):
        """
        Create or update.

        :param namespace:
        :param deployment:
        :return:
        """

        for current_deployment in self.get_deployments(namespace=namespace):
            if current_deployment.name == deployment.name:
                return True

        self.provision_deployment_raw(namespace, deployment.convert_to_dict())

    def provision_deployment_raw(self, namespace, dict_req):
        """
        Provision deployment from raw dict request.

        :param namespace:
        :param dict_req:
        :return:
        """
        metadata = kubernetes.client.V1ObjectMeta(name=dict_req["metadata"]["name"])

        spec_selector = kubernetes.client.V1LabelSelector(
            **dict_req["spec"]["selector"]
        )
        containers = [
                    kubernetes.client.V1Container(
                        name=container["name"],
                        image=container["image"],
                        ports=[kubernetes.client.V1ContainerPort(**dict_port) for dict_port in container["ports"]]
                    )
                    for container in dict_req["spec"]["template"]["spec"]["containers"]
                ]
        spec_template = kubernetes.client.V1PodTemplateSpec(
            metadata=kubernetes.client.V1ObjectMeta(
                **dict_req["spec"]["template"]["metadata"]
            ),
            spec=kubernetes.client.V1PodSpec(
                containers=containers
            )
        )
        spec = kubernetes.client.V1DeploymentSpec(
                replicas=dict_req["spec"]["replicas"],
                selector=spec_selector,
                template=spec_template
            )

        deployment = kubernetes.client.V1Deployment(
            metadata=metadata,
            spec=spec
        )

        self.apps_v1_api_client.create_namespaced_deployment(namespace=namespace, body=deployment)

    def provision_ingress(self, namespace, ingress: Ingress):
        """
        Create or update.

        :param namespace:
        :param ingress:
        :return:
        """

        for current_ingress in self.get_ingresses(namespace=namespace):
            if current_ingress.name == ingress.name:
                #return True
                pass

        self.provision_ingress_raw(namespace, ingress.generate_provision_request())

    def provision_ingress_raw(self, namespace, dict_req):
        """
        Provision ingress from raw dict request.

        :param namespace:
        :param dict_req:
        :return:
        """
        logger.info(f"Provisioning Kubernentes ingress: {dict_req['metadata']['name']}")
        body = kubernetes.client.V1Ingress(
            api_version="networking.k8s.io/v1",
            kind="Ingress",
            metadata=kubernetes.client.V1ObjectMeta(**dict_req["metadata"]),
            spec=kubernetes.client.V1IngressSpec(
                rules=[kubernetes.client.V1IngressRule(
                    host=rule.get("host"),
                    http=kubernetes.client.V1HTTPIngressRuleValue(
                        paths=[kubernetes.client.V1HTTPIngressPath(
                            path=path["path"],
                            path_type=path.get("path_type"),
                            backend=kubernetes.client.V1IngressBackend(
                                service=kubernetes.client.V1IngressServiceBackend(
                                    port=kubernetes.client.V1ServiceBackendPort(
                                        number=path["backend"]["service"]["port"]["number"],
                                    ),
                                    name=path["backend"]["service"]["name"])
                            )
                        ) for path in rule["http"]["paths"]]
                    )
                )
                for rule in dict_req["spec"]["rules"]]
            )
        )

        # self.networking_v1_api_client.patch_namespaced_ingress(name=dict_req["metadata"]["name"], namespace=namespace, body=body)
        self.networking_v1_api_client.create_namespaced_ingress(namespace=namespace, body=body)
    
    def provision_service(self, namespace, service):
        """
        Create or update.

        :param namespace:
        :param service:
        :return:
        """

        for current_service in self.get_services(namespace=namespace):
            if current_service.name == service.name:
                return True

        self.provision_service_raw(namespace, service.convert_to_dict())

    def provision_service_raw(self, namespace, dict_req):
        """
        Provision service from raw dict request.

        :param namespace:
        :param dict_req:
        :return:
        """
        breakpoint()
        body = kubernetes.client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=kubernetes.client.V1ObjectMeta(name=dict_req["metadata"]["name"]),
            spec=kubernetes.client.V1ServiceSpec(
                selector=dict_req["spec"]["selector"],
                type=dict_req["spec"]["type"],
                ports=[kubernetes.client.V1ServicePort(
                    **port
                ) for port in dict_req["spec"]["ports"]]
            )
        )

        self.client.create_namespaced_service(namespace=namespace, body=body)

    def dispose_service(self, namespace, service):
        """
        Delete if exists.

        :param namespace:
        :param service:
        :return:
        """
        breakpoint()
        for current_service in self.get_services(namespace=namespace):
            if current_service.name == service.name:
                return True

        self.client.delete_namespaced_service(namespace=namespace, body=body)
"""
Client to work with kube claster

"""
import base64
import tempfile

from horey.kubernetes_api.base_entities.kubernetes_account import KubernetesAccount
from horey.kubernetes_api.service_entities.namespace import Namespace
from horey.kubernetes_api.service_entities.pod import Pod
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

    @property
    def client(self):
        """
        Connect to client.

        :return:
        """

        if self._client is None:
            self.connect()
        return self._client

    @staticmethod
    def _write_cafile(data: str) -> tempfile.NamedTemporaryFile:
        # protect yourself from automatic deletion
        cafile = tempfile.NamedTemporaryFile(delete=False)
        cadata_b64 = data
        cadata = base64.b64decode(cadata_b64)
        cafile.write(cadata)
        cafile.flush()
        return cafile

    @staticmethod
    def k8s_api_client(endpoint: str, token: str, cafile: str) -> kubernetes.client.CoreV1Api:
        kconfig = kubernetes.config.kube_config.Configuration(
            host=endpoint,
            api_key={"authorization": "Bearer " + token}
        )
        kconfig.ssl_ca_cert = cafile
        kclient = kubernetes.client.ApiClient(configuration=kconfig)
        return kubernetes.client.CoreV1Api(api_client=kclient)

    def connect(self):
        """
        Config
        :return:
        """
        account = KubernetesAccount.get_kubernetes_account()
        my_cafile = KubernetesClient._write_cafile(account.cadata)

        my_token = account.token

        self._client = KubernetesClient.k8s_api_client(
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

    def get_namespaces(self):
        """
        Get pods

        :return:
        """
        ret = [Namespace(namespace) for namespace in self.client.list_namespace(watch=False).items]
        return ret

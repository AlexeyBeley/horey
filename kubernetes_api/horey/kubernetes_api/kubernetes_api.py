"""
API to the kubernetes.

"""

from horey.kubernetes_api.clients.kubernetes_client import KubernetesClient
from horey.kubernetes_api.base_entities.kubernetes_account import KubernetesAccount


class KubernetesAPI:
    """
    Main class

    """

    def __init__(self, configuration=None):
        self.client = KubernetesClient()
        self.configuration = configuration
        self.pods = []
        self.namespaces = []
        if configuration is not None:
            KubernetesAccount.set_kubernetes_account(KubernetesAccount(endpoint=configuration.endpoint, token=configuration.token, cadata=configuration.cadata))

    def init_pods(self):
        """
        Init pods.

        :return:
        """
        self.pods = self.client.get_pods()

    def init_namespaces(self):
        """
        Init namespaces.

        :return:
        """
        self.namespaces = self.client.get_namespaces()

    def provision_(self):
        breakpoint()

"""
API to the kubernetes.

"""

from horey.kubernetes_api.kubernetes_clients.kubernetes_client import KubernetesClient
from horey.kubernetes_api.base_entities.kubernetes_account import KubernetesAccount


class KubernetesAPI:
    """
    Main class

    """

    def __init__(self, configuration=None):
        self.client = KubernetesClient()
        self.configuration = configuration
        self.pods = []
        if configuration is not None:
            KubernetesAccount.set_kubernetes_account(KubernetesAccount(configuration.endpoint, configuration.token))

    def init_pods(self):
        """
        Init pods.

        :return:
        """

        self.pods = self.client.get_pods()

"""
API to the kubernetes.

"""

from horey.kubernetes_api.kubernetes_clients.kubernetes_client import KubernetesClient


class KubernetesAPI:
    """
    Main class

    """

    def __init__(self, configuration=None):
        self.client = KubernetesClient()
        self.configuration = configuration
        self.pods = []

    def init_pods(self):
        """
        Init pods.

        :return:
        """

        self.pods = self.client.get_pods()

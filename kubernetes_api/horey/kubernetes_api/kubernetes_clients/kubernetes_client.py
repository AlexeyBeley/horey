"""
Client to work with kube claster

"""

from kubernetes import client, config

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()


class KubernetesClient:
    """
    Main class

    """

    def __init__(self):
        self._client = client.CoreV1Api()

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
    def connect():
        """
        Config
        :return:
        """
        config.load_kube_config()

    def get_pods(self):
        """
        Get pods

        :return:
        """
        return self.client.list_pod_for_all_namespaces(watch=False)

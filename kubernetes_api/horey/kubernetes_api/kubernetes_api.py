"""
API to the kubernetes.

"""
import json
import os

from horey.kubernetes_api.clients.kubernetes_client import KubernetesClient
from horey.kubernetes_api.base_entities.kubernetes_account import KubernetesAccount
from horey.kubernetes_api.kubernetes_api_configuration_policy import KubernetesAPIConfigurationPolicy


class KubernetesAPI:
    """
    Main class

    """

    def __init__(self, configuration: KubernetesAPIConfigurationPolicy=None):
        self.client = KubernetesClient()
        self.configuration = configuration
        self.pods = []
        self.namespaces = []
        self.deployments = []
        if configuration is not None:
            KubernetesAccount.set_kubernetes_account(KubernetesAccount(endpoint=configuration.endpoint, token=configuration.token, cadata=configuration.cadata))

    def cache(self, objects):
        """
        Cache objects to file as json.

        :param objects:
        :return:
        """

        lst_ret = [obj.convert_to_dict() for obj in objects]
        with open(os.path.join(self.configuration.namespace_cache_dir_path, objects[0].cache_file_name), "w") as file_handler:
            json.dump(lst_ret, file_handler, indent=4)

    def init_pods(self):
        """
        Init pods.

        :return:
        """
        self.pods = self.client.get_pods()
        self.cache(self.pods)

    def init_namespaces(self):
        """
        Init namespaces.

        :return:
        """
        self.namespaces = self.client.get_namespaces()
        self.cache(self.pods)

    def init_deployments(self):
        """
        Init deployments.

        :return:
        """
        self.deployments = self.client.get_deployments()
        self.cache(self.pods)

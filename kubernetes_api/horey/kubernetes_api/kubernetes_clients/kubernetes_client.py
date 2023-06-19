"""
Client to work with kube claster

"""

from kubernetes import client, config
from horey.kubernetes_api.base_entities.kubernetes_account import KubernetesAccount
from horey.h_logger import get_logger

logger = get_logger()

# Configs can be set in Configuration class directly or using helper utility


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

        account = KubernetesAccount.get_kubernetes_account()
        if account.token and account.endpoint:
            # Create a Kubernetes configuration object
            _config = {
                'apiVersion': 'v1',
                'clusters': [
                    {
                        'name': 'eks-cluster',
                        'cluster': {
                            'server': account.endpoint,
                            'certificate-authority-data': account.token
                        }
                    }
                ],
                'contexts': [
                    {
                        'name': 'eks-context',
                        'context': {
                            'cluster': 'eks-cluster',
                            'user': 'eks-user'
                        }
                    }
                ],
                'current-context': 'eks-context'
            }
            #breakpoint()
            #client.Configuration.set_default(_config)
            configuration = client.Configuration()
            configuration.host = account.endpoint
            # configuration.ssl_ca_cert = self.ssl_ca_cert
            # configuration.verify_ssl = self._verify_ssl
            configuration.api_key['authorization'] = "bearer " + account.token
            logger.info(f"Setting kubernetes cluster default endpoint to: {account.endpoint}")
            client.Configuration.set_default(configuration)
        else:
            config.load_kube_config()

    def get_pods(self):
        """
        Get pods

        :return:
        """
        return self.client.list_pod_for_all_namespaces(watch=False)

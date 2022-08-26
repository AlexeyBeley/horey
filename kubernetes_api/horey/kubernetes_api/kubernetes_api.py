import json
import pdb
from horey.kubernetes_api.kubernetes_clients.storage_client import KubernetesClient


class KubernetesAPI:
    def __init__(self, configuration=None):
        self.compute_client = KubernetesClient()

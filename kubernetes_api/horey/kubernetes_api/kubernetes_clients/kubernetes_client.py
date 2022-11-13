import pdb
from kubernetes import client, config

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()


print("Listing pods with their IPs:")
v1 = client.CoreV1Api()
ret = v1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

from horey.kubernetes_api.base_entities.kubernetes_account import KubernetesAccount


class KubernetesClient:
    CLIENT_CLASS = None

    def __init__(self):
        self._client = client.CoreV1Api()

    @property
    def client(self):
        if self._client is None:
            self.connect()
        return self._client

    @client.setter
    def client(self, _):
        raise ValueError("Can not explicitly set client")

    def connect(self):
        pdb.set_trace()
        account = KubernetesAccount.get_kubernetes_account()
        for connection_step in account.connection_steps:
            self._client = self.CLIENT_CLASS(
                project=connection_step.project, credentials=connection_step.credentials
            )

    def execute(self, function, args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = dict()
        return function(args, kwargs)
        pdb.set_trace()

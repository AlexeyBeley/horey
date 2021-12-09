import pdb

from horey.gcp_api.base_entities.gcp_account import GCPAccount


class GCPClient:
    CLIENT_CLASS = None

    def __init__(self):
        self._client = None

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
        account = GCPAccount.get_gcp_account()
        for connection_step in account.connection_steps:
            self._client = self.CLIENT_CLASS(project=connection_step.project, credentials=connection_step.credentials)

    def execute(self, function, args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = dict()
        return function(args, kwargs)
        pdb.set_trace()
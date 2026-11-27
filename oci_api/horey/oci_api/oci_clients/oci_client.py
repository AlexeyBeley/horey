import pdb

from horey.oci_api.base_entities.oci_account import OCIAccount


class OCIClient:
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
        account = OCIAccount.get_oci_account()
        for connection_step in account.connection_steps:
            self._client = self.CLIENT_CLASS(
                project=connection_step.project, credentials=connection_step.credentials
            )

    def execute(self, function, args=None, kwargs=None):
        pdb.set_trace()
        if args is None:
            args = []
        if kwargs is None:
            kwargs = dict()
        return function(*args, **kwargs)
        pdb.set_trace()

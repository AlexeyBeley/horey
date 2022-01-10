import pdb

from horey.google_api.base_entities.google_account import GoogleAccount
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


class GoogleClient:
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
        account = GoogleAccount.get_google_account()
        if account is None:
            flow = InstalledAppFlow.from_client_secrets_file(
                "/Users/alexey.beley/private/ignore/accounts/credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        pdb.set_trace()
        for connection_step in account.connection_steps:
            self._client = self.CLIENT_CLASS(project=connection_step.project, credentials=connection_step.credentials)

    def execute(self, function, args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = dict()
        return function(args, kwargs)
        pdb.set_trace()
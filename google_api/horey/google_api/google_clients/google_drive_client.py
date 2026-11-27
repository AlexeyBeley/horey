import pdb

from horey.google_api.google_clients.google_client import GoogleClient

from horey.h_logger import get_logger

logger = get_logger()


class GoogleDriveClient(GoogleClient):
    CLIENT_CLASS = "drive"

    def __init__(self):
        super().__init__()

    def list_files(self):
        request_kwargs = {}
        results = (
            self.client.files()
            .list(pageSize=10, fields="nextPageToken, files(id, name)")
            .execute()
        )
        items = results.get("files", [])
        pdb.set_trace()
        return self.execute(self.client.files().list, kwargs=request_kwargs)
        bucket = self.client.create_bucket(bucket.name)

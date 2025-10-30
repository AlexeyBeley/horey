from pathlib import Path
from horey.selenium_api.selenium_api import SeleniumAPI


class Provider:
    selenium_api = None

    def __init__(self):
        self.name = None
        self.id = None
        self._cache_dir_path = None

    @property
    def cache_dir_path(self):
        return Path(f"/opt/{self.name}")

    @classmethod
    def connect(cls):
        if cls.selenium_api is None:
            cls.selenium_api = SeleniumAPI()
            cls.selenium_api.connect(options="--no-sandbox --disable-gpu --disable-dev-shm-usage")

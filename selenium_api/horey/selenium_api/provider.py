from horey.selenium_api.selenium_api import SeleniumAPI


class Provider:
    _selenium_api = None

    def __init__(self):
        self.name = None
        self.id = None
        self.auction_events = []

    @property
    def selenium_api(self):
        if Provider._selenium_api is None:
            Provider.connect()
        return Provider._selenium_api

    @classmethod
    def connect(cls):
        if cls._selenium_api is None:
            cls._selenium_api = SeleniumAPI()
            cls._selenium_api.connect(options="--no-sandbox --disable-gpu --disable-dev-shm-usage")

    @classmethod
    def disconnect(cls):
        if cls._selenium_api is None:
            return
        cls._selenium_api.disconnect()
        cls._selenium_api = None


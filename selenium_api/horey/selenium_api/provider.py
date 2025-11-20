from horey.selenium_api.selenium_api import SeleniumAPI
from horey.h_logger import get_logger


logger = get_logger()


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

    @staticmethod
    def connect():
        if Provider._selenium_api is None:
            logger.info("Connecting Selenium in Provider")
            Provider._selenium_api = SeleniumAPI()
            Provider._selenium_api.connect(options="--no-sandbox --disable-gpu --disable-dev-shm-usage")

    @staticmethod
    def disconnect():
        logger.info("Disconnecting Provider")
        if Provider._selenium_api is None:
            return
        Provider._selenium_api.disconnect()
        Provider._selenium_api = None


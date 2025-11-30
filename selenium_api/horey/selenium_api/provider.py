from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from typing import List
from horey.selenium_api.selenium_api import SeleniumAPI
from horey.selenium_api.auction_event import AuctionEvent
from horey.selenium_api.lot import Lot
from horey.h_logger import get_logger


logger = get_logger()


class Provider:
    _selenium_api = None
    MONTH_BY_NAME = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "october": 10, "november": 11, " nov ": 11, "december": 12, }

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

    @staticmethod
    def find_month_index(str_src):
        for month_name, month_number in Provider.MONTH_BY_NAME.items():
            if month_name in str_src:
                return month_name, str_src.index(month_name)
        breakpoint()
        raise NotImplementedError(f"Can not determine month from: {str_src}")

    @staticmethod
    def extract_time_meridiem(hour_minute, meridiem):
        if hour_minute.count(":") != 1:
            raise ValueError(hour_minute)
        meridiem = meridiem.replace(".", "").lower()
        if meridiem not in ["pm", "am"]:
            raise ValueError(f"{meridiem=} not one of am/pm")
        hour, minute = hour_minute.split(":")
        hour = int(hour)
        minute = int(minute)

        if meridiem == "pm":
            if hour < 12:
                hour += 12
        elif meridiem != "am":
            raise NotImplementedError(f"meridiem is not one of am/pm in {meridiem}")

        return hour, minute

    def press_cookies_agree(self):
        try:
            btn = self.selenium_api.get_element(By.ID, "didomi-notice-agree-button")
            btn.click()
        except NoSuchElementException:
            pass
        self.selenium_api.wait_for_page_load()

    def init_auction_event_lots(self, auction_event: AuctionEvent):
        """
        Init from Web.

        :param auction_event:
        :return:
        """

        logger.info(f"Starting initializing '{auction_event.id}' auction event lots")
        map_old_lots = {lot.url: lot for lot in auction_event.lots}

        auction_event.lots = self.load_auction_event_lots(auction_event)

        auction_event.init_lots_default_information()
        for i, lot in enumerate(auction_event.lots):
            lot.auction_event_id = auction_event.id
            old_lot = map_old_lots.get(lot.url)
            if old_lot is not None:
                lot.id = old_lot.id
                if lot.current_max < 0:
                    lot.current_max = old_lot.current_max

            if lot.current_max is None:
                breakpoint()

            logger.info(f"Finished {i}/{len(auction_event.lots)} auction event lots, {lot.current_max=}")

        self.validate_lots(auction_event.lots)
        return auction_event.lots

    def validate_lots(self, lots: List[Lot]):
        """
        Check the data format.

        :param lots:
        :return:
        """

        for lot in lots:
            if lot.description is None:
                breakpoint()
                raise NotImplementedError("lot.description = lot.raw_text or self.name")

            if not isinstance(lot.province, str) or lot.province.count(",") != 0:
                breakpoint()
                raise NotImplementedError("lot.province")

            if not isinstance(lot.name, str):
                breakpoint()
                raise NotImplementedError("lot.name")

            if not lot.current_max and not lot.starting_bid:
                breakpoint()
                raise NotImplementedError("lot.current_max lot.starting_bid")

    def load_auction_event_lots(self, _):
        """
        Per provider.

        :param _:
        :return:
        """
        raise NotImplementedError()

    def init_auction_events(self):
        """
        Load and validate.

        :return:
        """

        auction_events = self.load_auction_events()
        for auction_event in auction_events:
            self.validate_auction_event(auction_event)
        return auction_events

    def load_auction_events(self):
        """
        Per provider.

        :return:
        """

        raise NotImplementedError()

    def validate_auction_event(self, auction_event: AuctionEvent):
        """
        Validate data.

        :param auction_event:
        :return:
        """

        if auction_event.description is None:
            breakpoint()
            raise NotImplementedError("auction_event.description")

        if not isinstance(auction_event.provinces, str):
            breakpoint()
            raise NotImplementedError("auction_event.provinces")

        if not isinstance(auction_event.name, str):
            breakpoint()
            raise NotImplementedError("auction_event.province")


import json
import datetime
import re
import time
from pathlib import Path

from horey.selenium_api.selenium_api import SeleniumAPI
from selenium.webdriver.common.by import By
from horey.h_logger import get_logger
from horey.common_utils.common_utils import CommonUtils
from horey.selenium_api.lot import Lot
from horey.selenium_api.provider import Provider
from horey.selenium_api.auction_event import AuctionEvent
from selenium.common.exceptions import NoSuchElementException
logger = get_logger()


class Mcdougallauction(Provider):
    def __init__(self):
        super().__init__()
        self.name = "mcdougallauction"
        self.main_page = "https://www.mcdougallauction.com"

    def load_auction_event_lots(self, auction_event: AuctionEvent):
        """
        Load auction event lots from web.

        :return:
        """

        logger.info(f"Loading {auction_event.id=} page {auction_event.url} elements")
        lots_elements = self.load_page_lot_elements(auction_event.url)

        logger.info(f"Loaded {auction_event.id=} page {auction_event.url} {len(lots_elements)} elements")

        lots = []
        for lot_element in lots_elements:
            lot = Lot()
            lot.starting_bid = 1
            link_element = lot_element.find_element(By.TAG_NAME, "a")
            lot.url = link_element.get_attribute('href')
            lot.description = lot_element.text

            for line in lot_element.text.split("\n"):
                if "Current Bid:" in line:
                    for element in ["$", "USD", "CAD", "Current Bid:", ","]:
                        line = line.replace(element, "").strip()
                    lot.current_max = float(line)
                    lot.starting_bid = lot.current_max
                if "Location:" in line:
                    lot.address = line.replace("Location:", "").strip()
                    provinces = lot.guess_provinces(lot.address)
                    if len(provinces) == 1:
                        lot.province = provinces[0]

                if "Opening Bid:" in line:
                    for element in ["$", "CAD", "Opening Bid:", ","]:
                        line = line.replace(element, "").strip()
                    lot.current_max = float(line)
                    lot.starting_bid = lot.current_max

            item_image_element = lot_element.find_element(By.TAG_NAME, "img")
            lot.image_url = item_image_element.get_attribute("src")

            element_title = lot_element.find_element(By.CLASS_NAME, "item-title")
            lot.name = element_title.text

            lots.append(lot)
            if not lot.current_max:
                breakpoint()
                raise NotImplementedError("current_max")
            if not lot.province:
                if auction_event.provinces.count(",") > 0:
                    breakpoint()
                    raise NotImplementedError("province")
                lot.province = auction_event.provinces

        self.disconnect()
        return lots

    def load_page_lot_elements(self, page_url):
        """
        Raw elements

        :return:
        """

        logger.info(f"Loading page {page_url} items")
        self.selenium_api.get(page_url)
        self.selenium_api.wait_for_page_load()

        results_element = self.selenium_api.get_element(By.CLASS_NAME, "results")
        results_element_text = results_element.text
        if "Results" not in results_element_text:
            breakpoint()
            raise RuntimeError(results_element_text)

        results_count = int(results_element_text.split(" ")[0])
        lots_elements = []

        for i in range(100):
            lots_elements_tmp = self.selenium_api.get_elements_by_class("auction-product-item")
            if len(lots_elements_tmp) == len(lots_elements):
                if len(lots_elements_tmp) == results_count:
                    return lots_elements_tmp
                logger.info(f"Loaded {len(lots_elements_tmp)}/{results_count} auction event lots, going to sleep")
                time.sleep(5)
            lots_elements = lots_elements_tmp
            self.selenium_api.scroll_to_bottom()

        raise TimeoutError("Was not able to scroll to the bottom")

    def load_page_auction_event_elements(self):
        """
        Raw elements

        :return:
        """
        ""

        results_element = self.selenium_api.get_element(By.CLASS_NAME, "results")
        results_element_text = results_element.text
        if "Results" not in results_element_text:
            breakpoint()
            raise RuntimeError(results_element_text)

        results_count = int(results_element_text.split(" ")[0])

        logger.info("Loading page auction event items")
        auctions_elements = []
        for i in range(100):
            auctions_elements_tmp = self.selenium_api.get_elements(By.CLASS_NAME, "online-auction-item")

            if len(auctions_elements_tmp) == len(auctions_elements):
                if len(auctions_elements_tmp) == results_count:
                    return auctions_elements_tmp
                logger.info(f"Loaded {len(auctions_elements_tmp)}/{results_count} auction events, going to sleep")
                time.sleep(5)
            auctions_elements = auctions_elements_tmp
            self.selenium_api.scroll_to_bottom()

        raise TimeoutError("Was not able to scroll to the bottom of auctions elements")

    def load_auction_events(self):
        """
        Load free items.

        :return:
        """

        self.connect()

        logger.info(f"Loading provider {self.name} auctions")

        self.selenium_api.get(self.main_page+"/auction-event-list.php")
        self.selenium_api.wait_for_page_load()

        auctions_elements = self.load_page_auction_event_elements()

        auction_events = []
        for auction_element in auctions_elements:
            auction_event = AuctionEvent()
            url_element = auction_element.find_element(By.TAG_NAME, "a")
            auction_event.url = url_element.get_attribute('href')
            title_element = auction_element.find_element(By.CLASS_NAME, "item-title")
            auction_event.name = title_element.text
            location_element = auction_element.find_element(By.TAG_NAME, "p")
            location_element_text = location_element.text
            if "Location:" not in location_element_text:
                breakpoint()
                raise ValueError(f"Can not find Location: {location_element_text}")
            auction_event.address = location_element_text.replace("Location:", "").strip()

            auction_event.description = location_element_text
            auction_events.append(auction_event)

        logger.info(f"Found {len(auction_events)=}")
        for i, auction_event in enumerate(auction_events):
            self.init_auction_event(auction_event)
            logger.info(f"Finished {i}/{len(auction_events)}")
        self.disconnect()
        return auction_events

    def init_auction_event(self, auction_event: AuctionEvent):
        """
        From web page.

        :param auction_event:
        :return:
        """

        logger.info(f"Initializing Auction event: {auction_event.url}")
        self.selenium_api.get(auction_event.url)
        self.selenium_api.wait_for_page_load()
        auction_event.description = self.selenium_api.get_element(By.CLASS_NAME, "auction-event-info").text

        lines = auction_event.description.split("\n")
        for i, line in enumerate(lines):
            if "Closing Date:" in line:
                break
        else:
            breakpoint()
            raise NotImplementedError("Closing date missing")

        auction_event.end_time = self.extract_date(lines[i + 1], lines[i + 2])
        auction_event.init_provinces()
        if not auction_event.provinces:
            # todo: breakpoint()
            logger.error("Expecting provinces to be determined by now.")
            auction_event.provinces = "none"
        if not auction_event.address:
            logger.error("Expecting address to be determined by now.")
            auction_event.address = "none"

        auction_event.name = auction_event.name + " " + auction_event.end_time.strftime("%Y-%m-%d_%H:%M")

    def extract_date(self, date_line, time_line):
        """
        From date and time lines.

        :param date_line:
        :param time_line:
        :return:
        """
        date_line = date_line.lower()

        for month_name, month_number in Provider.MONTH_BY_NAME.items():
            if month_name in date_line:
                month = month_number
                day_year = date_line[date_line.index(month_name)+len(month_name):].strip()
                day, year = day_year.split(",")
                day = int(day.strip())
                year = int(year.strip())
                break
        else:
            breakpoint()
            raise NotImplementedError(f"Can not determine month from: {date_line}")

        hour_minute, meridiem, gmt_string = time_line.strip().split(" ")
        hour, minute = hour_minute.split(":")
        hour = int(hour)
        minute = int(minute)

        if meridiem == "PM":
            if hour < 12:
                hour += 12
        elif meridiem != "AM":
            raise NotImplementedError(f"meridiem is not one of AM/PM in {time_line}")

        match = re.search(r'GMT([+-]\d+)', gmt_string)
        if not match:
            if gmt_string == "CST":
                tz_delta = datetime.timedelta(hours=-6)
            else:
                raise ValueError(f"Invalid GMT offset format. Must be like 'GMT+2'., received: {gmt_string}")
        else:
            offset_sign = match.group(1)
            offset_hours = int(offset_sign)
            tz_delta = datetime.timedelta(hours=offset_hours)

        naive_dt = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
        dt_aware = naive_dt.replace(tzinfo=datetime.timezone(tz_delta))
        return dt_aware.astimezone(datetime.timezone.utc)

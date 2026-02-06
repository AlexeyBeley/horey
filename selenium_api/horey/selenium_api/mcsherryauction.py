import json
import datetime
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


class Mcsherryauction(Provider):
    def __init__(self):
        super().__init__()
        self.name = "mcsherryauction"
        self.main_page = "https://bid.mcsherryauction.com"

    def load_page_lots(self, page_url, auction_event: AuctionEvent):
        """
        Load free items.

        :return:
        """

        logger.info(f"Loading {auction_event.id=} page {page_url} elements")
        lots_elements = self.load_page_lot_elements(page_url)
        logger.info(f"Loaded {auction_event.id=} page {page_url} {len(lots_elements)} elements")

        lots = []
        for lot_element in lots_elements:
            lot = Lot()
            lot.starting_bid = 1
            lot.description = lot_element.text
            link_element = lot_element.find_element(By.TAG_NAME, "a")

            if "No Bids Yet" in lot_element.text:
                lot.current_max = 0
                if "Start Price" in lot_element.text:
                    for line in lot_element.text.split("\n"):
                        if "Start Price" in line:
                            lot.starting_bid = float(line.split(":")[1].strip())
            else:
                try:
                    highbid_element = lot_element.find_element(By.CLASS_NAME, "gridView_highbid")
                except Exception as inst:
                    print(lot_element.text)
                    break
                if "Current Bid: " not in highbid_element.text:
                    breakpoint()
                    raise ValueError("Current Bid does not present")
                lot.current_max = float(highbid_element.text.split(" ")[-1].replace(",", ""))

            lot.url = link_element.get_attribute('href')
            item_image_element = lot_element.find_element(By.TAG_NAME, "img")
            lot.image_url = item_image_element.get_attribute('src')
            element_title = lot_element.find_element(By.CLASS_NAME, "gridView_title")
            lot.name = element_title.text
            lot.address = auction_event.address
            lot.province = auction_event.provinces
            lots.append(lot)

        return lots

    def load_page_lot_elements(self, page_url):
        """
        Raw elements

        :return:
        """

        logger.info(f"Loading page {page_url} items")
        for retry_counter in range(6):
            self.selenium_api.get(page_url)
            self.selenium_api.wait_for_page_load()
            try:
                item_elements = self.selenium_api.get_elements_by_class("gridItem")
                break
            except NoSuchElementException as error_inst:
                logger.exception("Fetch gridItem failed: %s: %s", page_url, error_inst)

                h1_elements = self.selenium_api.get_elements(By.TAG_NAME, "h1")
                for h1_element in h1_elements:
                    if h1_element.text == "500":
                        time.sleep(10)
                        break
        else:
            breakpoint()
            return []
        return item_elements

    def get_page_count(self, initial_page):
        """
        Get number of pages to fetch

        :return:
        """

        logger.info(f"Getting page count from {initial_page}")

        self.selenium_api.get(initial_page+f"_p{1}?ps=100")
        self.selenium_api.wait_for_page_load()
        pagingbar_pages = self.selenium_api.get_elements_by_class("pagingbar_pages")
        if not pagingbar_pages:
            return 1
        a_elements = pagingbar_pages[-1].find_elements(By.TAG_NAME, "a")
        if not a_elements:
            return 1

        max_page = 0
        for link in a_elements:
            try:
                max_page = max(max_page, int(link.text))
            except ValueError:
                break
        if max_page == 0:
            raise ValueError("Was not able to find max page")
        logger.info(f"Found max page: {max_page}")
        return max_page

    def init_auction_events(self, known_auction_events_by_url):
        """
        Load free items.

        :return:
        """

        self.connect()

        logger.info(f"Loading provider {self.name} auctions")

        self.selenium_api.get(self.main_page)
        self.selenium_api.wait_for_page_load()
        try:
            auction_list_element = self.selenium_api.get_element(By.CLASS_NAME, "auctionslisting")
        except NoSuchElementException as error_inst:
            logger.exception("Fetch auctionslisting failed: %s: %s", self.main_page, error_inst)
            self.disconnect()
            return None

        auctions_elements = auction_list_element.find_elements(By.CLASS_NAME, "row")
        auction_events = []

        time_format_string = "%Y %b %d @ %H:%M"  # '2025 Nov 04 @ 17:00'

        for auctions_element in auctions_elements:
            auction_event = AuctionEvent()
            url_element = auctions_element.find_element(By.TAG_NAME, "a")
            auction_event.url = url_element.get_attribute('href')
            title_element = auctions_element.find_element(By.CLASS_NAME, "row_thumbnail")
            auction_event.name = title_element.get_attribute("title")

            end_time = auctions_element.find_element(By.CLASS_NAME, "datetime")

            time_text_index = end_time.text.find("Auction Local Time")
            if time_text_index < 0:
                raise NotImplementedError("Can not find 'Auction Local Time'")
            if end_time.text.find("Auction Local Time (UTC-06:00") < 0 and end_time.text.find("Auction Local Time (UTC-05:00") < 0:
                raise NotImplementedError("Auction Local Time (UTC-06:00")
            str_end_time = end_time.text[:time_text_index]
            end_time = datetime.datetime.strptime(str_end_time, time_format_string)
            auction_event.end_time = end_time.astimezone(datetime.timezone.utc)

            auction_event.description = auctions_element.text
            auction_events.append(auction_event)
            location_element = auctions_element.find_element(By.CLASS_NAME, "location")
            auction_event.address = location_element.text
        self.disconnect()
        return auction_events

    def load_auction_event_lots(self, auction_event: AuctionEvent):
        """
        Init from Web.

        :param auction_event:
        :return:
        """

        logger.info(f"Starting initializing '{auction_event.id}' auction event lots")
        lots = []

        for page_counter in range(1, self.get_page_count(auction_event.url)+1):
            lots += self.load_page_lots(auction_event.url + f"_p{page_counter}?ps=100",
                                                      auction_event)

            """if lot.current_max == 0:
                if old_lot is not None:
                    lot.current_max = old_lot.current_max
                else:
                    lot.current_max = self.find_lot_starting_bid(lot)
                    logger.info(f"Finished {i}/{len(auction_event.lots)} auction event lots")
            """
        self.disconnect()
        return lots

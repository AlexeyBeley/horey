import datetime
import json

from selenium.webdriver.common.by import By
from horey.h_logger import get_logger
from horey.common_utils.common_utils import CommonUtils
from horey.selenium_api.lot import Lot
from horey.selenium_api.provider import Provider
from horey.selenium_api.auction_event import AuctionEvent
from selenium.common.exceptions import NoSuchElementException

logger = get_logger()


class MAauction(Provider):
    def __init__(self):
        super().__init__()
        self.name = "maauctions"
        self.initial_page = "https://www.maauctions.com/auctions/24839-october-28-2025-sporting-goods-liquidation-timed-auction-manitoba"
        self.main_page = "https://www.maauctions.com/auctions"

    def load_page_lots(self, page_url):
        """
        Load free items.

        :return:
        """

        logger.info(f"Loading page {page_url} items")

        lots = []
        self.selenium_api.get(page_url)
        self.selenium_api.wait_for_page_load()
        try:
            lot_list_element = self.selenium_api.get_element(By.CLASS_NAME, "lotList")
        except NoSuchElementException as error_inst:
            logger.exception("Fetch failed: %s: %s", page_url, error_inst)
            breakpoint()
            return []

        lots_elements = lot_list_element.find_elements(By.CLASS_NAME, "lot")
        for lot_element in lots_elements:
            lot = Lot()
            link_element = lot_element.find_element(By.TAG_NAME, "a")

            try:
                highbid_element = lot_element.find_element(By.CLASS_NAME, "tile-two-winning-bid")
            except Exception as error_inst:
                logger.exception("Fetch failed: %s: %s", lot_element.text, error_inst)
                break
            highbid = highbid_element.text
            if not highbid.startswith("$"):
                raise ValueError("Current Bid does not present")
            lot.high_bid = float(highbid.replace(",", "")[1:])

            lot.url = link_element.get_attribute('href')
            item_image_element = lot_element.find_element(By.TAG_NAME, "img")
            lot.image_url = item_image_element.get_attribute('src')
            element_title = lot_element.find_element(By.CLASS_NAME, "lot-title")
            lot.name = lot_element.text
            lots.append(lot)

        return lots

    def get_page_count(self, initial_page):
        """
        Get number of pages to fetch

        :return:
        """

        self.selenium_api.get(initial_page)
        self.selenium_api.wait_for_page_load()
        try:
            pagingbar_element = self.selenium_api.get_element(By.CLASS_NAME, "pagination")
        except NoSuchElementException as ins_err:
            breakpoint()
            return 1
        total_element = pagingbar_element.find_element(By.CLASS_NAME, "total")
        max_page = int(total_element.text)
        logger.info(f"Found page count: {max_page}")
        return max_page

    def init_all_items(self, update_info=True):
        """
        Load all items.

        :return:
        """

        initial_page = self.initial_page

        if not initial_page.startswith("https://www.maauctions.com/auctions/"):
            raise NotImplementedError("https://www.maauctions.com/auctions/")

        file_name = initial_page[len("https://www.maauctions.com/auctions/"):] + ".json"
        file_path = self.cache_dir_path / file_name

        if not update_info and file_path.exists():
            ret = CommonUtils.init_from_api_cache(Lot, file_path)
            return ret

        items = []
        for page_counter in range(1,self.get_page_count()+1):
            items += self.load_page_items(page_counter)
            #self.selenium_api.get(item.url)
            #element_item_description = self.selenium_api.get_element(By.ID, "cphBody_cbItemDescription")
            #item.description = element_item_description.text

        ret = [CommonUtils.convert_to_dict(item.__dict__) for item in items]
        with open(file_path, "w", encoding="utf-8") as file_handler:
            json.dump(ret, file_handler)

        return items

    def init_auction_events(self):
        """
        Load free items.

        :return:
        """

        self.connect()

        logger.info(f"Loading provider {self.name} auctions")

        self.selenium_api.get(self.main_page)
        self.selenium_api.wait_for_page_load()
        auction_list_element = self.selenium_api.get_element(By.CLASS_NAME, "auctionList")
        auctions_elements = auction_list_element.find_elements(By.CLASS_NAME, "auction")
        auction_events = []

        time_format_string = '%m/%d/%Y %I:%M:%S %p'  # '11/1/2025 10:00:00 AM'

        for auctions_element in auctions_elements:
            auction_event = AuctionEvent()
            link_element = auctions_element.find_element(By.TAG_NAME, "a")
            auction_event.link = link_element.get_attribute('href')
            title_element = auctions_element.find_element(By.CLASS_NAME, "auctionTitle")
            auction_event.name = title_element.text
            details = auctions_element.find_element(By.CLASS_NAME, "details")

            start_time = details.find_element(By.CLASS_NAME, "start_time")
            text_time = start_time.text.replace("Start Time", "")
            auction_event.start_time = datetime.datetime.strptime(text_time, time_format_string)

            try:
                end_time = details.find_element(By.CLASS_NAME, "end_time")
                text_time = end_time.text.replace("End Time", "")
                auction_event.end_time = datetime.datetime.strptime(text_time, time_format_string)
            except NoSuchElementException:
                pass

            description_element = auctions_element.find_element(By.CLASS_NAME, "auction-preview-text")
            auction_event.description = description_element.text
            auction_events.append(auction_event)

        for auction_event in auction_events:
            auction_event.link = self.init_real_auction_event_link(auction_event.link)

        return auction_events

    def init_real_auction_event_link(self, base_link):
        """
        Some auctions located on other links- sublinks.

        :param base_link:
        :return:
        """

        self.selenium_api.get(base_link)
        self.selenium_api.wait_for_page_load()
        try:
            self.selenium_api.get_element(By.CLASS_NAME, "pagination")
            return base_link
        except NoSuchElementException:
            button = self.selenium_api.get_element(By.CLASS_NAME, "viewAllLotsBtn")
            button.click()
            return self.selenium_api.driver.current_url

    def init_auction_event_lots(self, auction_event: AuctionEvent):
        for page_counter in range(1, self.get_page_count(auction_event.link+"?page=1&pageSize=125")+1):
            auction_event.lots += self.load_page_lots(auction_event.link + f"?page={page_counter}&pageSize=125")

        return auction_event.lots

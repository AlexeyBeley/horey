import datetime
import time

from selenium.webdriver.common.by import By
from horey.h_logger import get_logger
from horey.selenium_api.lot import Lot
from horey.selenium_api.provider import Provider
from horey.selenium_api.auction_event import AuctionEvent
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement
logger = get_logger()


class Pennerauction(Provider):
    def __init__(self):
        super().__init__()
        self.name = "pennerauction"
        self.main_page = "https://pennerauctions.ca"

    def load_page_lots(self, page_url, auction_event: AuctionEvent):
        """
        Load free items.

        :return:
        """

        lots = None

        for _ in range(5):
            lots = []
            try:
                logger.info(f"Loading {auction_event.id=} page {page_url} elements")

                lots_elements = self.load_page_lot_elements(page_url)
                logger.info(f"Loaded {auction_event.id=} page {page_url} {len(lots_elements)} elements")

                for lot_element in lots_elements:
                    lot = self.init_lot_from_lot_element(lot_element)
                    lot.address = auction_event.address
                    lot.province = auction_event.provinces
                    lots.append(lot)

                break
            except StaleElementReferenceException:
                logger.info(f"Loading lot elements failed: {auction_event.id=} page {page_url}. Sleeping and retrying")
                time.sleep(10)
        if not lots:
            breakpoint()
        return lots

    @staticmethod
    def init_lot_from_lot_element(lot_element: WebElement):
        lot = Lot()
        lot.description = lot_element.text
        for _ in range(50):
            try:
                element_title = lot_element.find_element(By.CLASS_NAME, "lot-title")
                lot.name = element_title.text
                break
            except NoSuchElementException:
                time.sleep(0.1)
        else:
            breakpoint()
            raise RuntimeError("Did not load correctly")

        link_element = lot_element.find_element(By.TAG_NAME, "a")
        lot.url = link_element.get_attribute("href")
        item_image_element = lot_element.find_element(By.TAG_NAME, "img")
        lot.image_url = item_image_element.get_attribute("src")

        lot.starting_bid = 1
        if "High Bid" not in lot_element.text:
            if "Bidding opens in" in lot_element.text:
                lot.current_max = 0
                lot.starting_bid = 0
                return lot
            raise ValueError(lot_element.text)

        for line in lot_element.text.split("\n"):
            if "High Bid" in line:
                break
        else:
            raise ValueError(f"Could not find relevant line: {lot_element.text}")

        try:
            line = line.split(":")[-1].replace(",", "").replace("CAD", "").lower()
            # ' 0.00  x 3'
            lot.current_max = float(line)
        except ValueError:
            if " x " not in line:
                breakpoint()
                logger.info("Manual set current max")
            left, right = line.split("x")
            lot.current_max = float(left.strip()) * float(right.strip())

        if lot.current_max == 0:
            min_bid_element = lot_element.find_element(By.CLASS_NAME, "TileDisplayMinBid")
            # '1.00 CAD'
            min_bid = float(min_bid_element.text.replace(",", "").replace("CAD", "").strip())
            quantity = 1
            try:
                quantity_element = lot_element.find_element(By.CLASS_NAME, "TileDisplayBidQuantity")
                # 'x 3'
                quantity = int(quantity_element.text.lower().split("x")[1].strip())
            except NoSuchElementException:
                pass

            lot.starting_bid = min_bid * quantity

        return lot

    def load_page_lot_elements(self, page_url):
        """
        Raw elements

        :return:
        """

        logger.info(f"Loading page {page_url} items")
        self.selenium_api.get(page_url)
        item_elements = None
        for retry_counter in range(6):
            self.selenium_api.wait_for_page_load()
            item_elements = self.selenium_api.get_elements_by_class("lot-tile")
            if not item_elements:
                logger.info("Was not able to find `lot-tile`. Going to sleep")
                time.sleep(10)
                continue
            break

        if not item_elements:
            breakpoint()
        return item_elements

    def get_page_count(self, initial_page):
        """
        Get number of pages to fetch

        :return:
        """

        logger.info(f"Getting page count from {initial_page}")

        self.selenium_api.get(initial_page+"?ipp=100&apage=1")
        self.selenium_api.wait_for_page_load()

        self.press_cookies_agree()

        for _ in range(50):
            try:
                pagingbar = self.selenium_api.get_element(By.CLASS_NAME, "pagination")
                break
            except NoSuchElementException:
                time.sleep(0.1)
        else:
            logger.exception(f"Was not able to find 'pagination'")
            return 1

        a_elements = pagingbar.find_elements(By.TAG_NAME, "li")
        if not a_elements:
            return 1

        max_page = 0
        for link in a_elements:
            try:
                max_page = max(max_page, int(link.text))
            except ValueError as inst_error:
                if "…" not in repr(inst_error):
                    break

        if max_page == 0:
            raise ValueError("Was not able to find max page")
        logger.info(f"Found max page: {max_page}")
        return max_page

    def init_auction_events(self):
        """
        Load free items.

        :return:
        """

        self.connect()

        logger.info(f"Loading provider {self.name} auctions")

        self.selenium_api.get(self.main_page)
        self.selenium_api.wait_for_page_load()
        try:
            auction_list_element = self.selenium_api.get_element(By.CLASS_NAME, "penner-auctions")
        except NoSuchElementException as error_inst:
            logger.exception("Fetch penner-auctions failed: %s: %s", self.main_page, error_inst)
            self.disconnect()
            return None

        auctions_elements = auction_list_element.find_elements(By.CLASS_NAME, "auction-card")
        auction_events = []

        for auctions_element in auctions_elements:
            auction_event = AuctionEvent()
            btn = auctions_element.find_element(By.CLASS_NAME, "auction-button")
            auction_event.url = btn.get_attribute("href")
            auction_events.append(auction_event)
            continue

        for auction_event in auction_events:
            self.init_auction_event(auction_event)

        self.disconnect()
        return auction_events

    def init_auction_event(self, auction_event: AuctionEvent):
        self.connect()

        logger.info(f"Loading provider {self.name} auction event {auction_event.url}")

        self.selenium_api.get(auction_event.url)
        self.selenium_api.wait_for_page_load()

        self.press_cookies_agree()

        time_format_string = "%m/%d/%Y"  # "11/5/2025"

        try:
            title_element = self.selenium_api.get_element(By.CLASS_NAME, "auction-title")
        except Exception as inst_error:
            logger.info(f"Was not able to locate auction-title, {inst_error}")
            try:
                title_element = self.selenium_api.get_element(By.CLASS_NAME, "auction-event-name")
            except Exception:
                breakpoint()
                raise NotImplementedError()

        auction_event.name = title_element.text
        if not auction_event.name:
            breakpoint()
        for _ in range(10):
            try:
                col_element = self.selenium_api.get_element(By.CLASS_NAME, "col")
                break
            except Exception:
                time.sleep(1)
        else:
            raise TimeoutError("col")

        # todo: fix
        if "Automatically Remove Closed Lots" in col_element.text:
            auction_event.start_time = datetime.datetime.now(tz=datetime.timezone.utc)
            auction_event.end_time = datetime.datetime.now(tz=datetime.timezone.utc)
            auction_event.address = "manitoba"
            auction_event.provinces = "manitoba"
            auction_event.description = "manual not null"
            breakpoint()
            return auction_event

        for line in col_element.text.split("\n"):
            if "Date" in line:
                break
        else:
            breakpoint()
            raise ValueError(f"Can not find date in {col_element.text}")
        line = line.replace("Date(s)", "").strip()
        str_start_date, str_end_date = line.split("-")
        str_start_date = str_start_date.strip()
        start_time = datetime.datetime.strptime(str_start_date, time_format_string)
        auction_event.start_time = start_time.astimezone(datetime.timezone.utc)

        str_end_date = str_end_date.strip()
        end_time = datetime.datetime.strptime(str_end_date, time_format_string)
        auction_event.end_time = end_time.astimezone(datetime.timezone.utc)

        auction_event.address = self.selenium_api.get_element(By.CLASS_NAME, "company-address").text
        auction_event.description = self.selenium_api.get_element(By.CLASS_NAME, "auction-description-container").text

        auction_event.init_provinces()
        if not auction_event.provinces:
            breakpoint()

        if not auction_event.name:
            breakpoint()

        if not auction_event.url:
            breakpoint()

        if not auction_event.provinces:
            raise NotImplementedError()

        if not auction_event.name:
            raise NotImplementedError()

        if not auction_event.url:
            raise NotImplementedError()
        return True

    def load_auction_event_lots(self, auction_event: AuctionEvent):
        """
        Init from Web.

        :param auction_event:
        :return:
        """

        self.connect()

        logger.info(f"Starting initializing '{auction_event.id}' auction event lots")
        lots = []
        for page_counter in range(1, self.get_page_count(auction_event.url)+1):
            lots += self.load_page_lots(auction_event.url + f"?ipp=100&apage={page_counter}",
                                                      auction_event)
            if not lots:
                breakpoint()

        self.disconnect()
        return lots

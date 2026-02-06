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


class Kayesauction(Provider):
    def __init__(self):
        super().__init__()
        self.name = "kayesauctions"
        self.main_page = "https://kayesauctions.ca"

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
                    if not auction_event.address:
                        breakpoint()
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
        """
        Init from web element.

        :param lot_element:
        :return:
        """

        lot = Lot()
        lot.description = lot_element.get_attribute("innerHTML")

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
            lot.current_max = float(line.strip())
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
            if "Next" in link.text:
                break
            max_page = max(max_page, int(link.text))

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

        self.selenium_api.get(self.main_page + "/current-auctions")
        self.selenium_api.wait_for_page_load()

        auctions_elements_lists = self.selenium_api.get_elements(By.CSS_SELECTOR, "div.hRdzm4[role='list']")
        auctions_elements_list = auctions_elements_lists[1]
        auctions_elements = auctions_elements_list.find_elements(By.CSS_SELECTOR, "div.T7n0L6[role='listitem']")
        if not auctions_elements:
            breakpoint()
            raise NotImplementedError("Can not find listings")

        auction_events = []
        for auctions_element in auctions_elements:
            auction_event = AuctionEvent()
            try:
                btn = auctions_element.find_element(By.CSS_SELECTOR, "[data-testid='linkElement']")
            except NoSuchElementException:
                continue

            auction_event.url = btn.get_attribute("href")
            auctions_element_text = auctions_element.text
            for line in auctions_element_text.split("\n"):

                if "Bidding Starts" in line:
                    auction_event.start_time = self.extract_time_from_line(line)

                if "Bidding open from" in line:
                    auction_event.start_time = datetime.datetime.now()

                if "Location:" in line:
                    auction_event.address = line.replace("Location:", "")

                if "closes" in line.lower():
                    auction_event.end_time = self.extract_time_from_line(line)

                if "closing" in line.lower():
                    auction_event.end_time = self.extract_time_from_line(line)

            if not auction_event.end_time:
                breakpoint()
                raise ValueError("Needed for checking if the event finished")
            auction_events.append(auction_event)

        for auction_event in auction_events:
            logger.info(f"Loading {auction_event.url}")
            self.selenium_api.get(auction_event.url)
            self.selenium_api.wait_for_page_load()
            self.press_cookies_agree()
            for _ in range(500):
                auction_event.name = self.selenium_api.get_element(By.CLASS_NAME, "auction-title").text
                if auction_event.name:
                    break
                time.sleep(0.1)
            else:
                raise ValueError("Name")

            for _ in range(50):
                try:
                    logger.info(f"Looking for {auction_event.url} 'Auction Details' btn")
                    btn_details = self.selenium_api.get_element(By.CSS_SELECTOR, "[title='Auction Details']")
                    btn_details.click()
                    self.selenium_api.wait_for_page_load()
                except Exception as inst_error:
                    logger.error(f"Auction description Auction Details btn not found: {repr(inst_error)}")

                try:
                    auction_event.description = self.selenium_api.get_element(By.ID, "panel-auction-detail-auction-information").text
                    break
                except Exception as inst_error:
                    logger.error(f"Auction description auction-information not found: {repr(inst_error)} retrying")
                    time.sleep(0.1)
            else:
                raise TimeoutError("Was not able to fetch auction description")

            if not auction_event.address:
                auction_event.address = self.selenium_api.get_element(By.TAG_NAME, "app-city-state-zip-link").text
                auction_event.address = auction_event.address.replace("\n", " ")

        if not auction_events:
            breakpoint()
            raise RuntimeError("No auction events found")

        self.disconnect()
        return auction_events

    def extract_time_from_line(self, line):
        line = line.lower()
        month_name, month_index = self.find_month_index(line)
        month = self.MONTH_BY_NAME[month_name]

        line_date = line[month_index + len(month_name):]
        day, line_date = line_date.split(",")
        day = int(day.strip())
        year, line_date = line_date.strip().split("at")
        year = int(year.strip())
        parts = line_date.strip().split(" ", 2)
        hour_minute, meridiem = parts[0], parts[1]
        hour, minute = self.extract_time_meridiem(hour_minute, meridiem)
        return datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)

    def init_auction_event_lots(self, auction_event: AuctionEvent):
        """
        Init from Web.

        :param auction_event:
        :return:
        """

        self.connect()

        logger.info(f"Starting initializing '{auction_event.id}' auction event lots")
        map_old_lots = {lot.url: lot for lot in auction_event.lots}
        auction_event.lots = []

        for page_counter in range(1, self.get_page_count(auction_event.url)+1):
            auction_event.lots += self.load_page_lots(auction_event.url + f"?ipp=100&apage={page_counter}",
                                                      auction_event)
            if not auction_event.lots:
                breakpoint()

        auction_event.init_lots_default_information()
        for i, lot in enumerate(auction_event.lots):
            lot.auction_event_id = auction_event.id
            old_lot = map_old_lots.get(lot.url)
            if old_lot is not None:
                lot.id = old_lot.id

            if lot.current_max is None:
                breakpoint()

        self.disconnect()
        return auction_event.lots

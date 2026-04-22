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


class Neighbourhoodauctions(Provider):
    def __init__(self):
        super().__init__()
        self.name = "neighbourhoodauctions"
        self.main_page = "https://www.icollector.com/Neighbourhood-Auctions-LTD_ae2775"

    def init_auction_events(self, known_auction_events_by_url):
        """
        Load free items.

        :return:
        """

        self.connect()

        logger.info(f"Loading provider {self.name} auctions")

        self.selenium_api.get(self.main_page)
        self.selenium_api.wait_for_page_load()
        all_divs = self.selenium_api.get_elements(By.CLASS_NAME, "row")
        auction_events = []
        for auctions_element in all_divs:
            auction_event = AuctionEvent()
            try:
                row_thumbnail = auctions_element.find_element(By.CLASS_NAME, "row_thumbnail")
            except NoSuchElementException:
                continue
            auction_event.name =  auctions_element.find_element(By.CLASS_NAME, "title").text
            auction_event.description = auction_event.name

            auction_event.url = row_thumbnail.get_attribute("href")
            auctions_element_text = auctions_element.text
            for line in auctions_element_text.split("\n"):

                if "Auction Local Time" in line:
                    line = line[:line.index("Auction Local Time")]
                    line = line.replace(" @ ", " at ")
                    while "  " in line: line = line.replace("  ", " ")
                    auction_event.start_time = self.extract_time_from_line(line)
                    auction_event.end_time = auction_event.start_time

                if "Winnipeg" in line:
                    auction_event.address = line

            if not auction_event.end_time:
                breakpoint()

            if not auction_event.address:
                breakpoint()

            auction_events.append(auction_event)


        if not auction_events:
            breakpoint()
            raise RuntimeError("No auction events found")

        self.disconnect()
        return auction_events

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
            lot.url = link_element.get_attribute('href')
            if "winnipeg" in auction_event.address.lower():
                lot.interested = True
            else:
                raise NotImplementedError(auction_event.address)

            if "No Bids Yet" in lot_element.text:
                lot.current_max = 0
                if "Start Price" in lot_element.text:
                    for line in lot_element.text.split("\n"):
                        if "Start Price" in line:
                            lot.starting_bid = float(line.split(":")[1].strip())
            elif ("No Online Bidding For This Lot" in lot_element.text or
                  "Please Read Before Bidding" in lot_element.text or
                  "More Items Coming" in lot_element.text):
                continue
            else:
                try:
                    highbid_element = lot_element.find_element(By.CLASS_NAME, "gridView_highbid")
                    if "Current Bid: " not in highbid_element.text:
                        breakpoint()
                        raise ValueError("Current Bid does not present")
                    lot.current_max = float(highbid_element.text.split(" ")[-1].replace(",", ""))
                except NoSuchElementException as inst:
                    if "Bidding Has Concluded" in lot_element.text:
                        for line in lot_element.text.split("\n"):
                            if "Sold to" in line:
                                lot.current_max = float(line.split("=")[1].replace(",", "").strip())
                                break
                        else:
                            breakpoint()
                            lot.current_max = 0
                    else:
                        logger.exception(inst)
                        logger.info(f"{lot_element.text=}, {lot.url=}")
                        breakpoint()

            item_image_element = lot_element.find_element(By.TAG_NAME, "img")
            lot.image_url = item_image_element.get_attribute('src')
            element_title = lot_element.find_element(By.CLASS_NAME, "gridView_title")
            lot.name = element_title.text
            lot.address = auction_event.address
            lot.province = auction_event.provinces
            lots.append(lot)

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

    def extract_time_from_line(self, line):
        """
        Extact
        :param line:
        :return:
        """

        line = line.lower()
        # '2026 apr 26 at 19:00'
        year, month_name, day, at, hour_minute = line.split(" ")
        year = int(year)
        day = int(day)
        if at != "at":
            raise ValueError(f"Incorrect line: {line}")
        hour, minute = hour_minute.split(":")
        hour = int(hour)
        minute = int(minute)

        month = self.MONTH_BY_NAME[month_name]

        return datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)

    def yield_auction_event_lots(self, auction_event: AuctionEvent):
        """
        Init from Web.

        :param auction_event:
        :return:
        """

        logger.info(f"Starting initializing '{auction_event.id}' auction event lots")
        lots = []
        for page_counter in range(1, self.get_page_count(auction_event.url)+1):
            for lot in  self.load_page_lots(auction_event.url + f"_p{page_counter}?ps=100",
                                                      auction_event):
                yield lot
        self.disconnect()
        return lots


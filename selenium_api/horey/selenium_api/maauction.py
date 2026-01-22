"""
Lot 75W Non-Operable 2020 Ram 1500 Classic 4x4 Express 4dr Crew Cab 5.5 ft. SB Hemi
Lot 75W Non-Operable 2020 Ram 1500 Classic 4x4 Express 4dr Crew Cab 5.5 ft. SB Pickup
"""
import datetime
import json
import time
from zoneinfo import ZoneInfo
from urllib.parse import urlencode, urlparse, urlunparse

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

    def load_page_lots(self, page_url, auction_event_address=None):
        """
        Load free items.

        :return:
        """

        lots_elements = self.load_page_lot_elements(page_url)

        lots = []

        for i, lot_element in enumerate(lots_elements):
            lot = Lot()
            lot.raw_text = lot_element.text
            lot.description = lot.raw_text
            url_element = lot_element.find_element(By.TAG_NAME, "a")
            try:
                highbid_element = lot_element.find_element(By.CLASS_NAME, "tile-two-winning-bid")
            except Exception as error_inst:
                logger.exception("Fetch tile-two-winning-bid failed: %s: %s", lot_element.text, error_inst)
                break
            highbid = highbid_element.text
            if not highbid.startswith("$"):
                raise ValueError("Current Bid does not present")
            lot.current_max = float(highbid.replace(",", "")[1:])

            lot.url = url_element.get_attribute('href')
            item_image_element = lot_element.find_element(By.TAG_NAME, "img")
            lot.image_url = item_image_element.get_attribute('src')

            element_title = lot_element.find_element(By.CLASS_NAME, "lot-title")
            lot.name = element_title.text
            if "Location:" in lot_element.text:
                lines = lot_element.text.split("\n")
                for line in lines:
                    if "Location:" in line:
                        lot.address = line.replace("Location:", "")
                        break
                else:
                    breakpoint()
                    raise NotImplementedError("Can not find location")
            elif auction_event_address:
                lot.address = auction_event_address
            else:
                logger.warning(f"Was not able to find lot address: {page_url}")
                lot.address = "none"
                lot.province = "none"

            lots.append(lot)
            logger.info(f"Finished lot elements: {i}/{len(lots_elements)}")

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
                lot_list_element = self.selenium_api.get_element(By.CLASS_NAME, "lotList")
                break
            except NoSuchElementException as error_inst:
                logger.exception(f"Fetch lotList failed: {page_url}: {error_inst}")
                try:
                    lot_list_contianer_element = None
                    for _ in range(100):
                        try:
                            lot_list_contianer_element = self.selenium_api.get_element(By.CLASS_NAME, "lotListContainer")
                        except Exception:
                            # F idiots!
                            lot_list_contianer_element = self.selenium_api.get_element(By.CLASS_NAME,
                                                                                       "lotListContainer ")
                        if "Loading..." not in lot_list_contianer_element.text:
                           break
                        time.sleep(0.1)
                    if "No Lots Found" in lot_list_contianer_element.text:
                        return []
                except Exception as inst_err:
                    logger.exception(f"Fetch lotListContainer failed: {page_url}: {inst_err}")
                    breakpoint()
                    pass

                h1_elements = self.selenium_api.get_elements(By.TAG_NAME, "h1")
                for h1_element in h1_elements:
                    if h1_element.text == "500":
                        time.sleep(10)
                        break
        else:
            breakpoint()
            return []

        return lot_list_element.find_elements(By.CLASS_NAME, "lot")

    def get_page_count(self, initial_page):
        """
        Get number of pages to fetch

        :return:
        """

        for retry_counter in range(6):
            self.selenium_api.get(initial_page)
            self.selenium_api.wait_for_page_load()
            try:
                pagingbar_element = self.selenium_api.get_element(By.CLASS_NAME, "pagination")
                break
            except NoSuchElementException as error_inst:
                logger.warning(f"Fetch pagination failed: {initial_page}: {repr(error_inst)}")

                h1_elements = self.selenium_api.get_elements(By.TAG_NAME, "h1")
                for h1_element in h1_elements:
                    if h1_element.text == "500":
                        time.sleep(10)
                        break
        else:
            raise TimeoutError(f"Was not able to fetch: {initial_page}")

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

        urls = []
        for auctions_element in auctions_elements:
            url_element = auctions_element.find_element(By.TAG_NAME, "a")
            url = url_element.get_attribute("href")
            urls.append(url)

        auction_events = []
        for url in urls:
            auction_events += self.init_auction_events_from_internal_url(url)

        self.disconnect()
        return auction_events

    def init_auction_events_from_internal_url(self, url):
        """
        This provider has multiple events under same base event.

        :param url:
        :return:
        """

        self.selenium_api.get(url)
        self.selenium_api.wait_for_page_load()
        try:
            self.selenium_api.get_element(By.CLASS_NAME, "pagination")
        except NoSuchElementException:
            auction_ring_elements = self.selenium_api.get_elements(By.CLASS_NAME, "auction-ring")
            urls = []
            for auction_ring_element in auction_ring_elements:
                btn_element = auction_ring_element.find_element(By.CLASS_NAME, "viewRingCatalogBtn")
                urls.append(btn_element.get_attribute("href"))

            auction_events = []
            for url in urls:
                auction_events += self.init_auction_events_from_internal_url(url)
            return auction_events

        auction_event = AuctionEvent()
        auction_event.url = url
        title_element = self.selenium_api.get_element(By.CLASS_NAME, "infoBoxAuctionTitle")

        self.init_auction_event_name(auction_event, title_element)

        auction_description = self.selenium_api.get_element(By.CLASS_NAME, "auctionDescription")
        auction_event.description = auction_description.text
        auction_location = self.selenium_api.get_element(By.CLASS_NAME, "auctionLocation")
        auction_event.address = auction_location.text
        auction_event.init_provinces()
        if not auction_event.provinces:
            breakpoint()

        self.init_auction_event_times(auction_event)
        return [auction_event]

    def init_auction_event_times(self, auction_event):
        """
        Start end end time

        :param auction_event:
        :return:
        """

        self.init_auction_event_start_time(auction_event)
        self.init_auction_event_end_time(auction_event)

        if auction_event.start_time and auction_event.end_time:
            return True

        auction_event_address = auction_event.provinces \
            if auction_event.provinces and "," not in auction_event.provinces \
            else None
        lots = self.load_page_lots(self.add_query_params(auction_event.url, {"page": 1, "pageSize": 125}),
                                   auction_event_address=auction_event_address)
        if not lots:
            return False

        if auction_event.start_time is None:
            self.init_auction_event_start_time_from_lot(auction_event, lots[0])

        if auction_event.end_time is None:
            self.init_auction_event_end_time_from_lot(auction_event, lots[0])
        return True

    def init_auction_event_start_time_from_lot(self, auction_event: AuctionEvent, lot: Lot):
        """
        From lot.

        :param auction_event:
        :param lot:
        :return:
        """

        self.selenium_api.get(lot.url)
        self.selenium_api.wait_for_page_load()
        try:
            start_time_element = self.selenium_api.get_element(By.CLASS_NAME, "startTime")
        except NoSuchElementException:
            breakpoint()
            return None
        # '12/3/2025 10:00:00 PM'
        parse_format = '%m/%d/%Y %I:%M:%S %p'
        start_time_string = start_time_element.text.replace("Start Time:", "")
        naive_dt = datetime.datetime.strptime(start_time_string, parse_format)
        tz = MAauction.get_auction_event_tz(auction_event)

        if tz is None:
            provinces = lot.guess_provinces(lot.raw_text)
            if len(provinces) == 0:
                breakpoint()
                raise RuntimeError(f"Expected 1 province: {provinces}")
            if len(provinces) > 1:
                logger.error(f"More than 1 province: {provinces}")
            tz = self.get_province_tz(provinces[0])
            if tz is None:
                breakpoint()
        auction_event.start_time = naive_dt.astimezone(tz)

    def init_auction_event_end_time_from_lot(self, auction_event: AuctionEvent, lot: Lot):
        """
        From lot.

        :param auction_event:
        :param lot:
        :return:
        """

        self.selenium_api.get(lot.url)
        self.selenium_api.wait_for_page_load()
        try:
            end_time_element = self.selenium_api.get_element(By.CLASS_NAME, "endTime")
        except NoSuchElementException:
            return None

        # '12/3/2025 10:00:00 PM'
        parse_format = '%m/%d/%Y %I:%M:%S %p'
        end_time_string = end_time_element.text.replace("End Time:", "")
        naive_dt = datetime.datetime.strptime(end_time_string, parse_format)
        tz = MAauction.get_auction_event_tz(auction_event)

        if tz is None:
            provinces = lot.guess_provinces(lot.raw_text)
            if len(provinces) == 0:
                breakpoint()
                raise RuntimeError(f"Expected 1 province: {provinces}")
            if len(provinces) > 1:
                logger.error(f"More than 1 province: {provinces}")
            tz = self.get_province_tz(provinces[0])
            if tz is None:
                breakpoint()
        auction_event.end_time = naive_dt.astimezone(tz)

    @staticmethod
    def init_auction_event_name(auction_event, title_element):
        """

        :param auction_event:
        :param title_element:
        :return:
        """

        parsed_url = urlparse(auction_event.url)
        query_params = str(parsed_url.query)
        auction_event.name = title_element.text
        if "filter" in query_params:
            auction_event.name += "-" + query_params.split("=")[1].strip("()").split(":")[1]

    @staticmethod
    def init_auction_event_start_time(auction_event):
        """
        Bidding Opens: - 9:00 AM Wednesday November 5, 2025

        :return:
        """

        if "Bidding Now Open!" in auction_event.description:
            return datetime.datetime.now(tz=datetime.timezone.utc)

        if "Bidding Opens:" in auction_event.description:
            for line in auction_event.description.split("\n"):
                closing_text_index = line.find("Bidding Opens:")
                if closing_text_index > -1:
                    line = line.strip("- ")
                    break
            else:
                breakpoint()
                raise ValueError("Was not able to find start time string:  1")

            auction_event.start_time = MAauction.extract_time(auction_event, line)
        else:
            logger.error(f"Was not able to find start time in description: {auction_event.description}")
            return

    @staticmethod
    def get_auction_event_tz(auction_event):
        """
        Find tz if single province.

        :param auction_event:
        :return:
        """

        provinces = auction_event.provinces.split(",")
        if not provinces:
            breakpoint()
        provinces = list(set(provinces) - {"offsite"})
        if len(provinces) > 1:
            return None
        return MAauction.get_province_tz(provinces[0])

    @staticmethod
    def get_province_tz(province):
        """
        Province is string

        :param province:
        :return:
        """

        if province == "alberta":
            tz = ZoneInfo("America/Edmonton")
        elif province == "manitoba":
            tz = ZoneInfo("America/Winnipeg")
        elif province == "ontario":
            tz = ZoneInfo("America/Toronto")
        elif province.lower() == "new brunswick":
            tz = ZoneInfo("America/Halifax")
        else:
            breakpoint()
            raise ValueError(province)
        return tz

    @staticmethod
    def extract_time(auction_event, line):
        """
        Extract time from line.

        :param auction_event:
        :param line:
        :return:
        """

        if "2025" in line:
            year = 2025
        elif "2026" in line:
            year = 2026
        else:
            # 'https://www.maauctions.com/auctions/24918-january-10th-2026-automotive-timed-vehicles-and-rvs-alberta'
            new_line = auction_event.url.replace("th-", " ").replace("-", " ")
            if line != new_line:
                logger.info(f"Trying to extract date from URL: {auction_event.url}")
                ret = MAauction.extract_time(auction_event, new_line)
                if ret is not None:
                    return ret
                logger.info(f"Manual check the date for: {auction_event.url}")
            else:
                logger.info(f"Extracting date failed from URL: {auction_event.url}")
                return None

            raise_exception = True
            breakpoint()
            if raise_exception:
                raise RuntimeError(auction_event)
        line_lower = line.lower()
        for str_month, month in Provider.MONTH_BY_NAME.items():
            if str_month in line_lower:
                day_index = line_lower.index(str_month)+len(str_month)
                day = ""
                for day_digit in line[day_index:].strip():
                    if not day_digit.isdigit():
                        break
                    day += day_digit
                try:
                    day = int(day)
                except ValueError:
                    breakpoint()
                    day = 1
                break
        else:
            raise_exception = True
            breakpoint()
            if raise_exception:
                raise RuntimeError(f"Was not able to find month in line '{line}', {auction_event}")

        dt_aware = datetime.datetime(year, month, day, 9, 0, 0, tzinfo=MAauction.get_auction_event_tz(auction_event))
        return dt_aware.astimezone(datetime.timezone.utc)

    def init_auction_event_end_time(self, auction_event: AuctionEvent):
        """
        Human readable to utc

        Lots Start Closing: 9:00AM Wednesday November 12,2025

        :param auction_description:
        :return:
        """
        if "Auction closing: " in auction_event.description:
            for line in auction_event.description.split("\n"):
                closing_text_index = line.find("Auction closing: ")
                if closing_text_index > -1:
                    break
            else:
                breakpoint()
                raise ValueError("Was not able to find end time data")
            line = line[closing_text_index + len("Lots Start Closing:"):].strip()
        elif "Lots Start Closing:" in auction_event.description:
            for line in auction_event.description.split("\n"):
                closing_text_index = line.find("Lots Start Closing:")
                if closing_text_index > -1:
                    break
            else:
                breakpoint()
                raise ValueError("Was not able to find end time data")

            line = line[closing_text_index + len("Lots Start Closing:"):].strip()
        else:
            logger.error(f"Was not able to find end time in description: {auction_event.description}")
            return

        auction_event.end_time = self.extract_time(auction_event, line)

    def init_real_auction_event_url(self, base_url):
        """
        Some auctions located on other urls- suburlss.

        :param base_url:
        :return:
        """

        self.selenium_api.get(base_url)
        self.selenium_api.wait_for_page_load()
        try:
            self.selenium_api.get_element(By.CLASS_NAME, "pagination")
            return base_url
        except NoSuchElementException:
            button = self.selenium_api.get_element(By.CLASS_NAME, "viewAllLotsBtn")
            button.click()
            return self.selenium_api.driver.current_url

    def load_auction_event_lots(self, auction_event: AuctionEvent):
        """
        Init from the web.

        :param auction_event:
        :return:
        """

        lots = []

        auction_event_address = auction_event.provinces \
            if auction_event.provinces and "," not in auction_event.provinces \
            else None

        for page_counter in range(1, self.get_page_count(self.add_query_params(auction_event.url, {"page": 1, "pageSize": 125}))+1):
            lots += self.load_page_lots(self.add_query_params(auction_event.url, {"page": page_counter, "pageSize": 125}),
                                                      auction_event_address=auction_event_address)

        for i, lot in enumerate(lots):
            logger.info(f"Updating lot current max and starting bid: {i}/{len(lots)}")
            try:
                lot.current_max = self.init_lot_current_bid_from_url(lot.url)
                lot.starting_bid = self.find_lot_starting_bid(lot) if lot.current_max == 0 else lot.current_max
            except Exception as inst_error:
                logger.info(f"Error: {repr(inst_error)}")
                breakpoint()

            if lot.starting_bid is None:
                breakpoint()
            logger.info(f"Updated {lot.url}, {lot.current_max=}, {lot.starting_bid=}")
        self.disconnect()

        return lots

    def validate(self, auction_event):
        """
        Validate the auction event lots.

        :param auction_event:
        :return:
        """

        old_lots_by_maa_id = {}
        for lot in auction_event.lots:
            lot_maa_id = self.get_lot_maauction_id(lot)
            if lot_maa_id in old_lots_by_maa_id:
                logger.error(f"Duplicate ids: {old_lots_by_maa_id[lot_maa_id]} {lot.name=}")
            old_lots_by_maa_id[lot_maa_id] = lot

        if len(auction_event.lots) != len(old_lots_by_maa_id):
            raise ValueError("Fix the duplicates.")

    def get_lot_maauction_id(self, lot: Lot) -> str:
        """
        1W, 343W etc

        :param lot:
        :return:
        """

        lot_maa_id_part = lot.name.split("\n")[0]
        if not lot_maa_id_part.startswith("Lot") or (not lot_maa_id_part.endswith("W") and not lot_maa_id_part[-1].isdigit()):
            raise ValueError(f"Can not decide lot id from: '{lot.name}', '{lot.url}'")
        return lot_maa_id_part.strip().split(" ")[1]

    def init_lot_current_bid_from_url(self, lot_url):
        self.selenium_api.get(lot_url)
        self.selenium_api.wait_for_page_load()
        try:
            element = self.selenium_api.get_element(By.CLASS_NAME, "currentBid")
        except NoSuchElementException:
            element = self.selenium_api.get_element(By.ID, "app-body")
            element_text = element.text
            if "Loading" in element_text:
                time.sleep(2)
                element = self.selenium_api.get_element(By.ID, "app-body")
                element_text = element.text

            if "Lot not found" not in element_text:
                logger.error(f"'Lot not found' not in {element_text}")
                raise
            return -1

        element_text = element.text
        if "Current Bid:" not in element_text:
            breakpoint()

        element_text = element_text.replace("Current Bid:", "").replace("$", "").replace("CAD", "").replace(",", "")
        return float(element_text)

    def find_lot_starting_bid(self, lot: Lot):
        """
        Try guessing the current max- it can be set to minimum.

        :param lot:
        :return:
        """

        for retry_counter in range(6):
            self.selenium_api.get(lot.url)
            self.selenium_api.wait_for_page_load()
            try:
                element = self.selenium_api.get_element(By.CLASS_NAME, "startingBid")
                break
            except NoSuchElementException as error_inst:
                logger.warning(f"Fetch startingBid failed: {lot.url}: {repr(error_inst)}")

                h1_elements = self.selenium_api.get_elements(By.TAG_NAME, "h1")
                for h1_element in h1_elements:
                    if h1_element.text == "500":
                        time.sleep(10)
                        break
        else:
            raise TimeoutError(f"Was not able to fetch: {lot.url}")

        try:
            bid_price = element.text[element.text.find("$") + 1:]
            return float(bid_price.replace(",", ""))
        except Exception as inst_error:
            raise ValueError(f"Was not able to find minimal bid for: {lot.url}") from inst_error

    @staticmethod
    def add_query_params(url, params):
        """
        Adds or updates query parameters in a given URL.

        Args:
            url (str): The original URL.
            params (dict): A dictionary of key-value pairs to add or update.

        Returns:
            str: The URL with the added/updated query parameters.
        """

        parsed_url = urlparse(url)
        query_params = {key_val.split("=")[0]: key_val.split("=")[1] for key_val in parsed_url.query.split('&')} if parsed_url.query else {}
        query_params.update(params)
        new_query_string = urlencode(query_params)

        # Reconstruct the URL with the new query string
        new_url = urlunparse(parsed_url._replace(query=new_query_string))
        return new_url

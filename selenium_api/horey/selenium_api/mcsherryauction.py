import json
from pathlib import Path

from horey.selenium_api.selenium_api import SeleniumAPI
from selenium.webdriver.common.by import By
from horey.h_logger import get_logger
from horey.common_utils.common_utils import CommonUtils
from horey.selenium_api.lot import Lot
from horey.selenium_api.provider import Provider

logger = get_logger()


class Mcsherryauction(Provider):
    def __init__(self):
        super().__init__()
        self.name = "mcsherryauction"
        initial_page = "https://bid.mcsherryauction.com/Man-Cave-Vintage-Service-Station-General-Store-Items-Oct28th-41_as109978"
        # initial_page = "https://bid.mcsherryauction.com/Consignment-Auction-Equip-Building-Supplies-Tractors-Vehicles-Oct29th-42_as111330"
        # initial_page = "https://bid.mcsherryauction.com/Estate-Moving-44-Nov-5th_as111253"
        self.initial_page = "https://bid.mcsherryauction.com/Consignment-Auction-Equip-Building-Supplies-Tractors-Vehicles-Oct29th-42_as111330"
        self.main_page = "https://bid.mcsherryauction.com"

    def load_page_items(self, page_id):
        """
        Load free items.

        :return:
        """

        logger.info(f"Loading page {page_id} items")

        items = []

        self.selenium_api.get(self.initial_page+f"_p{page_id}?ps=100")
        self.selenium_api.wait_for_page_load()
        item_elements = self.selenium_api.get_elements_by_class("gridItem")
        for item_element in item_elements:
            item = Lot()
            link_element = item_element.find_element(By.TAG_NAME, "a")

            if "No Bids Yet" in item_element.text:
                item.high_bid = 0
            else:
                try:
                    highbid_element = item_element.find_element(By.CLASS_NAME, "gridView_highbid")
                except Exception as inst:
                    print(item_element.text)
                    break
                if "Current Bid: " not in highbid_element.text:
                    breakpoint()
                    raise ValueError("Current Bid does not present")
                item.high_bid = float(highbid_element.text.split(" ")[-1].replace(",", ""))

            item.url = link_element.get_attribute('href')
            item_image_element = item_element.find_element(By.TAG_NAME, "img")
            item.image_url = item_image_element.get_attribute('src')
            element_title = item_element.find_element(By.CLASS_NAME, "gridView_title")
            item.name = element_title.text
            items.append(item)

        return items

    def get_page_count(self):
        """
        Get number of pages to fetch

        :return:
        """

        self.selenium_api.get(self.initial_page+f"_p{1}?ps=100")
        self.selenium_api.wait_for_page_load()
        pagingbar_pages = self.selenium_api.get_elements_by_class("pagingbar_pages")
        a_elements = pagingbar_pages[-1].find_elements(By.TAG_NAME, "a")
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

    def init_all_items(self, update_info=True):
        """
        Load all items.

        :return:
        """

        initial_page = self.initial_page

        if not initial_page.startswith("https://bid.mcsherryauction.com/"):
            raise NotImplementedError("https://bid.mcsherryauction.com/")

        file_name = initial_page[len("https://bid.mcsherryauction.com/"):] + ".json"
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

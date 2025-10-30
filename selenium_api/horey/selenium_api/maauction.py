import json

from selenium.webdriver.common.by import By
from horey.h_logger import get_logger
from horey.common_utils.common_utils import CommonUtils
from horey.selenium_api.lot import Lot
from horey.selenium_api.provider import Provider

logger = get_logger()


class MAauction(Provider):
    def __init__(self):
        super().__init__()
        self.name = "maauctions"
        self.initial_page = "https://www.maauctions.com/auctions/24839-october-28-2025-sporting-goods-liquidation-timed-auction-manitoba"
        self.main_page = "https://www.maauctions.com"

    def load_page_items(self, page_id):
        """
        Load free items.

        :return:
        """

        logger.info(f"Loading page {page_id} items")

        items = []
        self.selenium_api.get(self.initial_page+f"?page={page_id}&pageSize=125")
        self.selenium_api.wait_for_page_load()
        item_list_element = self.selenium_api.get_element(By.CLASS_NAME, "lotList")
        item_elements = item_list_element.find_elements(By.CLASS_NAME, "lot")
        for item_element in item_elements:
            lot = Lot()
            link_element = item_element.find_element(By.TAG_NAME, "a")

            try:
                highbid_element = item_element.find_element(By.CLASS_NAME, "tile-two-winning-bid")
            except Exception as inst:
                print(item_element.text)
                break
            if not highbid_element.text.startswith("$"):
                raise ValueError("Current Bid does not present")
            lot.high_bid = float(highbid_element.text[1:])

            lot.url = link_element.get_attribute('href')
            item_image_element = item_element.find_element(By.TAG_NAME, "img")
            lot.image_url = item_image_element.get_attribute('src')
            element_title = item_element.find_element(By.CLASS_NAME, "lot-title")
            lot.name = element_title.text
            items.append(lot)

        return items

    def get_page_count(self):
        """
        Get number of pages to fetch

        :return:
        """

        self.selenium_api.get(self.initial_page+f"?page=1&pageSize=125")
        self.selenium_api.wait_for_page_load()
        pagingbar_element = self.selenium_api.get_element(By.CLASS_NAME, "pagination")
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

    def init_auctions(self):
        """
        Load free items.

        :return:
        """

        self.connect()

        logger.info(f"Loading provider {self.name} auctions")

        items = []
        self.selenium_api.get(self.main_page)
        self.selenium_api.wait_for_page_load()
        item_list_element = self.selenium_api.get_element(By.CLASS_NAME, "lotList")
        item_elements = item_list_element.find_elements(By.CLASS_NAME, "lot")
        for item_element in item_elements:
            lot = Lot()
            link_element = item_element.find_element(By.TAG_NAME, "a")

            try:
                highbid_element = item_element.find_element(By.CLASS_NAME, "tile-two-winning-bid")
            except Exception as inst:
                print(item_element.text)
                break
            if not highbid_element.text.startswith("$"):
                raise ValueError("Current Bid does not present")
            lot.high_bid = float(highbid_element.text[1:])

            lot.url = link_element.get_attribute('href')
            item_image_element = item_element.find_element(By.TAG_NAME, "img")
            lot.image_url = item_image_element.get_attribute('src')
            element_title = item_element.find_element(By.CLASS_NAME, "lot-title")
            lot.name = element_title.text
            items.append(lot)

        return items
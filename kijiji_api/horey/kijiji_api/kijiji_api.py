import time

import selenium.webdriver.remote.webelement

from horey.kijiji_api.kijiji_api_configuration_policy import KijijiAPIConfigurationPolicy
from horey.selenium_api.selenium_api import SeleniumAPI
from collections import defaultdict
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException
from horey.h_logger import get_logger
from horey.common_utils.common_utils import CommonUtils
from horey.common_utils.free_item import FreeItem

logger = get_logger()

class KijijiAPI:
    NAME = "Kijiji"
    def __init__(self, configuration: KijijiAPIConfigurationPolicy = None, selenium_api=None):
        self._selenium_api = selenium_api
        self.configuration = configuration

    @property
    def selenium_api(self):
        if self._selenium_api is None:
            self._selenium_api = SeleniumAPI()
        return self._selenium_api


    def get_free_items(self, address="winnipeg"):
        """
        Load all free items.

        :return:
        """

        ret = []
        for page_id in range(1, 3):
            ret += self.get_free_items_single_page(page_id)
        return ret


    def get_free_items_single_page(self, page_id):
        """
        Free Items from single page

        """

        logger.info(f"Loading page {page_id}")
        self.selenium_api.get(
            f"https://www.kijiji.ca/b-buy-sell/winnipeg/free/page-{page_id}/k0c10l1700192?search=true&sort=dateDesc&view=list")
        self.selenium_api.wait_for_page_load()
        items_list = self.selenium_api.get_by_css_selector("data-testid", "srp-search-list")

        items = self.selenium_api.get_lis_from_ul(items_list)
        lst_ret = []
        for item in items:
            item_title = self.selenium_api.get_sub_elements_by_css_selector(item, "data-testid", "listing-link")
            if len(item_title) != 1:
                if item.is_displayed():
                    logger.error(f"{item_title=} should be single item")
                continue
            listing_link = item_title[0].get_property("href")
            item_title = item_title[0].text

            item_price = self.selenium_api.get_sub_elements_by_css_selector(item, "data-testid", "listing-price")
            if len(item_price) != 1:
                if item.is_displayed():
                    logger.error(f"{item_price=} should be single item")

                continue

            item_price = item_price[0].text
            if item_price != "Free":
                continue

            item_description = self.selenium_api.get_sub_elements_by_css_selector(item, "data-testid", "listing-description")
            if len(item_description) != 1:
                raise RuntimeError(f"Item description element is not single: {len(item_description)}")
            item_description = item_description[0].text
            imgs_element = item.find_element(By.TAG_NAME, "img")
            image_url = imgs_element.get_attribute("src")

            item = FreeItem(item_title, listing_link, image_url=image_url, description=item_description, address="Winnipeg")
            lst_ret.append(item)

        return lst_ret

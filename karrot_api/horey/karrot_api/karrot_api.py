import time

import selenium.webdriver.remote.webelement

from horey.karrot_api.karrot_api_configuration_policy import KarrotAPIConfigurationPolicy
from horey.selenium_api.selenium_api import SeleniumAPI
from collections import defaultdict
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException
from horey.h_logger import get_logger
from horey.common_utils.common_utils import CommonUtils
from horey.common_utils.free_item import FreeItem

logger = get_logger()

class KarrotAPI:
    def __init__(self, configuration: KarrotAPIConfigurationPolicy = None, selenium_api=None):
        self._selenium_api = selenium_api
        self.configuration = configuration

    @property
    def selenium_api(self):
        if self._selenium_api is None:
            self._selenium_api = SeleniumAPI()
        return self._selenium_api

    def reload_elements(self):
        """
        Using dynamic loading
        
        :return: 
        """
        main = CommonUtils.load_object_from_module_raw("/Users/alexeybeley/git/horey/karrot_api/horey/karrot_api/dynamic.py", "main")
        free_items = main(self.selenium_api)

    def main(self):
        count = 2
        free_items = []
        for i in range(count):
            try:
                self.selenium_api.scroll_to_bottom()
            except Exception as inst_error:
                logger.exception(inst_error)
                breakpoint()
            logger.info(f"Going to sleep {i}/{count}")
            time.sleep(2)

            try:
                free_items = self.fetch_free_items_from_page()
            except Exception as inst_error:
                logger.exception(inst_error)
                continue

            len_free_items = len(free_items)
            logger.info(f"Fetched: {len_free_items} free items")
            if len_free_items > 230:
                break
        return free_items


    def get_free_items(self):
        """
        Load all free items.

        :return:
        """

        self.selenium_api.connect()

        self.selenium_api.get("https://www.facebook.com/marketplace/winnipeg/free/?exact=false")
        self.selenium_api.wait_for_page_load()
        self.close_popup()
        self.selenium_api.scroll_to_bottom()
        ret = self.fetch_free_items_from_page()
        logger.info(f"Total fetched free items from Facebook: {len(ret)}")
        return ret

    def load_free_logged_in(self):
        """
        Load free items.

        :return:
        """

        self.selenium_api.connect()

        self.selenium_api.get("https://www.facebook.com/marketplace/winnipeg/free/?exact=false")
        self.selenium_api.wait_for_page_load()
        login = False
        breakpoint()
        if login:
            self.login()
        self.reload_elements()
        breakpoint()

        breakpoint()
        count = 6
        item_elements = []
        for i in range(count):
            self.selenium_api.scroll_to_bottom()
            logger.info(f"Going to sleep {i}/{count}")
            time.sleep(2)

            item_elements = self.fetch_free_items_from_page()
            if len(item_elements) > 230:
                break

        breakpoint()


    def fetch_free_items_from_page(self):
        """
        Fetch elements

        :return:
        """

        count = 10
        for i in range(count):
            by_class = defaultdict(list)
            try:
                divs = self.selenium_api.get_elements_by_tagname("div")
                for div in divs:
                    by_class[div.get_attribute("class")].append(div)

                logger.info(f"Fetched divs classIds: {len(by_class)=}")
                return self.get_free_items_from_elements_by_class_id(by_class)
            except StaleElementReferenceException:
                logger.error(f"StaleElementReferenceException. Going to sleep {i}/{count}")
            time.sleep(1)

        raise TimeoutError("Was not able to fetch free items")

    def get_free_items_from_elements_by_class_id(self, by_class):
        """
        Get item elements from class dict

        :param by_class:
        :return:
        """

        for class_id, values in by_class.items():
            if len(values) < 10:
                continue
            if len(values) > 100:
                continue
            logger.info(f"Initializing item elements by class ID: {class_id}")
            free_items = self.get_free_items_by_class_id(values)
            logger.info(f"Initialized {len(free_items)=} free items ")
            if len(free_items) < 10:
                continue
            
            return free_items
        else:
            raise ValueError("Initializing free items")


    def get_free_items_by_class_id(self, elements):
        """
        Magic happens here

        :param elements:
        :return:
        """

        lst_ret = []
        urls = []
        for element in elements:
            logger.info(f"Raw: {element.text=}")
            free_item = self.generate_free_item(element)
            if free_item is None:
                continue
            if free_item.url in urls:
                continue
            urls.append(free_item.url)
            lst_ret.append(free_item)

        if len(lst_ret) > 10:
            return lst_ret
        return []


    def generate_free_item(self, item_element: selenium.webdriver.remote.webelement.WebElement)->FreeItem:
        """
        Generate Free Item from item element
        :param item_element:
        :return:
        """
        try:
            image = item_element.find_element(By.TAG_NAME, "img")
        except NoSuchElementException:
            return None
        image_url = self.selenium_api.get_image_element_href(image)

        item_text_blocks = item_element.find_elements(By.TAG_NAME, "div")
        item_text_blocks += item_element.find_elements(By.TAG_NAME, "span")

        item_hrefs = item_element.find_elements(By.TAG_NAME, "a")
        url = None
        for item_href in item_hrefs:
            url = item_href.get_attribute("href")


        unique_lines = {line for text_block in item_text_blocks for line in text_block.text.split("\n")}
        lines = []
        for line in unique_lines:
            if not line:
                continue
            if line.replace("!", "").lower() == "free":
                continue
            lines.append(line)

        description = "\n".join(lines)
        return FreeItem("Facebook", url, image_url=image_url, description=description)

    def close_popup(self):
        """
        Close the popup that asks to login

        :return:
        """

        div_elements = self.selenium_api.get_elements(By.TAG_NAME, "div")
        for div_close in div_elements:
            try:
                if div_close.get_attribute("aria-label") == "Close":
                    div_close.click()
                    break
            except Exception:
                pass

    def login(self):
        """
        Login to facebook

        :return:
        """

        form_elements = self.selenium_api.get_elements(By.TAG_NAME, "form")
        for form_element in form_elements:
            if "Email or phone number" in form_element.text:
                break
        else:
            breakpoint()
            raise ValueError("Can not find login form")

        div_elements = form_element.find_elements(By.TAG_NAME, "div")
        for div_user in div_elements:
            if div_user.text == "Email or phone number":
                inputs = div_user.find_elements(By.TAG_NAME, "input")
                if not inputs:
                    continue
                for input_element in inputs:
                    try:
                        logger.info("Trying to write to user div->input")
                        input_element.send_keys(self.configuration.username)
                        break
                    except ElementNotInteractableException:
                        pass
                else:
                    continue
                break
        else:
            breakpoint()
            raise ValueError("Can not find  user input")

        for div_user in div_elements:
            if div_user.text == "Password":
                inputs = div_user.find_elements(By.TAG_NAME, "input")
                if not inputs:
                    continue
                for input_element in inputs:
                    try:
                        logger.info("Trying to write to password div->input")
                        input_element.send_keys(self.configuration.password)
                        break
                    except ElementNotInteractableException:
                        pass
                else:
                    continue
                break
        else:
            breakpoint()
            raise ValueError("Can not find  user input")

        for div in div_elements:
            if div.text == "Log In" and div.get_attribute("role") == "button":
                div.click()
                break
        else:
            raise ValueError("Was not able to find the login button to click")

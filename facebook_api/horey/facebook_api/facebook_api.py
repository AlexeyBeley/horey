import time

import selenium.webdriver.remote.webelement

from horey.facebook_api.facebook_api_configuration_policy import FacebookAPIConfigurationPolicy
from horey.selenium_api.selenium_api import SeleniumAPI
from collections import defaultdict
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from horey.h_logger import get_logger
from horey.common_utils.common_utils import CommonUtils
from horey.common_utils.free_item import FreeItem

logger = get_logger()

class FacebookAPI:
    def __init__(self, configuration:FacebookAPIConfigurationPolicy):
        self._selenium_api = None
        self.configuration = configuration

    @property
    def selenium_api(self):
        if self._selenium_api is None:
            self._selenium_api = SeleniumAPI(store_data=True)
        return self._selenium_api

    def reload_elements(self):

        main = CommonUtils.load_object_from_module_raw("/Users/alexeybeley/git/horey/facebook_api/horey/facebook_api/dynamic.py", "main")
        breakpoint()
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
                free_items = self.get_free_items()
            except Exception as inst_error:
                logger.exception(inst_error)
                breakpoint()
                continue

            len_free_items = len(free_items)
            logger.info(f"Fetched: {len_free_items} free items")
            if len_free_items > 230:
                break
        return free_items



    def load_free(self):
        """
        Load free items.

        :return:
        """

        self.selenium_api.connect(options="--no-sandbox --disable-gpu --disable-dev-shm-usage")

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

            item_elements = self.get_free_items()
            if len(item_elements) > 230:
                break

        breakpoint()


    def get_free_items(self):
        """
        Fetch elements

        :return:
        """

        lst_ret = []
        divs = self.selenium_api.get_elements_by_tagname("div")
        by_class = defaultdict(list)
        for div in divs:
            by_class[div.get_attribute("class")].append(div)

        candidate_batches_with_13_tokens = [values for class_name, values in by_class.items() if len(class_name.split(" ")) == 13]
        # The biggest number of divs with the same 13 tokens in class name are the item list
        candidate_item_elements = max(candidate_batches_with_13_tokens, key=lambda x: len(x))

        for item_element in candidate_item_elements:
            item = self.generate_free_item(item_element)
            if item:
                lst_ret.append(item)
        return lst_ret


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
        name = None
        for line in unique_lines:
            if not line:
                continue
            if line.replace("!", "").lower() == "free":
                continue
            lines.append(line)
            if not name and not line.lower().replace("ca$", "").isdigit():
                name = line

        description = "\n".join(lines)
        return FreeItem(name, url, image_url=image_url, description=description)

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

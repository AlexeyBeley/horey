from horey.selenium_api.selenium_api import SeleniumAPI
from selenium.webdriver.common.by import By
from horey.h_logger import get_logger

logger = get_logger()


class Item:
    def __init__(self):
        self.high_bid = None
        self.image_url = None
        self.url = None
        self.name = None
        self.description = None


class Mcsherryauction:
    def __init__(self):
        self.selenium_api = SeleniumAPI()
        self.initial_page = "https://bid.mcsherryauction.com/Man-Cave-Vintage-Service-Station-General-Store-Items-Oct28th-41_as109978_p{page_id}?ps=100"
        self.selenium_api.connect(options="--no-sandbox --disable-gpu --disable-dev-shm-usage")

    def load_page_items(self, page_id):
        """
        Load free items.

        :return:
        """

        items = []

        self.selenium_api.get(self.initial_page.format(page_id=page_id))
        self.selenium_api.wait_for_page_load()
        item_elements = self.selenium_api.get_elements_by_class("gridItem")
        for item_element in item_elements:
            item = Item()
            link_element = item_element.find_element(By.TAG_NAME, "a")

            highbid_element = item_element.find_element(By.CLASS_NAME, "gridView_highbid")
            if "Current Bid: " not in highbid_element.text:
                breakpoint()
                raise ValueError("Current Bid does not present")
            item.high_bid = float(highbid_element.text.split(" ")[-1])

            item.url = link_element.get_attribute('href')
            item_image_element = item_element.find_element(By.TAG_NAME, "img")
            item.image_url = item_image_element.get_attribute('src')
            breakpoint()
            self.selenium_api.get(item.url)
            element_item_description = self.selenium_api.get_element(By.ID, "cphBody_cbItemDescription")
            item.description = element_item_description.text
            items.append(item)

        breakpoint()

    def get_page_count(self):
        """
        Get number of pages to fetch

        :return:
        """

        self.selenium_api.get(self.initial_page.format(page_id=1))
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

    def init_all_items(self):
        """
        Load all items.

        :return:
        """
        items = []
        for page_counter in range(1,self.get_page_count()):
            items += self.load_page_items(page_counter)



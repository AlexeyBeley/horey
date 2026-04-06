import os
import time
import traceback
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException



from horey.h_logger import get_logger

logger = get_logger()


class SeleniumAPI:
    driver = None
    v_display = None
    def __init__(self, data_dir:Path=None, chromedriver_path:Path=None, chrome_path:Path=None):
        self.data_dir = data_dir
        self.chromedriver_path = chromedriver_path
        self.chrome_path = chrome_path
        self.proxy = None


    def wait_for_page_load(self, timeout=10):
        """Waits for the page to be fully loaded based on document.readyState.

        Args:
            timeout (int): Maximum time to wait in seconds (default: 10).

        Returns:
            bool: True if the page is loaded within the timeout, False otherwise.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script('return document.readyState === "complete";')
            )
            return True
        except:
            return False

    def connect(self):
        """
        Connect to the chrome driver.

        :param:
        :return:
        """
        if SeleniumAPI.driver is not None:
            return SeleniumAPI.driver

        logger.info("Connecting diver in SeleniumAPI")

        chrome_options = Options()
        if self.proxy:
            #chrome_options.add_argument(f"--proxy-server=http://{self.proxy}")
            chrome_options.add_argument(f"--proxy-server={self.proxy}")

        if self.chrome_path:
            return self.connect_from_chromedriver_file()

        service = Service()

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gp")
        chrome_options.add_argument("--disable-dev-shm-usage")
        if self.data_dir:
            chrome_options.add_argument(f"--user-data-dir={self.data_dir / 'chrome-profile'}")
            chrome_options.add_argument(f"--profile-directory=Profile1")

        SeleniumAPI.driver = webdriver.Chrome(service=service, options=chrome_options)
        # self.driver.maximize_window()
        SeleniumAPI.driver.set_window_size(1440, 900)
        SeleniumAPI.driver.set_window_position(0, 0)

    def connect_from_chromedriver_file(self):
        """
        Files were downloaded.

        :return:
        """

        logger.info(f"Options from chrome file: {self.chrome_path}")

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--single-process")
        # chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
        # chrome_options.add_argument(f"--data-path={mkdtemp()}")
        # chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        chrome_options.add_argument("--remote-debugging-pipe")
        chrome_options.add_argument("--verbose")
        chrome_options.add_argument("--log-path=/tmp")
        chrome_options.binary_location = str(self.chrome_path)

        logger.info(f"Connecting from chromedriver file: {self.chromedriver_path}")
        service = Service(
            executable_path=str(self.chromedriver_path),
            service_log_path="/tmp/chromedriver.log"
        )

        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        SeleniumAPI.driver = driver
        SeleniumAPI.driver.set_window_size(1440, 900)
        SeleniumAPI.driver.set_window_position(0, 0)
        return True


    @staticmethod
    def disconnect():
        if SeleniumAPI.driver is not None:
            SeleniumAPI.driver.quit()
            logger.info("Disconnecting diver in SeleniumAPI")
            SeleniumAPI.driver = None
        try:
            SeleniumAPI.v_display.stop()
        except Exception:
            pass

    def get_element(self, by, value) -> WebElement:
        """
        Reliably get element

        :param by:
        :param value:
        :return:
        """

        for _ in range(20):
            try:
                return self.driver.find_element(by, value)
            except StaleElementReferenceException:
                time.sleep(1)
        raise TimeoutError("Was not able to fetch element")

    def get_elements(self, by, value):
        """
        Reliably get list of elements

        :param by:
        :param value:
        :return:
        """

        if by == By.CSS_SELECTOR:
            # Use WebDriverWait to ensure the elements are present before attempting to find them.
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, value))
            )

        return self.driver.find_elements(by, value)

    def get_by_id(self, str_id):
        return self.driver.find_element(By.ID, str_id)

    def get_element_by_name(self, name):
        return self.driver.find_element(By.NAME, name)

    def get_element_by_xpath(self, path):
        return self.driver.find_element(By.XPATH, path)

    def get_elements_by_partial_link_text(self, link_text):
        return self.driver.find_elements(By.PARTIAL_LINK_TEXT, link_text)

    def get_elements_by_class(self, name):
        return self.driver.find_elements(By.CLASS_NAME, name)

    def get_by_css_selector(self, selector, value):
        return self.driver.find_element(By.CSS_SELECTOR,  f'[{selector}="{value}"]')

    def get_div_by_css_selector(self, selector, value):
        return self.driver.find_element(By.ID,  f'[{selector}="{value}"]')

    def get_elements_by_tagname(self, tagname):
        return self.driver.find_elements(By.TAG_NAME, tagname)

    def get_lis_from_ul(self, ul_element):
        return ul_element.find_elements(By.TAG_NAME, "li")

    def get_sub_elements_by_css_selector(self, element, selector, value):
        return element.find_elements(By.CSS_SELECTOR,  f'[{selector}="{value}"]')

    def get(self, url):

        self.connect()

        try:
            return SeleniumAPI.driver.get(url)
        except Exception as inst_err:
            logger.error(f"Exception occurred: {inst_err}")
            if "invalid session id" not in str(inst_err):
                raise

        SeleniumAPI.disconnect()
        self.connect()
        return SeleniumAPI.driver.get(url)

    def fill_input(self, str_id, input_data):
        search_box = self.get_by_id(str_id)
        search_box.send_keys(input_data)
        return search_box

    @staticmethod
    def retry(func, count, sleep_time):
        for i in range(count):
            try:
                return func()
            except Exception:
                print(f"Running retry on func {func.__name__} {i+1}/{count}")
                if i == count-1:
                    raise
            time.sleep(sleep_time)

    def click_by_class_name_and_text(self, class_name, text, retrty_count=10, sleep_time=0.1):
        def click_by_class_name_and_text_helper():
            obj = self.get_by_class_name_and_text(class_name, text, retrty_count=retrty_count,
                                                  sleep_time=sleep_time)
            obj.click()

        self.retry(click_by_class_name_and_text_helper, retrty_count, sleep_time)

    def get_by_class_name_and_text(self, class_name, text, retrty_count=10, sleep_time=0.1):
        for i in range(retrty_count):
            try:
                obj = self.get_by_class_and_text_raw(class_name, text)
                break
            except Exception as exception_inst:
                print(f"Retrying to get class by name and text: '{class_name}', '{text}'")
                time.sleep(sleep_time)
        else:
            raise exception_inst

        self.scroll_to(obj)
        time.sleep(0.5)
        return obj

    def get_by_class_and_text_raw(self, class_name, text):
        ret = []
        elements = self.driver.find_elements(By.CLASS_NAME, class_name)
        for element in elements:
            if element.text == text:
                ret.append(element)
        if len(ret) != 1:
            raise ValueError(f"Can not find single element by class name: '{class_name}' and internal text: '{text}'. "
                             f"Found {len(ret)} elements")
        return ret[0]

    def get_by_class_name(self, class_name):
        elements = self.driver.find_elements(By.CLASS_NAME, class_name)
        return elements

    def scroll_to(self, obj):
        obj_location = obj.location
        size = self.driver.get_window_size()
        width_offset = size["width"]//2
        height_offset = size["height"]//2

        new_location_x = obj_location["x"] - width_offset
        new_location_y = obj_location["y"] - height_offset

        self.driver.execute_script(f"window.scrollTo({new_location_x}, {new_location_y})")

    def wait_for_element_clickable(self, locator, timeout=10):
        """Waits for a specific element to be clickable on the page.

        Args:
            locator (tuple): A Selenium locator (e.g., (By.ID, "button_id")).
            timeout (int): Maximum time to wait in seconds (default: 10).

        Returns:
            selenium.webdriver.remote.webelement.WebElement or None: The found element if clickable, None otherwise.
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return element
        except:
            return None

    def wait_for_element_visible(self, locator, timeout=10):
        """Waits for a specific element to be visible on the page.

        Args:
            locator (tuple): A Selenium locator (e.g., (By.ID, "element_id")).
            timeout (int): Maximum time to wait in seconds (default: 10).

        Returns:
            selenium.webdriver.remote.webelement.WebElement or None: The found element if visible, None otherwise.
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return element
        except:
            return None

    def scroll_to_bottom(self):
        """
        Execute javascript to scroll.

        :return:
        """
        logger.info("Scrolling to bottom")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #logger.info("Sleeping 2 sec after scrolling")
        #time.sleep(2)
        logger.info("Sending command+r after reloading")
        ActionChains(self.driver).key_down(Keys.COMMAND).send_keys("r").key_up(Keys.COMMAND).perform()
        self.wait_for_page_load()

    @staticmethod
    def get_image_element_href(image: WebElement) -> str:
        """

        :param image:
        :return:
        """

        return image.get_attribute("src")

    def get_screenshot(self)-> Path:
        """
        Save screenshot to file.

        :return:
        """

        path = Path("/tmp/screenshot.png")
        if SeleniumAPI.driver is None:
            traceback.print_exc()

        SeleniumAPI.driver.save_screenshot(str(path))
        return path

    def throttled_get(self, url):
        """
        Get with throttling.

        :param url:
        :return:
        """

        retries = 10
        for i in range(10):
            self.get(url)
            self.wait_for_page_load()

            body = self.get_element(By.TAG_NAME, "body").text
            if "This page is displayed while the website verifies you are not a bot" in body:
                self.disconnect()
                sleep_time = 0.2 * (i+1)
                logger.info(f"{i}/{retries} Refetching after {sleep_time}")
                time.sleep(sleep_time)
                self.connect()
                continue
            return True
        raise TimeoutError(f"Was not able to fetch url: {url}")


import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumAPI:
    def __init__(self):
        self.driver = None
        self.path_to_driver = "./chromedriver"

    def connect(self):
        cService = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=cService)
        # self.driver.maximize_window()
        self.driver.set_window_size(1440, 900)
        self.driver.set_window_position(0, 0)

    def disconnect(self):
        self.driver.quit()

    def get_by_id(self, str_id):
        return self.driver.find_element(By.ID, str_id)

    def get(self, url):
        self.driver.get(url)

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

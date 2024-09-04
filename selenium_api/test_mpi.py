import time
from mpi import SeleniumAPI
import signal
from selenium.webdriver.common.by import By


stop = False
def handler(signum, frame):
    stop = True
signal.signal(signal.SIGTSTP, handler)


def click_on_driver(selenium_api):
    ret = selenium_api.get_by_id("authenticate-with-ddref")
    selenium_api.scroll_to(ret)
    ret.click()

def enter_credentials(selenium_api):
    ret = selenium_api.get_by_id("DocumentNumber")
    ret.send_keys("325905479")

    ret = selenium_api.get_by_id("Code")
    ret.send_keys("R3P1G7")

    ret = selenium_api.get_by_id("DateOfBirth")
    ret.send_keys("02/02/1987")

    ret = selenium_api.get_by_class_name("iCheck-helper")
    if len(ret) != 1:
        raise
    ret[0].click()
    breakpoint()
    ret = selenium_api.get_by_id("nextBtn")
    ret.click()


def choose_road_test(selenium_api):

    ret = selenium_api.get_by_id("link-container")
    elements = ret.find_elements(By.CLASS_NAME, "redirect-to-test-flow-container")
    for element in elements:
        if "Road Test" in element.text:
            hreflink = element.find_element(By.CLASS_NAME, "redirect-test-flow-href")
            hreflink.click()
            break
    else:
        raise Exception


def choose_language(selenium_api):
    class_name = "drop-down-form-group"
    dropdowns = selenium_api.get_by_class_name(class_name)
    dropdowns[0].click()
    time.sleep(2)
    class_name = "select2-results__option"
    ret = selenium_api.get_by_class_name(class_name)
    for x in ret:
        if "Passenger Vehicle" in x.text:
            x.click()
            break

    time.sleep(2)

    dropdowns[1].click()

    class_name = "select2-results__option"
    ret = selenium_api.get_by_class_name(class_name)
    for x in ret:
        if "English" in x.text:
            x.click()
            break

    ret = selenium_api.get_by_id("nextBtn")
    ret.click()


def choose_place_and_date(selenium_api):
    class_name = "select2-selection--single"
    dropdowns = selenium_api.get_by_class_name(class_name)
    dropdowns[0].click()

    class_name = "select2-results__option"
    ret = selenium_api.get_by_class_name(class_name)
    for x in ret:
        if "King Edward" in x.text:
            x.click()
            break

    str_id = "ToTime"
    ret = selenium_api.get_by_id(str_id)
    ret.send_keys("20:00")
    ret.click()


def main():
    selenium_api = SeleniumAPI()
    selenium_api.connect()
    selenium_api.get("https://onlineservices.mpi.mb.ca/drivertesting/identity/verify")
    time.sleep(2)
    click_on_driver(selenium_api)
    time.sleep(2)
    enter_credentials(selenium_api)
    time.sleep(2)
    choose_road_test(selenium_api)
    time.sleep(2)
    choose_language(selenium_api)
    time.sleep(2)
    choose_place_and_date(selenium_api)
    sleep_timeout = 10
    for x in range(1000):
        print(f"{x}/1000")
        ret = selenium_api.get_by_id("search-submit")
        ret.click()
        if book_the_test(selenium_api):
            break
        time.sleep(sleep_timeout)

def book_the_test(selenium_api):
    return False
    breakpoint()
    str_id = "appointment-table"
    table = selenium_api.get_by_id(str_id)
    rows = table.find_element(By.CLASS_NAME, "odd")
    rows_even = table.find_element(By.CLASS_NAME, "even")


main()

#
#
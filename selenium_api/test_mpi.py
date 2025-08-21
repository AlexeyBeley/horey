import time
from mpi import SeleniumAPI
import signal
from selenium.webdriver.common.by import By
import sys

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
    #ret.send_keys("325905479")
    ret.send_keys("11111")

    ret = selenium_api.get_by_id("Code")
    ret.send_keys("R3P2V1")

    ret = selenium_api.get_by_id("DateOfBirth")
    ret.send_keys("25/12/1987")

    ret = selenium_api.get_by_class_name("iCheck-helper")
    if len(ret) != 1:
        raise
    ret[0].click()
    breakpoint()
    ret = selenium_api.get_by_id("nextBtn")
    ret.click()


def choose_road_test(selenium_api):
    #breakpoint()
    #ret = selenium_api.get_by_id("link-container")
    ret = selenium_api.driver.find_element(By.CLASS_NAME,"service-description-field")
    ret.click()
    return
    elements = ret.find_elements(By.CLASS_NAME, "service-description-field")
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
        #if "King Edward" in x.text:
        # if "Main Street" in x.text:
        if "Bison" in x.text:
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
        try:
            ret = selenium_api.get_by_id("search-submit")
            ret.click()
        except Exception as inst:
            body = selenium_api.driver.find_element(By.TAG_NAME, "body")
            if "session has expired" in body.text:
                bell(2)
            breakpoint()
        if book_the_test(selenium_api):
            break
        time.sleep(sleep_timeout)


def bell(time_sleep):
    for i in range(2400):
        sys.stdout.write('\a')
        sys.stdout.flush()
        time.sleep(time_sleep)


def book_the_test(selenium_api):
    with open("./stop.txt") as file_handler:
        ret = file_handler.read()
    if ret == "stop":
        breakpoint()
    for _ in range(10):
        try:
            return book_the_test_helper(selenium_api)
        except Exception as inst:
            print(repr(inst))
            time.sleep(0.5)


def book_the_test_helper(selenium_api):
    requested_dates = ["18", "19", "20"]
    month = "sep"

    str_id = "appointment-table"
    table = selenium_api.get_by_id(str_id)
    selenium_api.scroll_to(table)
    rows = table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        if "Start Time" in row.text:
            continue
        if "There are no available" in row.text:
            continue
        print(row.text)
        cells = row.find_elements(By.TAG_NAME, "td")
        str_date = cells[1].text.lower()
        str_date = str_date.replace("2024", "year")
        print(f"{str_date=}")
        if month in str_date and any(requested_date in str_date for requested_date in requested_dates):
            bell(0.5)
            breakpoint()
    return False


main()

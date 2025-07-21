import json
import time
from selenium_api import SeleniumAPI
import sys
import requests
from horey.h_logger import get_logger
from pathlib import Path
import selenium

logger = get_logger()


def get_selenium_api():
    selenium_api = SeleniumAPI()
    selenium_api.connect()
    return selenium_api


def main():
    max_page = 3
    base_retries = 10
    silent = False

    selenium_api = get_selenium_api()
    file_path = Path(__file__).parent / "known_free.json"
    with open(file_path) as file_handler:
        known = json.load(file_handler)
    retries = base_retries
    while retries > 0:
        try:
            check_free(selenium_api, max_page, known)
        except Exception as err_instance:
            try:
                page_source = selenium_api.driver.page_source
            except selenium.common.exceptions.InvalidSessionIdException:
                selenium_api = get_selenium_api()
            except Exception as internal_error:
                logger.exception(internal_error)
                page_source = ""
            if "Too Many Requests" in page_source:
                message = f"(ERROR!)\n [Too Many Requests {retries}]"
                logger.info(message)
                send_telegram_message(message)
                time.sleep(30)
                continue

            if "Read timed out" in repr(err_instance):
                selenium_api = get_selenium_api()
                silent = True

            logger.exception(err_instance)
            #selenium_api = get_selenium_api()
            retries -= 1
            message = f"(ERROR!)\n [Left retries {retries}]"
            logger.info(message)
            if not silent:
                send_telegram_message(message)
            silent = False
            time.sleep(5)
            continue

        retries = base_retries
        logger.info(f"Finished checking {max_page} pages")
        with open(file_path, "w") as file_handler:
            json.dump(known, file_handler, indent=4)
        time.sleep(90)


def check_free(selenium_api, max_page, known):
    for page_id in range(1, max_page):
        check_single_page(page_id, selenium_api, known)
        time.sleep(5)


def check_single_page(page_id, selenium_api, known):
    logger.info(f"Loading page {page_id}")
    selenium_api.get(
        f"https://www.kijiji.ca/b-buy-sell/winnipeg/free/page-{page_id}/k0c10l1700192?search=true&sort=dateDesc&view=list")
    selenium_api.wait_for_page_load()
    items_list = selenium_api.get_by_css_selector("data-testid", "srp-search-list")

    items = selenium_api.get_lis_from_ul(items_list)
    for item in items:
        item_title = selenium_api.get_sub_elements_by_css_selector(item, "data-testid", "listing-link")
        if len(item_title) != 1:
            if not item.is_displayed():
                continue
            if item.text not in known:
                known[item.text] = {}
            continue
        listing_link = item_title[0].get_property("href")
        item_title = item_title[0].text

        item_price = selenium_api.get_sub_elements_by_css_selector(item, "data-testid", "listing-price")
        if len(item_price) != 1:
            if item.is_displayed():
                if item.text not in known:
                    known[item.text] = {}
                continue
            else:
                continue

        item_price = item_price[0].text
        if item_price != "Free":
            continue

        item_description = selenium_api.get_sub_elements_by_css_selector(item, "data-testid", "listing-description")
        if len(item_description) != 1:
            raise RuntimeError(f"Item description element is not single: {len(item_description)}")
        item_description = item_description[0].text
        if item_title in known:
            continue
        known[item_title] = {"price": item_price, "item_title": item_title, "item_description": item_description}

        message = f"({item_price})\n [{item_title}] {listing_link}\n:\n {item_description}"
        logger.info(message)

        send_telegram_message(message)


def bell(time_sleep, range):
    for i in range(range):
        sys.stdout.write('\a')
        sys.stdout.flush()
        time.sleep(time_sleep)


def send_telegram_message(message):
    """
    Sends a message to a Telegram chat using a bot.

    Args:
        bot_token (str): The API token of your Telegram bot.
        chat_id (str or int): The chat ID of the recipient (user or group).
        message (str): The text of the message to send.

    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """

    with open("/opt/kijiji.json") as fh:
        dict_config = json.load(fh)

    bot_token = dict_config["token"]
    chat_id = dict_config["chat_id"]
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message,
    }
    try:
        response = requests.post(api_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        return True
    except requests.exceptions.RequestException as e:
        logger.exception(e)
        return False


main()

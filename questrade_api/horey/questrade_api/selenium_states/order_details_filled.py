"""
State

"""

import datetime
import platform
import time
from pathlib import Path
from enum import Enum
from selenium.webdriver.common.by import By
from horey.questrade_api.selenium_states.selenium_state import SeleniumState
from horey.selenium_api.selenium_api import SeleniumAPI
from selenium.common.exceptions import StaleElementReferenceException, \
                            JavascriptException, ElementNotInteractableException, \
                            ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class OrderDetailsFilled(SeleniumState):

    class Order(Enum):
        SELL = 1
        BUY = 2 

    def __init__(self, selenium_api:SeleniumAPI, name:str, order_type:Order, symbol:str, price:float, parent:SeleniumState=None):
        super().__init__(selenium_api, name, parent=parent)
        self.order_type = order_type
        self.symbol = symbol
        self.price = price
        self.clicked_on_ignore_night_sales = False
    
    def reach_state(self):
        """
        Reach if not reached
        """

        if self.check_state_reached():
            return True
        
        if self.parent:
            self.parent.reach_state()
        
        self.reach_state_raw()

        if not self.check_state_reached():
            raise ValueError("Was not able to reach state")
    
    def reach_state_raw(self):
        """
        fill the data.

        """

        page_url = f"https://myportal.questrade.com/investing/summary/quote/{self.symbol}"
        if self.selenium_api.driver.current_url != page_url:
           self.selenium_open_symbol_page(self.symbol)
        
        if self.selenium_api.driver.current_url != page_url:
            raise ValueError("Was not able to open the page")

        limit_time = datetime.datetime.now() + datetime.timedelta(seconds=60)
        element_limit_price_div = self.get_element_limit_price_input_div(is_displayed=None, retries=1)
        # sometimes the click does not work
        while element_limit_price_div is None and datetime.datetime.now() < limit_time: 
            try:
                self.selenium_press_sell_button()
            except self.selenium_api.VisibilityError:
                pass
            # when the click worked we need to press ok
            self.check_and_dismiss_otc_popup()
            element_limit_price_div = self.get_element_limit_price_input_div(is_displayed=None, retries=1)
        
        if datetime.datetime.now() >= limit_time:
            raise TimeoutError("Was not able to press the button")

        if not self.clicked_on_ignore_night_sales:
            self.check_and_dismiss_night_trading_popup()

        self.fill_price()
        self.fill_trade_window()
            
        btn = self.selenium_api.get_shadowed_element_by_css_selector('button[data-qt*="order-entry-next-button"]', is_displayed=True)

        if not btn:
            # The order placing button is not visible.
            breakpoint()

    
    def selenium_open_symbol_page(self, symbol):
        """
        Open sybol page
        """

        return self.selenium_api.throttled_get(f"https://myportal.questrade.com/investing/summary/quote/{symbol}")

    
    def check_state_reached(self):
        """
        Check state
        """

        if self.selenium_api.driver.current_url != f"https://myportal.questrade.com/investing/summary/quote/{self.symbol}":
            return False
        element_limit_price_div = self.get_element_limit_price_input_div()
        if element_limit_price_div.get_attribute("value") != str(self.price):
            breakpoint()
            return False
        return True
        
    def fill_price(self):
        element_limit_price_div = self.get_element_limit_price_input_div(is_displayed=True, retries=20)
        if element_limit_price_div is None:
            breakpoint()
            raise ValueError("Do not see the limit price input div after pressing Sell button")
        if element_limit_price_div.get_attribute("value") == str(self.price):
            return True

        select_all_key = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL

        actions = ActionChains(self.selenium_api.driver)
        actions.click(element_limit_price_div)  # Focus the element
        actions.key_down(select_all_key).send_keys("a").key_up(select_all_key)
        actions.send_keys(Keys.BACKSPACE)
        actions.perform()

        # Force hard clearance of value via JS to override pre-filled values/masks
        for _ in range(50):
            try:
                self.selenium_api.driver.execute_script("arguments[0].value = '';", element_limit_price_div)
                break
            except JavascriptException:
                time.sleep(0.1)
        else:
            logger.warning("Was not able to hard delete contents of input")

        formatted_price = f"{self.price:.4f}".rstrip('0').rstrip('.') if isinstance(self.price, float) else str(self.price)
        # 4. Input the new float price
        element_limit_price_div.send_keys(formatted_price)

        # 5. Dispatch UI events so Angular updates validation & recalculates "Estimated order total"
        self.selenium_api.driver.execute_script("""
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
        """, element_limit_price_div)
    
    def click_time_frame_selection_chip(self):
        """
        Find the "Day" chip and press it.
        """
        return self.selenium_api.driver.execute_script("""
            function clickChip(root) {
            if (!root) return false;

            // Look for q-chip or label containing "Day"
            const labels = Array.from(root.querySelectorAll('q-chip, label, .q-chip-label'));
            for (let el of labels) {
                if (el.textContent && el.textContent.trim() === 'Day') {
                    const chip = el.closest('q-chip') || el;
                    chip.click();
                    return true;
                }
            }

            // Search inside shadow roots
            for (let child of root.querySelectorAll('*')) {
                if (child.shadowRoot) {
                    if (clickChip(child.shadowRoot)) return true;
                }
            }
            return false;
            }
            return clickChip(document);
            """)

    def fill_trade_window(self):
        """
        Do it using JS
        """

        if not self.click_time_frame_selection_chip():
            breakpoint()
            raise ValueError("Was not able to press the time fram selection")

        js_folder_path = Path(__file__).parent / "js_helpers"
        file_path = js_folder_path / "get_symbol_time_frames.js"
        lines = self.selenium_api.run_javascript_file(file_path)
        
        frames = []
        for line in lines:
            if "DayActive" in line:
                frames.append("Day")
                continue
            if "GTC" in line:
                frames.append("GTC")
                continue
            if "GTEM" in line:
                frames.append("GTEM")
                continue
            if "Overnight" in line:
                frames.append("Overnight")
                continue
            breakpoint()

        if "GTEM" in frames:
            string_replacements = {"STRING_REPLACEMENT_WINDOW_ABBR": "GTEM"}
        else:
            string_replacements = {"STRING_REPLACEMENT_WINDOW_ABBR": "DAY"}
        file_path = js_folder_path / "template_press_trade_window_choice.js"
        ret = self.selenium_api.run_javascript_file(file_path, string_replacements=string_replacements)
        return string_replacements["STRING_REPLACEMENT_WINDOW_ABBR"] 

    def get_element_limit_price_input_div(self, is_displayed=True, retries=50):
        """
        Get div input
        """

        for _ in range(retries):
            div_input = self.get_div_input_by_label_raw("Limit Price")
            if div_input is None:
                time.sleep(0.1)
                continue
        
            if is_displayed is not None and div_input.is_displayed() != is_displayed:
                raise self.selenium_api.VisibilityError(f"Input {label_text} state { div_input.is_displayed()} is not in required staet: {is_displayed}")

            return div_input
            
        return None
    
    def get_div_input_by_label_raw(self, label_text):
        """
        Find using JS
        """
        js_script = """
        function findInShadow(root = document) {
            // 1. Try finding input relative to the label
            let labels = Array.from(root.querySelectorAll('label'));
            for (let label of labels) {
                if (label.textContent.trim() === 'STRING_REPLACEMENT_LABEL_TEXT') {
                let container = label.closest('.oe-input-container');
                if (container) return container.querySelector('input');
                }
            }

            // 2. Direct fallback using container classes
            let el = root.querySelector('div.oe-input input');
            if (el) return el;

            // 3. Recurse down Shadow Roots
            for (let child of root.querySelectorAll('*')) {
                if (child.shadowRoot) {
                    let found = findInShadow(child.shadowRoot);
                    if (found) return found;
                }
            }
            return null;
        }

        return findInShadow();
        """

        js_script = js_script.replace("STRING_REPLACEMENT_LABEL_TEXT", label_text)
        div_input = self.selenium_api.driver.execute_script(js_script)
        return div_input

    def selenium_press_sell_button(self):
        """
        Fallback that works 50% of the time:
        if not btn:
            btn = self.selenium_api.get_shadowed_element_by_text("button", "Sell")
        """

        btn = None
        limit_time = datetime.datetime.now() + datetime.timedelta(seconds=60)
        while btn is None and datetime.datetime.now() < limit_time: 
            btn = self.selenium_api.get_shadowed_element_by_css_selector('button[data-qt*="sell-button"]', is_displayed=True)
            if btn is not None:
                break
            time.sleep(1)
        else:
            raise TimeoutError("Was not able to find sell button during 60 seconds")

        try:
            btn.click()
        except ElementNotInteractableException:
            logger.info("Sell button click: ElementNotInteractableException")
            raise
        except StaleElementReferenceException:
            logger.info("Sell button click: StaleElementReferenceException")
            raise
        except ElementClickInterceptedException:
            self.selenium_api.get_screenshot()
            breakpoint()

    def check_and_dismiss_otc_popup(self, timeout=3):
        """
        Checks if the OTC/PINK sheet confirmation popup is present inside shadow roots.
        If found, returns True and clicks the 'OK' button.
        """
        
        btn = self.selenium_api.get_shadowed_element_by_css_selector('button[data-qt*="otc-confirm-notification-ok-button"]')
        if btn is not None:
            btn.click()
            return True
        return False

    def check_and_dismiss_night_trading_popup(self):
        js_script = """
        const searchTarget = "ow would you like to trade";

        function findAndHandlePopup(root) {
        if (!root) return null;

        // Check all elements inside the current root for matching header text
        const elements = root.querySelectorAll('*');
        for (let el of elements) {
            const text = (el.textContent || '').toLowerCase();

            // Check if this container holds the OTC popup title
            if (text.includes(searchTarget)) {
                return el;
            }

            // Recursively traverse open shadow roots
            if (el.shadowRoot) {
                const found = findAndHandlePopup(el.shadowRoot);
                if (found) return found;
            }
        }
        return null;
        }
        return findAndHandlePopup(document);
        """

        element = self.selenium_api.driver.execute_script(js_script)
        if not element:
            return
        all_descendants = element.find_elements("xpath", ".//*")
        ret = [x for x in all_descendants if "Place a day order" in x.text]
        if ret and ret[0].is_displayed():
            ret[0].click()
            self.clicked_on_ignore_night_sales = True

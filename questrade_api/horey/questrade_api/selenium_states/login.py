"""
Login state.

"""
import time
from selenium.webdriver.common.by import By
from horey.questrade_api.selenium_states.selenium_state import SeleniumState
from horey.selenium_api.selenium_api import SeleniumAPI

class Login(SeleniumState):
    """
    State Class
    """

    def __init__(self, selenium_api:SeleniumAPI, username, password):
        super().__init__(selenium_api, "Login")
        self.username = username
        self.password = password

    def reach_state(self):
        """
        Reach if not reached
        """

        if self.check_state_reached():
            return True

        self.load_login_page()

        # self.selenium_state
        self.selenium_api.fill_input("userId", self.username)
        self.selenium_api.fill_input("password", self.password)
        # login
        btn_container = self.selenium_api.get_element(By.CLASS_NAME, "container-action")
        btn = btn_container.find_element(By.NAME ,"button")
        btn.click()
        # send sms
        for _ in range(60):
            btn_container = self.selenium_api.get_element(By.CLASS_NAME, "container-action")
            if btn_container:
                break
            time.sleep(1)
        btn = btn_container.find_element(By.NAME ,"button")
        if not btn.is_displayed():
            raise self.selenium_api.VisibilityError("Login button not visible")
        btn.click()
        if self.check_state_reached():
            return True

        main_div = self.selenium_api.get_element(By.CLASS_NAME, "container-main")
        main_div_text = main_div.text

        if "Enter verification code" in main_div_text:
            while True:
                input_div = self.selenium_api.get_element(By.CLASS_NAME, "aq-input", is_displayed=True)
                ret = input_div.get_attribute("value")
                if len(ret) == 6:
                    break
                time.sleep(0.5)
            breakpoint()

        if not self.check_state_reached():
            raise ValueError("Was not able to login")
        return True

    def load_login_page(self):
        """
        Load and validate login page
        """
        self.selenium_api.get("https://login.questrade.com/Account/Login")
        main_div = self.selenium_api.get_element(By.CLASS_NAME, "container-main", is_displayed=True)
        main_div_text = main_div.text
        # before full page load:
        # 'Log in to Questrade\nForgot your user ID or password?\nLog In'

        for str_src in ["Log in to Questrade", "Forgot your user ID or password", "Log In"]:
            if str_src in main_div_text:
                break
        else:
            raise NotImplementedError("Retry open login page")

        # After load:
        # 'Log in to Questrade\nUser ID\nPassword\nForgot your user ID or password?\nLog In'
        for _ in range(10):
            main_div = self.selenium_api.get_element(By.CLASS_NAME, "container-main")
            main_div_text = main_div.text
            for str_src in ["User ID", "Password"]:
                if str_src not in main_div_text:
                    time.sleep(1)
                    break
            else:
                return True
        raise TimeoutError("Was not able to load login page")

    def check_state_reached(self):
        """
        Check if the state reached.
        """

        btn_container = self.selenium_api.get_element(By.CLASS_NAME, "profile-button")
        return btn_container is not None and btn_container.is_displayed()

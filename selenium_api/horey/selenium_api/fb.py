from horey.selenium_api.selenium_api import SeleniumAPI


class FB:
    def __init__(self, configuration):
        self.selenium_api = SeleniumAPI()
        self.configuration = configuration

    def load_free(self):
        """
        Load free items.

        :return:
        """

        self.selenium_api.connect(options="--no-sandbox --disable-gpu --disable-dev-shm-usage")

        self.selenium_api.get("https://www.facebook.com/marketplace/winnipeg/free/?exact=false")
        self.selenium_api.wait_for_page_load()
        div_user = self.selenium_api.get_element_by_name("email")
        div_user.send_keys(self.configuration.username)

        div_password = self.selenium_api.get_element_by_name("pass")
        div_password.send_keys(self.configuration.password)

        ret = self.selenium_api.get_element_by_partial_link_text("/marketplace/item/")
        breakpoint()
        login_button_xpath = '//span[text()="Log In"]'
        login_button = self.selenium_api.get_element_by_xpath(login_button_xpath)
        login_button.click()
        print("Clicked the 'Log In' button via XPath text match.")

        breakpoint()
        login_button_xpath = '//span[text()="Log In"]'

        breakpoint()
        btn_login = self.selenium_api.get_element_by_name("login")
        btn_login.click()
        divs = self.selenium_api.get_elements_by_tagname("div")
        divs = [x for x in divs if "Email or phone number" in x.text]
        for x in divs:
            try:
                x.click()
                x.send_keys("A")
            except Exception as inst_err:
                print(f"Error: {repr(inst_err)}")
        breakpoint()
        # page_source = self.selenium_api.driver.page_source

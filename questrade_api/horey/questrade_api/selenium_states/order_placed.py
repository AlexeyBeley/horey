"""
State

"""
from horey.questrade_api.selenium_states.selenium_state import SeleniumState
from horey.selenium_api.selenium_api import SeleniumAPI

class OrderPlaced(SeleniumState):
    def __init__(self, selenium_api:SeleniumAPI, name:str, symbol:str, price:float, parent:SeleniumState=None):
        super().__init__(selenium_api, name, parent=parent)
        self.symbol = symbol
        self.price = price

    def reach_state(self):
        """
        Reach if not reached
        """

        if self.parent:
            self.parent.reach_state()
    
        # todo: remove
        return True
        btn = self.selenium_api.get_shadowed_element_by_css_selector('button[data-qt*="order-entry-next-button"]', is_displayed=True)

        if not btn:
            breakpoint()
        btn.click()
        breakpoint()
        btn = self.selenium_api.get_shadowed_element_by_text("button", "Send order")
        if not btn:
            breakpoint()
        btn.click()

        try:
            header = self.selenium_api.get_shadowed_element_by_css_selector('div[data-qt*="order-review-title"]', is_displayed=True)
        except Exception:
            breakpoint()
        logger.info("todo: Unknown state")

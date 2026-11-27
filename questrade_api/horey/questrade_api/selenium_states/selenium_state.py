"""
Base class

"""
from horey.selenium_api.selenium_api import SeleniumAPI

class SeleniumState:
    def __init__(self, selenium_api:SeleniumAPI, name, parent=None):
        self.selenium_api = selenium_api
        self.name = name
        self.parent = parent

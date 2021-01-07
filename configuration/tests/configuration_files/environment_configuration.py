import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))


from configuration import Configuration


class EnvironmentConfiguration(Configuration):
    def __init__(self):
        super().__init__()
        self._name = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value



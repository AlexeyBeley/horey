import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))

from configuration_policy import Configuration


class JenkinsOpsConfiguration(Configuration):
    def __init__(self):
        super().__init__()
        self._username = None
        self._password = None
        self._port = None
        self._protocol = None

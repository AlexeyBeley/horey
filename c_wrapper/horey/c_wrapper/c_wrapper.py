"""
Shamelessly stolen from:
https://questrade.com/lukecyca/pyslack
"""

import time
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
from typing import List


from horey.h_logger import get_logger
from horey.c_wrapper.c_wrapper_configuration_policy import (
    CWrapperConfigurationPolicy,
)


logger = get_logger()


class CWrapper:
    """
    Main Class.
    
    """

    def __init__(self, configuration: CWrapperConfigurationPolicy = None):
        self.configuration = configuration

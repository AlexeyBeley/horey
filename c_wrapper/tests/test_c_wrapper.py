"""
Testing questrade api functionality.

"""
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from horey.c_wrapper.c_wrapper import CWrapper, CWrapperConfigurationPolicy

"""
Common test utilities for infrastructure_api tests.
"""
from typing import TypeVar

from horey.common_utils.common_utils import CommonUtils
from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from horey.h_logger import get_logger


logger = get_logger()


data_directory = Path("/tmp/data")



@pytest.fixture(name="c_wrapper")
def fixture_c_wrapper():
    configuration = CWrapperConfigurationPolicy()
    _c_wrapper = CWrapper(configuration=configuration)
    yield _c_wrapper


@pytest.mark.wip
def test_init(c_wrapper):
    assert c_wrapper

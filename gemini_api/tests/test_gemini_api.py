"""
Testing github api functionality.

"""
import json
import datetime
import pytest

from horey.aws_api.base_entities.region import Region
from horey.gemini_api.gemini_api import GeminiAPI, GeminiAPIConfigurationPolicy

"""
Common test utilities for infrastructure_api tests.
"""
from pathlib import Path

from horey.common_utils.common_utils import CommonUtils
from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from horey.h_logger import get_logger
from horey.aws_api.aws_api import AWSAPI

logger = get_logger()



@pytest.fixture(name="config")
def fixture_config():
    file_path = Path(__file__).parent.parent.parent.parent / "ignore" / "gemini_api_config.py"
    configuration = GeminiAPIConfigurationPolicy()
    configuration.init_from_file(file_path)
    yield configuration


@pytest.fixture(name="gemini_api")
def fixture_gemini_api(config):
    _gemini_api = GeminiAPI(configuration=config)
    yield _gemini_api


@pytest.mark.unit
def test_init_gemini_api(gemini_api):
    assert isinstance(gemini_api, GeminiAPI)

@pytest.mark.wip
def test_ask_json(gemini_api):
    current_day = datetime.datetime.now().astimezone().isoformat()
    prompt = f"Given date context ({current_day})"
    ret = gemini_api.ask_json(prompt, {"Day": "%A"})
    assert ret == {"Day": datetime.datetime.now().strftime("%A")}
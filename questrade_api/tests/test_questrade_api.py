"""
Testing questrade api functionality.

"""
from pathlib import Path

import pytest

from horey.questrade_api.questrade_api import QuestradeAPI, QuestradeAPIConfigurationPolicy

"""
Common test utilities for infrastructure_api tests.
"""
from typing import TypeVar

from horey.common_utils.common_utils import CommonUtils
from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from horey.h_logger import get_logger

test_mock_values_file_tokenh = Path(__file__).parent.parent.parent.parent / "ignore" / "test_q_api.py"
test_mock_values = CommonUtils.load_module(test_mock_values_file_tokenh)



logger = get_logger()


T = TypeVar('T', bound=ConfigurationPolicy)
data_directory = Path("/tmp/data")


class TestConfigs(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._token = None
        self._account = None
        self._api_server = None

    @property
    def api_server(self):
        return self._api_server

    @api_server.setter
    def api_server(self, value):
        self._api_server = value

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value


@pytest.fixture(name="tests_config")
def fixture_tests_config():
    configuration = TestConfigs()
    configuration.token = test_mock_values.token
    configuration.account = test_mock_values.account
    configuration.api_server = test_mock_values.api_server
    yield configuration


@pytest.fixture(name="questrade_api")
def fixture_questrade_api(tests_config):
    configuration = QuestradeAPIConfigurationPolicy()
    configuration.token = tests_config.token
    configuration.account = tests_config.account
    configuration.api_server = tests_config.api_server

    _questrade_api = QuestradeAPI(configuration=configuration)
    yield _questrade_api


@pytest.mark.wip
def test_connect(questrade_api):
    assert questrade_api.connect()

@pytest.mark.unit
def test_get_accounts(questrade_api):
    questrade_api.connect()
    assert questrade_api.get_accounts()


@pytest.mark.unit
def test_get_positions(questrade_api):
    assert questrade_api.get_positions()

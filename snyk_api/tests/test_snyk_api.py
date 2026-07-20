"""
Testing github api functionality.

"""
import json

import pytest

from horey.aws_api.base_entities.region import Region
from horey.snyk_api.snyk_api import SnykAPI, SnykAPIConfigurationPolicy

"""
Common test utilities for infrastructure_api tests.
"""
from typing import TypeVar
from pathlib import Path
import shutil

from horey.common_utils.common_utils import CommonUtils
from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from horey.h_logger import get_logger
from horey.aws_api.aws_api import AWSAPI

test_mock_values_file_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_snyk_api_mocks.py"
test_mock_values = CommonUtils.load_module(test_mock_values_file_path)



logger = get_logger()


T = TypeVar('T', bound=ConfigurationPolicy)
data_directory_path = Path("/tmp/data")


class TestConfigs(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._api_key = None
        self._org_id = None
    
    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value

    @property
    def org_id(self):
        return self._org_id

    @org_id.setter
    def org_id(self, value):
        self._org_id = value


def init_from_secrets_api(configuration_class: type[T], secret_name: str) -> T:
    """Download secret to temporary file and return file path."""
    aws_api = AWSAPI()
    data_directory_path.mkdir(exist_ok=True, parents=True)
    file_path = aws_api.get_secret_file(secret_name, data_directory_path, region = Region.get_region(test_mock_values.region))

    configuration = configuration_class()
    configuration.configuration_file_full_path = file_path
    configuration.init_from_file()
    if data_directory_path.exists():
        shutil.rmtree(data_directory_path)

    return configuration

@pytest.fixture(name="tests_config")
def fixture_tests_config():
    configuration = init_from_secrets_api(TestConfigs, test_mock_values.secret_name)
    yield configuration


@pytest.fixture(name="snyk_api")
def fixture_snyk_api(tests_config):
    configuration = SnykAPIConfigurationPolicy()
    configuration.api_key = tests_config.api_key
    configuration.org_id = tests_config.org_id

    _snyk_api = SnykAPI(configuration=configuration)
    yield _snyk_api


@pytest.mark.unit
def test_init_snyk_api(snyk_api):
    assert isinstance(snyk_api, SnykAPI)

@pytest.mark.unit
def test_get_projects(snyk_api):
    assert len(snyk_api.get_projects())

@pytest.mark.unit
def test_get_targets(snyk_api):
    assert len(snyk_api.get_targets())

@pytest.mark.unit
def test_get_integrations(snyk_api):
    assert len(snyk_api.get_integrations())
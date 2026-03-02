"""
Testing github api functionality.

"""
import json

import pytest

from horey.aws_api.base_entities.region import Region
from horey.github_api.github_api import GithubAPI, GithubAPIConfigurationPolicy

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

test_mock_values_file_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_github_api_mocks.py"
test_mock_values = CommonUtils.load_module(test_mock_values_file_path)



logger = get_logger()


T = TypeVar('T', bound=ConfigurationPolicy)
data_directory_path = Path("/tmp/data")


class TestConfigs(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._src_repo_name = None
        self._dst_repo_name = None
        self._dst_repo_names = None
        self._pat = None
        self._owner = None

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        self._owner = value

    @property
    def pat(self):
        return self._pat

    @pat.setter
    def pat(self, value):
        self._pat = value

    @property
    def dst_repo_name(self):
        return self._dst_repo_name

    @dst_repo_name.setter
    def dst_repo_name(self, value):
        self._dst_repo_name = value
    
    @property
    def dst_repo_names(self):
        return self._dst_repo_names

    @dst_repo_names.setter
    def dst_repo_names(self, value):
        self._dst_repo_names = value

    @property
    def src_repo_name(self):
        return self._src_repo_name

    @src_repo_name.setter
    def src_repo_name(self, value):
        self._src_repo_name = value


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


@pytest.fixture(name="github_api")
def fixture_github_api(tests_config):
    configuration = GithubAPIConfigurationPolicy()
    configuration.pat = tests_config.pat
    configuration.owner = tests_config.owner

    _github_api = GithubAPI(configuration=configuration)
    yield _github_api


@pytest.mark.unit
def test_init_github_api(github_api):
    assert isinstance(github_api, GithubAPI)


@pytest.mark.unit
def test_init_repositories(github_api):
    assert github_api.init_repositories()

@pytest.mark.unit
def test_create_repository(github_api):
    assert github_api.create_repository("test_repo_name")


@pytest.mark.unit
def test_copy_repository_permissions(github_api, tests_config):
    assert github_api.copy_repository_permissions(tests_config.src_repo_name, tests_config.dst_repo_name)

@pytest.mark.unit
def test_copy_repositories_permissions(github_api, tests_config):
    for dst_repo_name in json.loads(tests_config.dst_repo_names):
        assert github_api.copy_repository_permissions(tests_config.src_repo_name, dst_repo_name)


@pytest.mark.unit
def test_init_self_hosted_runners(github_api, tests_config):
    assert github_api.init_self_hosted_runners()


@pytest.mark.unit
def test_init_github_hosted_runners(github_api, tests_config):
    assert github_api.init_github_hosted_runners()



@pytest.mark.unit
def test_init_repository_self_hosted_runners(github_api, tests_config):
    assert github_api.init_repository_self_hosted_runners(tests_config.src_repo_name)


@pytest.mark.unit
def test_request_runner_registration_token(github_api, tests_config):
    assert github_api.request_runner_registration_token("test")

@pytest.mark.wip
def test_request_repository_runner_registration_token(github_api, tests_config):
    assert github_api.request_repository_runner_registration_token(tests_config.src_repo_name)




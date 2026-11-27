"""
Testing github ui functionality.

"""
import json
from pathlib import Path
import shutil
from typing import TypeVar

import pytest

from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.base_entities.region import Region
from horey.common_utils.common_utils import CommonUtils
from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from horey.github_api.github_api import GithubAPI, GithubAPIConfigurationPolicy
from horey.github_ui.github_ui import GithubUI
from horey.github_ui.github_ui_configuration_policy import GithubUIConfigurationPolicy
from horey.h_logger import get_logger
from horey.postgres_api.postgres_api import PostgresAPI

# Same secrets/mocks as the github_api tests.
test_mock_values_file_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_github_api_mocks.py"
test_mock_values = CommonUtils.load_module(test_mock_values_file_path)

logger = get_logger()

T = TypeVar('T', bound=ConfigurationPolicy)
data_directory_path = Path("/tmp/data")


class TstConfigs(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._src_repo_name = None
        self._dst_repo_name = None
        self._dst_repo_names = None
        self._pat = None
        self._owner = None
        self._action_name = None
        self._all_repos_url = None
        self._input_extract_job_name = None
        self._input_extract_job_step_name = None

    @property
    def input_extract_job_step_name(self):
        return self._input_extract_job_step_name

    @input_extract_job_step_name.setter
    def input_extract_job_step_name(self, value):
        self._input_extract_job_step_name = value

    @property
    def input_extract_job_name(self):
        return self._input_extract_job_name

    @input_extract_job_name.setter
    def input_extract_job_name(self, value):
        self._input_extract_job_name = value

    @property
    def all_repos_url(self):
        return self._all_repos_url

    @all_repos_url.setter
    def all_repos_url(self, value):
        self._all_repos_url = value

    @property
    def action_name(self):
        return self._action_name

    @action_name.setter
    def action_name(self, value):
        self._action_name = value

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
    configuration = init_from_secrets_api(TstConfigs, test_mock_values.secret_name)
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


@pytest.fixture(name="github_api_configuration_file_path")
def fixture_github_api_configuration_file_path(tests_config, tmp_path):
    """
    Credentials come from the same AWS secret as in test_github_api.py,
    written as a GithubAPIConfigurationPolicy file (pat, owner).
    """

    file_path = tmp_path / "github_api_configuration.json"
    file_path.write_text(json.dumps({"pat": tests_config.pat, "owner": tests_config.owner}), encoding="utf-8")
    yield file_path


@pytest.fixture(name="github_ui")
def fixture_github_ui(github_api_configuration_file_path):
    configuration = GithubUIConfigurationPolicy()
    configuration.github_api_configuration_file_path = github_api_configuration_file_path
    yield GithubUI(configuration)


@pytest.mark.unit
def test_github_ui_configuration_policy(github_api_configuration_file_path):
    configuration = GithubUIConfigurationPolicy()
    assert configuration.github_api_configuration_file_path is None
    configuration.github_api_configuration_file_path = github_api_configuration_file_path
    assert configuration.github_api_configuration_file_path == github_api_configuration_file_path


@pytest.mark.unit
def test_init_github_ui(github_ui):
    assert isinstance(github_ui, GithubUI)


@pytest.mark.unit
def test_github_ui_github_api(github_ui, tests_config):
    assert isinstance(github_ui.github_api, GithubAPI)
    assert github_ui.github_api.configuration.owner == tests_config.owner
    assert github_ui.github_api.configuration.pat == tests_config.pat


@pytest.mark.unit
def test_fetch_repositories(github_ui):
    repositories = github_ui.fetch_repositories()
    assert repositories
    assert all(isinstance(name, str) for name in repositories)


@pytest.mark.unit
def test_github_ui_configuration_init_from_file(github_api_configuration_file_path, tmp_path):
    ui_configuration_file_path = tmp_path / "github_ui_configuration.json"
    ui_configuration_file_path.write_text(
        json.dumps({"github_api_configuration_file_path": str(github_api_configuration_file_path)}), encoding="utf-8")

    configuration = GithubUIConfigurationPolicy()
    configuration.configuration_file_full_path = ui_configuration_file_path
    configuration.init_from_file()
    assert Path(configuration.github_api_configuration_file_path) == github_api_configuration_file_path
    assert isinstance(GithubUI(configuration).github_api, GithubAPI)


@pytest.fixture(name="postgres_api_configuration_file_path")
def fixture_postgres_api_configuration_file_path(tmp_path):
    """
    Dummy values: PostgresAPI connects lazily, nothing is opened in these tests.
    """

    file_path = tmp_path / "postgres_api_configuration.json"
    file_path.write_text(json.dumps({"host": "postgres.example.com", "port": 5433, "database": "horey",
                                     "username": "horey_user", "password": "p@ss/word"}), encoding="utf-8")
    yield file_path


@pytest.mark.unit
def test_github_ui_postgres_api(postgres_api_configuration_file_path):
    configuration = GithubUIConfigurationPolicy()
    configuration.postgres_api_configuration_file_path = postgres_api_configuration_file_path
    postgres_api = GithubUI(configuration).postgres_api
    assert isinstance(postgres_api, PostgresAPI)
    assert postgres_api.url.host == "postgres.example.com"
    assert postgres_api.url.port == 5433
    assert postgres_api.url.database == "horey"
    assert postgres_api.url.username == "horey_user"
    assert postgres_api.url.password == "p@ss/word"


@pytest.mark.unit
def test_github_ui_postgres_api_not_configured():
    with pytest.raises(ValueError, match="postgres_api_configuration_file_path was not set"):
        _ = GithubUI(GithubUIConfigurationPolicy()).postgres_api


@pytest.mark.unit
def test_github_ui_configuration_init_postgres_from_file(github_api_configuration_file_path,
                                                         postgres_api_configuration_file_path, tmp_path):
    ui_configuration_file_path = tmp_path / "github_ui_configuration.json"
    ui_configuration_file_path.write_text(json.dumps({
        "github_api_configuration_file_path": str(github_api_configuration_file_path),
        "postgres_api_configuration_file_path": str(postgres_api_configuration_file_path)}), encoding="utf-8")

    configuration = GithubUIConfigurationPolicy()
    configuration.configuration_file_full_path = ui_configuration_file_path
    configuration.init_from_file()
    github_ui = GithubUI(configuration)
    assert isinstance(github_ui.github_api, GithubAPI)
    assert isinstance(github_ui.postgres_api, PostgresAPI)

"""
Pip API tests

"""

import shutil
from pathlib import Path

import pytest
from horey.git_api.git_api import GitAPI
from horey.git_api.git_api_configuration_policy import GitAPIConfigurationPolicy


# pylint: disable=missing-function-docstring, unused-argument

horey_root_path = Path(__file__).parent.parent.parent.absolute()
config_file_name_test = "git_api_configuration.py"
config_file_name_horey = "h_git_api_configuration.py"
config_file_name_test_ref = "git_api_configuration_ref.py"


@pytest.fixture(name="git_api")
def git_api_fixtures(config_file_name):
    configuration = GitAPIConfigurationPolicy()
    configuration.configuration_file_full_path = horey_root_path.parent / "ignore" / "git_api" / config_file_name
    configuration.init_from_file()
    git_api = GitAPI(configuration)
    git_api.configuration.git_directory_path = "/tmp/git_api_tests"
    yield git_api
    if Path(git_api.configuration.git_directory_path).exists():
        shutil.rmtree(git_api.configuration.git_directory_path)


@pytest.mark.unit
def test_init():
    git_api = GitAPI(None)
    assert isinstance(git_api, GitAPI)


@pytest.mark.unit
@pytest.mark.parametrize("config_file_name", [config_file_name_horey, config_file_name_test])
def test_clone(git_api, config_file_name):
    assert git_api.clone()
    assert git_api.configuration.git_directory_path.exists()


@pytest.mark.unit
@pytest.mark.parametrize("config_file_name", [config_file_name_horey, config_file_name_test])
def test_checkout_remote(git_api, config_file_name):
    git_api.checkout_remote(git_api.configuration.main_branch)


@pytest.mark.unit
@pytest.mark.parametrize("config_file_name", [config_file_name_horey, config_file_name_test])
def test_checkout_remote_to_existing_branch(git_api, config_file_name):
    git_api.checkout_remote(git_api.configuration.main_branch)
    git_api.checkout_remote(git_api.configuration.main_branch)


@pytest.mark.unit
@pytest.mark.parametrize("config_file_name", [config_file_name_test_ref])
def test_checkout_remote_ref_pull_request(git_api, config_file_name):
    ref = ""
    git_api.checkout_remote(ref)


@pytest.mark.unit
@pytest.mark.parametrize("config_file_name", [config_file_name_test_ref])
def test_checkout_remote_ref_pull_request_to_existing(git_api, config_file_name):
    ref = ""
    git_api.checkout_remote(ref)
    git_api.checkout_remote(ref)

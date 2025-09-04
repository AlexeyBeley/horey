"""
Pip API tests

"""
import os
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
    before = os.getcwd()
    configuration = GitAPIConfigurationPolicy()
    configuration.configuration_file_full_path = horey_root_path.parent / "ignore" / "git_api" / config_file_name_horey
    configuration.init_from_file()
    git_api = GitAPI(configuration)
    assert isinstance(git_api, GitAPI)
    assert before == os.getcwd()


@pytest.mark.unit
@pytest.mark.parametrize("config_file_name", [config_file_name_horey, config_file_name_test])
def test_clone(git_api, config_file_name):
    before = os.getcwd()
    assert git_api.clone()
    assert git_api.configuration.git_directory_path.exists()
    assert before == os.getcwd()


@pytest.mark.unit
@pytest.mark.parametrize("config_file_name", [config_file_name_horey, config_file_name_test])
def test_checkout_remote(git_api, config_file_name):
    before = os.getcwd()
    git_api.checkout_remote(git_api.configuration.main_branch)
    assert before == os.getcwd()


@pytest.mark.unit
@pytest.mark.parametrize("config_file_name", [config_file_name_horey, config_file_name_test])
def test_checkout_remote_to_existing_branch(git_api, config_file_name):
    before = os.getcwd()
    git_api.checkout_remote(git_api.configuration.main_branch)
    git_api.checkout_remote(git_api.configuration.main_branch)
    assert before == os.getcwd()


@pytest.mark.unit
@pytest.mark.parametrize("config_file_name", [config_file_name_test_ref])
def test_checkout_remote_ref_pull_request(git_api, config_file_name):
    ref = "refs/pull/11111/merge"
    before = os.getcwd()
    git_api.checkout_remote(ref)
    assert before == os.getcwd()


@pytest.mark.unit
@pytest.mark.parametrize("config_file_name", [config_file_name_test_ref])
def test_checkout_remote_ref_pull_request_to_existing(git_api, config_file_name):
    ref = "refs/pull/11111/merge"
    before = os.getcwd()
    git_api.checkout_remote(ref)
    git_api.checkout_remote(ref)
    assert before == os.getcwd()


@pytest.mark.unit
@pytest.mark.parametrize("config_file_name", [config_file_name_horey, config_file_name_test])
def test_get_commit_id_branch(git_api, config_file_name):
    before = os.getcwd()
    git_api.checkout_remote(git_api.configuration.main_branch)
    assert git_api.get_commit_id()
    assert before == os.getcwd()


@pytest.mark.unit
@pytest.mark.parametrize("config_file_name", [config_file_name_test_ref])
def test_get_commit_id_ref(git_api, config_file_name):
    ref = "refs/pull/11111/merge"
    before = os.getcwd()
    git_api.checkout_remote(ref)
    assert git_api.get_commit_id()
    assert before == os.getcwd()
    
    
@pytest.mark.unit
def test_property_directory_path_with_dot_git():
    policy = GitAPIConfigurationPolicy()
    policy.remote = "something/git_path.git"
    policy.git_directory_path = "/tmp"
    assert policy.directory_path == Path("/tmp/git_path")


@pytest.mark.unit
def test_property_directory_path_without_dot_git():
    policy = GitAPIConfigurationPolicy()
    policy.remote = "something/git_path"
    policy.git_directory_path = "/tmp"
    assert policy.directory_path == Path("/tmp/git_path")

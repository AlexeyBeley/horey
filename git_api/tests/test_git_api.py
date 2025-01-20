"""
Pip API tests

"""

import os
import shutil
from pathlib import Path

import pytest
from horey.git_api.git_api import GitAPI
from horey.git_api.git_api_configuration_policy import GitAPIConfigurationPolicy


# pylint: disable=missing-function-docstring

horey_root_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

config_file_name = "git_api_configuration.py"
config_file_name = "h_git_api_configuration.py"
git_api_configuration_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(horey_root_path),
        "ignore",
        "git_api",
        config_file_name
    )
)


@pytest.mark.unit
def test_init():
    git_api = GitAPI(None)
    assert isinstance(git_api, GitAPI)


@pytest.mark.unit
def test_clone():
    configuration = GitAPIConfigurationPolicy()
    configuration.remote = "git@github.com:AlexeyBeley/horey.git"
    configuration.directory_path = Path(__file__).resolve().parent / "git" / "horey"
    configuration.ssh_key_file_path = "~/.ssh/key"

    git_api = GitAPI(configuration)
    assert git_api.clone()
    assert configuration.directory_path.exists()
    shutil.rmtree(configuration.directory_path)


@pytest.mark.wip
def test_checkout_remote_branch():
    branch_name = "main"
    branch_name = "alert_api"
    configuration = GitAPIConfigurationPolicy()
    configuration.configuration_file_full_path = git_api_configuration_file_path
    configuration.init_from_file()
    git_api = GitAPI(configuration)
    git_api.checkout_remote_branch(configuration.remote, branch_name)

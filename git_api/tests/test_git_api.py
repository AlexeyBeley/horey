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

git_api_configuration_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "git_api_configs",
        "git_api_configuration_main.py",
    )
)


@pytest.mark.wip
def test_init():
    git_api = GitAPI(None)
    assert isinstance(git_api, GitAPI)


@pytest.mark.wip
def test_clone():
    configuration = GitAPIConfigurationPolicy()
    configuration.remote = "git@github.com:AlexeyBeley/horey.git"
    configuration.directory_path = Path(__file__).resolve().parent / "git" / "horey"
    configuration.ssh_key_file_path = "~/.ssh/github_key"

    git_api = GitAPI(configuration)
    assert git_api.clone()
    assert configuration.directory_path.exists()
    shutil.rmtree(configuration.directory_path)

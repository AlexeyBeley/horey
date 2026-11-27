"""
Pip API tests

"""

import os
import shutil
from pathlib import Path

import pytest
from horey.health_api.health_api import HealthAPI
from horey.health_api.health_api_configuration_policy import HealthAPIConfigurationPolicy


# pylint: disable=missing-function-docstring

horey_root_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

health_api_configuration_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "health_api_configs",
        "health_api_configuration_main.py",
    )
)


@pytest.mark.wip
def test_init():
    health_api = HealthAPI(None)
    assert isinstance(health_api, HealthAPI)


@pytest.mark.wip
def test_clone():
    configuration = HealthAPIConfigurationPolicy()
    configuration.remote = "git@github.com:AlexeyBeley/horey.git"
    configuration.directory_path = Path(__file__).resolve().parent / "git" / "horey"
    configuration.ssh_key_file_path = "~/.ssh/github_key"

    health_api = HealthAPI(configuration)
    assert health_api.clone()
    assert configuration.directory_path.exists()
    shutil.rmtree(configuration.directory_path)

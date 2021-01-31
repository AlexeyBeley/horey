import os
import sys
from unittest import mock
import argparse
import json


sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "configuration_policies"))

from environment_configuration_policy import EnvironmentConfigurationPolicy


def test_init():
    assert isinstance(EnvironmentConfigurationPolicy(), EnvironmentConfigurationPolicy)


#@pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_command_line():
    description = "Working environment configuration_policy"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--name", required=True, type=str, help="Environment name")

    testargs = ["prog", "--name", "Production"]
    with mock.patch("sys.argv", testargs):
        config = EnvironmentConfigurationPolicy()
        config.init_from_command_line(parser)


#@pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_dictionary():
    config = EnvironmentConfigurationPolicy()
    config.init_from_dictionary({"name": "Production"})


# @pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_json_file():
    file_path = "configuration_values/environment_configuration_values.json"

    config_values = {
        "configuration_file_full_path": file_path}

    config = EnvironmentConfigurationPolicy()
    config.init_from_dictionary(config_values)
    config.init_from_json_file()


def test_init_from_environ():
    raise NotImplemented()
    os.environ[f"{EnvironmentConfigurationPolicy.ENVIRON_ATTRIBUTE_PREFIX.upper()}NAME"] = "Production"
    config = EnvironmentConfigurationPolicy()
    config.init_from_environ()


test_init_from_json_file()

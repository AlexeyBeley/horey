import os
import sys
from unittest import mock
import argparse
import json
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "configuration_files"))

from environment_configuration import EnvironmentConfiguration


def test_init():
    assert isinstance(EnvironmentConfiguration(), EnvironmentConfiguration)


#@pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_command_line():
    description = "Working environment configuration"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--name", required=True, type=str, help="Environment name")

    testargs = ["prog", "--name", "Production"]
    with mock.patch("sys.argv", testargs):
        config = EnvironmentConfiguration()
        config.init_from_command_line(parser)


#@pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_dictionary():
    config = EnvironmentConfiguration()
    config.init_from_dictionary({"name": "Production"})


def test_init_from_json_file():
    file_name = "./tmp.json"
    with open(file_name, "w+") as file_handler:
        json.dump({"name": "Production"}, file_handler)

    config = EnvironmentConfiguration()
    config.init_from_json_file(file_name)


def test_init_from_yaml_file():
    file_name = "./tmp.yaml"
    with open(file_name, "w+") as file_handler:
        yaml.dump({"name": "Production"}, file_handler)

    config = EnvironmentConfiguration()
    config.init_from_yaml_file(file_name)


def test_init_from_environ():
    os.environ[f"{EnvironmentConfiguration.ENVIRON_ATTRIBUTE_PREFIX.upper()}NAME"] = "Production"
    config = EnvironmentConfiguration()
    config.init_from_environ()


test_init_from_environ()
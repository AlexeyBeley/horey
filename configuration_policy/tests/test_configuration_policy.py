import os
import sys
from unittest import mock
import argparse


sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "horey", "configuration_policy"))


from configuration_policy import ConfigurationPolicy


def test_init():
    assert isinstance(ConfigurationPolicy(), Configuration)


# @pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_dictionary():
    configuration_values = {"configuration_file_full_path": "/fun_horey/configuration_policy.py"}
    os_path_exists_mock = mock.Mock()
    os_path_exists_mock.return_value = True

    with mock.patch("os.path.exists", os_path_exists_mock):
        config = ConfigurationPolicy()
        config.init_from_dictionary(configuration_values)


# @pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_command_line():
    testargs = ["prog", "--configuration_file_full_path", "/fun_horey/configuration_policy.py"]

    parser = argparse.ArgumentParser()
    parser.add_argument("--configuration_file_full_path", required=True, type=str)
    os_path_exists_mock = mock.Mock()
    os_path_exists_mock.return_value = True

    with mock.patch("sys.argv", testargs):
        with mock.patch("os.path.exists", os_path_exists_mock):
            config = ConfigurationPolicy()
            config.init_from_command_line(parser)


# @pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_environ():
    testargs = {f"{ConfigurationPolicy.ENVIRON_ATTRIBUTE_PREFIX.upper()}CONFIGURATION_FILE_FULL_PATH": "/fun_horey/configuration_policy.py"}

    os_path_exists_mock = mock.Mock()
    os_path_exists_mock.return_value = True

    with mock.patch("os.environ", testargs):
        with mock.patch("os.path.exists", os_path_exists_mock):
            config = ConfigurationPolicy()
            config.init_from_environ()


class ConfigurationSon(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._component1 = None

    @property
    def component1(self):
        return self._component1

    @component1.setter
    def component1(self, value):
        self._component1 = value


# @pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_python_file():
    config_values = {
        "configuration_file_full_path": "./configuration_policies/base_configuration_values.py"}

    config = ConfigurationSon()
    config.init_from_dictionary(config_values)
    config.init_from_python_file()


# @pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_json_file():
    config_values = {
        "configuration_file_full_path": "./configuration_policies/base_configuration_values.json"}

    config = ConfigurationSon()
    config.init_from_dictionary(config_values)
    config.init_from_json_file()


test_init_from_json_file()

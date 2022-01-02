import os
import sys
from unittest import mock
import argparse


from horey.configuration_policy.configuration_policy import ConfigurationPolicy

configuration_values_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "configuration_values")


def test_init():
    assert isinstance(ConfigurationPolicy(), ConfigurationPolicy)


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
        self._component2 = None

    @property
    def component1(self):
        return self._component1

    @component1.setter
    def component1(self, value):
        self._component1 = value

    @property
    @ConfigurationPolicy.validate_value_is_not_none_decorator
    def component2(self):
        return self._component2

    @component2.setter
    def component2(self, value):
        self._component2 = value


# @pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_python_file():
    config_values = {
        "configuration_file_full_path": os.path.join(configuration_values_dir, "base_configuration_values.py")}

    config = ConfigurationSon()
    config.init_from_dictionary(config_values)
    config.init_from_python_file()


# @pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_json_file():
    config_values = {
        "configuration_file_full_path": os.path.join(configuration_values_dir, "base_configuration_values.json")}

    config = ConfigurationSon()
    config.init_from_dictionary(config_values)
    config.init_from_json_file()


def test_property_value_not_set_exception():
    son = ConfigurationSon()
    son.component2 = "1"
    print(son.component2)

if __name__ == "__main__":
    test_property_value_not_set_exception()
"""
Pip API tests

"""

import os
from horey.common_utils.common_utils import CommonUtils
from horey.pip_api.pip_api import PipAPI
from horey.pip_api.pip_api_configuration_policy import PipAPIConfigurationPolicy


mock_values_file_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore", "mock_values.py"))
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

# pylint: disable=missing-function-docstring


def test_init():
    pip_api = PipAPI()
    assert isinstance(pip_api, PipAPI)


def test_init_packages():
    pip_api = PipAPI()
    pip_api.init_packages()
    assert isinstance(pip_api.packages, list)


def test_install_requirements():
    pip_api_configuration_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pip_api_configuration.py")
    requirements_file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "test_requirements.txt"))
    configuration = PipAPIConfigurationPolicy()
    configuration.configuration_file_full_path = pip_api_configuration_file_path
    configuration.init_from_file()
    pip_api = PipAPI(configuration=configuration)
    pip_api.install_requirements(requirements_file_path)
    assert isinstance(pip_api.packages, list)


def test_install_requirements_real_data():

    pip_api_configuration_file_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore", "pip_api_configuration.py"))

    requirements_file_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore", "test_requirements.txt"))

    configuration = PipAPIConfigurationPolicy()
    configuration.configuration_file_full_path = pip_api_configuration_file_path
    configuration.init_from_file()
    pip_api = PipAPI(configuration=configuration)
    pip_api.install_requirements(requirements_file_path)
    assert isinstance(pip_api.packages, list)


if __name__ == "__main__":
    test_init()
    test_init_packages()
    test_install_requirements()
    test_install_requirements_real_data()

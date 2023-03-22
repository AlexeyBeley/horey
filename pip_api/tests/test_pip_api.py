"""
Pip API tests

"""

import os
from horey.common_utils.common_utils import CommonUtils
from horey.pip_api.pip_api import PipAPI, Requirement
from horey.pip_api.pip_api_configuration_policy import PipAPIConfigurationPolicy


mock_values_file_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore", "mock_values.py")
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

# pylint: disable=missing-function-docstring


def test_init():
    pip_api = PipAPI()
    assert isinstance(pip_api, PipAPI)


def test_init_configuration():
    pip_api_configuration_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "pip_api_configuration.py"
    )
    configuration = PipAPIConfigurationPolicy()
    configuration.configuration_file_full_path = pip_api_configuration_file_path
    configuration.init_from_file()
    PipAPI(configuration=configuration)


def test_init_packages():
    pip_api = PipAPI()
    pip_api.init_packages()
    assert isinstance(pip_api.packages, list)


def test_install_requirements():
    pip_api_configuration_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "pip_api_configuration.py"
    )
    requirements_file_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "test_requirements.txt"
        )
    )
    configuration = PipAPIConfigurationPolicy()
    configuration.configuration_file_full_path = pip_api_configuration_file_path
    configuration.init_from_file()
    pip_api = PipAPI(configuration=configuration)
    pip_api.install_requirements(requirements_file_path)
    assert isinstance(pip_api.packages, list)


def test_install_requirements_real_data():

    pip_api_configuration_file_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "ignore",
            "pip_api_configuration.py",
        )
    )

    requirements_file_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "ignore",
            "test_requirements.txt",
        )
    )

    configuration = PipAPIConfigurationPolicy()
    configuration.configuration_file_full_path = pip_api_configuration_file_path
    configuration.init_from_file()
    pip_api = PipAPI(configuration=configuration)
    pip_api.install_requirements(requirements_file_path)
    assert isinstance(pip_api.packages, list)


def test_update_existing_requirement_no_max():
    pip_api = PipAPI()
    requirement_this = Requirement("some/path", "requests>=2.28.1")
    pip_api.REQUIREMENTS = {"requests": requirement_this}
    requirement_other = Requirement("some/path", "requests>=2.28.2")
    pip_api.update_existing_requirement(requirement_other)
    assert pip_api.REQUIREMENTS["requests"].min_version == "2.28.2"
    assert pip_api.REQUIREMENTS["requests"].max_version is None
    assert pip_api.REQUIREMENTS["requests"].include_min
    assert pip_api.REQUIREMENTS["requests"].include_max is None


def test_update_existing_requirement_with_max():
    pip_api = PipAPI()
    requirement_this = Requirement("some/path", "requests>=2.28.1")
    requirement_this.max_version = "2.29.1"
    requirement_this.include_max = True
    pip_api.REQUIREMENTS = {"requests": requirement_this}
    requirement_other = Requirement("some/path", "requests>=2.28.2")
    requirement_other.max_version = "2.29.1"
    requirement_other.include_max = False
    pip_api.update_existing_requirement(requirement_other)
    assert pip_api.REQUIREMENTS["requests"].min_version == "2.28.2"
    assert pip_api.REQUIREMENTS["requests"].max_version == "2.29.1"
    assert pip_api.REQUIREMENTS["requests"].include_min
    assert not pip_api.REQUIREMENTS["requests"].include_max


def test_update_existing_requirement_single_version():
    pip_api = PipAPI()
    requirement_this = Requirement("some/path", "requests>=2.28.1")
    requirement_this.max_version = "2.29.1"
    requirement_this.include_max = True
    pip_api.REQUIREMENTS = {"requests": requirement_this}
    requirement_other = Requirement("some/path", "requests>=2.29.1")
    pip_api.update_existing_requirement(requirement_other)
    assert pip_api.REQUIREMENTS["requests"].min_version == "2.29.1"
    assert pip_api.REQUIREMENTS["requests"].max_version == "2.29.1"
    assert pip_api.REQUIREMENTS["requests"].include_min
    assert pip_api.REQUIREMENTS["requests"].include_max


def test_update_existing_requirement_exception_1():
    pip_api = PipAPI()
    requirement_this = Requirement("some/path", "requests>=2.28.1")
    requirement_this.max_version = "2.29.1"
    requirement_this.include_max = True
    pip_api.REQUIREMENTS = {"requests": requirement_this}

    requirement_other = Requirement("some/path", "requests>2.29.1")
    pip_api.update_existing_requirement(requirement_other)
    assert pip_api.REQUIREMENTS["requests"].min_version == "2.29.1"
    assert pip_api.REQUIREMENTS["requests"].max_version == "2.29.1"
    assert pip_api.REQUIREMENTS["requests"].include_min
    assert pip_api.REQUIREMENTS["requests"].include_max


if __name__ == "__main__":
    #test_init()
    test_init_configuration()
    test_init_packages()
    #test_install_requirements()
    #test_install_requirements_real_data()
    test_update_existing_requirement_no_max()
    test_update_existing_requirement_with_max()
    test_update_existing_requirement_single_version()
    test_update_existing_requirement_exception_1()

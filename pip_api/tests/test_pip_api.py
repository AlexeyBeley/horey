"""
Pip API tests

"""

import os
import pytest
from horey.pip_api.pip_api import PipAPI, Requirement
from horey.pip_api.pip_api_configuration_policy import PipAPIConfigurationPolicy


# pylint: disable=missing-function-docstring

horey_root_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

pip_api_configuration_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "pip_api_configs",
        "pip_api_configuration_main.py",
    )
)


@pytest.mark.todo
def test_init():
    pip_api = PipAPI()
    assert isinstance(pip_api, PipAPI)


@pytest.mark.todo
def test_init_configuration():
    configuration = PipAPIConfigurationPolicy()
    configuration.configuration_file_full_path = pip_api_configuration_file_path
    configuration.init_from_file()
    PipAPI(configuration=configuration)


@pytest.mark.todo
def test_init_packages():
    pip_api = PipAPI()
    pip_api.init_packages()
    assert isinstance(pip_api.packages, list)


@pytest.mark.todo
def test_install_requirements():
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


@pytest.mark.todo
def test_install_requirements_real_data():
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


@pytest.mark.todo
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


@pytest.mark.todo
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


@pytest.mark.todo
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


@pytest.mark.todo
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


@pytest.mark.todo
def test_create_wheel():
    pip_api = PipAPI()
    setup_dir_path = os.path.join(horey_root_path, "pip_api")
    build_dir_path = os.path.join(horey_root_path, "build", "_build", "pip_api")
    pip_api.create_wheel(setup_dir_path, build_dir_path)


@pytest.mark.todo
def test_create_wheel_from_branch():
    configuration = PipAPIConfigurationPolicy()
    configuration.configuration_file_full_path = pip_api_configuration_file_path
    configuration.init_from_file()
    pip_api = PipAPI(configuration=configuration)
    setup_dir_path = os.path.join(horey_root_path, "pip_api")
    build_dir_path = os.path.join(horey_root_path, "build", "_build", "pip_api")
    pip_api.create_wheel(setup_dir_path, build_dir_path, branch_name="pip_api_enhance")


@pytest.mark.done
def test_provision_constructor_logic():
    configuration = PipAPIConfigurationPolicy()
    configuration.configuration_file_full_path = pip_api_configuration_file_path
    configuration.init_from_file()
    pip_api = PipAPI(configuration=configuration)
    pip_api.install_requirement_from_string(None, "horey.alert_system>=1.0.0")

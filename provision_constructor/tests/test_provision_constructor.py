"""
Provision constructor tests.
"""

import os

import pytest

from horey.provision_constructor.provision_constructor import ProvisionConstructor

# pylint: disable = missing-function-docstring
DEPLOYMENT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "provision_constructor_deployment"
)


@pytest.mark.wip
def test_init():
    provision_constructor = ProvisionConstructor()
    assert isinstance(provision_constructor, ProvisionConstructor)


@pytest.mark.wip
def test_provision_system_function_horey_package_generic_venv():
    """
    python -m venv ./test_venv

    @return:
    """

    provision_constructor = ProvisionConstructor()
    this_dir = os.path.dirname(os.path.abspath(__file__))
    provision_constructor.provision_system_function(
        "horey_package_generic",
        package_name="jenkins_manager",
        horey_repo_path=os.path.join(this_dir, "..", ".."),
        venv_path=os.path.join(this_dir, "test_venv"),
    )


@pytest.mark.wip
def test_provision_system_function_pip_api_package_venv():
    """
    python -m venv ./test_venv

    @return:
    """

    provision_constructor = ProvisionConstructor()
    this_dir = os.path.dirname(os.path.abspath(__file__))
    provision_constructor.provision_system_function(
        "pip_api_package",
        requirements_file_path=os.path.join(
            this_dir, "pip_api_tests_data", "requirements.txt"
        ),
        pip_api_configuration_file=os.path.join(
            this_dir, "pip_api_tests_data", "pip_api_configuration.py"
        ),
    )


@pytest.mark.ubuntu
def test_provision_system_function_logstash():
    provision_constructor = ProvisionConstructor()
    provision_constructor.provision_system_function("logstash", force=True, upgrade=True)


@pytest.mark.ubuntu
def test_provision_system_function_swap():
    provision_constructor = ProvisionConstructor()
    provision_constructor.provision_system_function("swap", force=False, upgrade=True, swap_size_in_gb=3)

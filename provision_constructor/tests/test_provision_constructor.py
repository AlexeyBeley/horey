"""
Provision constructor tests.
"""

import os
from horey.provision_constructor.provision_constructor import ProvisionConstructor

# pylint: disable = missing-function-docstring
DEPLOYMENT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "provision_constructor_deployment"
)


def test_init():
    provision_constructor = ProvisionConstructor()
    assert isinstance(provision_constructor, ProvisionConstructor)


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


def test_provision_system_function_logstash():
    provision_constructor = ProvisionConstructor()
    provision_constructor.provision_system_function("logstash", force=True, upgrade=True)


def test_provision_system_function_swap():
    provision_constructor = ProvisionConstructor()
    provision_constructor.provision_system_function("swap", force=False, upgrade=True, swap_size_in_gb=3)


if __name__ == "__main__":
    # test_init()
    # test_provision_system_function_horey_package_generic_venv()
    # test_provision_system_function_pip_api_package_venv()
    # test_provision_system_function_logstash()
    test_provision_system_function_swap()

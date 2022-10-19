"""
Test system_function_common module
"""

import os
from horey.provision_constructor.system_functions.system_function_common import SystemFunctionCommon

# pylint: disable = missing-function-docstring
DEPLOYMENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "provision_constructor_deployment")


def test_init():
    provision_constructor = SystemFunctionCommon(DEPLOYMENT_DIR)
    assert isinstance(provision_constructor, SystemFunctionCommon)


def test_init_pip_packages():
    system_function_common = SystemFunctionCommon(DEPLOYMENT_DIR)
    system_function_common.init_pip_packages()
    assert isinstance(system_function_common, SystemFunctionCommon)


def test_init_pip_packages_venv():
    system_function_common = SystemFunctionCommon(DEPLOYMENT_DIR)
    system_function_common.venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "build",
                                                    "_build", "_venv")
    system_function_common.init_pip_packages()
    assert isinstance(system_function_common, SystemFunctionCommon)


if __name__ == "__main__":
    #test_init()
    #test_init_pip_packages()
    test_init_pip_packages_venv()

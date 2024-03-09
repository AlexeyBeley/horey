"""
Static method tests

"""

import os
import shutil
import sys
import pytest

this_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(this_dir), "horey", "pip_api")))
import pip_api_make

# pylint: disable= missing-function-docstring

@pytest.fixture(name="tmp_dir_path")
def tmp_dir_path_fixture():
    tmp_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "tmp"))
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)
    yield tmp_dir
    shutil.rmtree(tmp_dir)


@pytest.mark.done
def test_init_configuration_main():
    pip_api_configuration_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "pip_api_configs", "pip_api_configuration_main.py"))
    sys.argv = ['pip_api_make.py', '--pip_api_configuration', pip_api_configuration_file_path]
    configs = pip_api_make.init_configuration()
    assert configs["multi_package_repositories"] == [os.path.abspath(os.path.dirname(os.path.dirname(this_dir)))]
    assert configs["venv_dir_path"] == os.path.abspath(os.path.join(this_dir, "venv"))


@pytest.mark.done
def test_init_configuration_main_1():
    pip_api_configuration_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "pip_api_configs", "pip_api_configuration_main_1.py"))
    sys.argv = ['pip_api_make.py', '--pip_api_configuration', pip_api_configuration_file_path]
    configs = pip_api_make.init_configuration()
    assert configs["multi_package_repositories"] == [os.path.abspath(os.path.dirname(os.path.dirname(this_dir)))]
    assert configs["venv_dir_path"] is None


@pytest.mark.done
def test_init_configuration_main_2():
    pip_api_configuration_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "pip_api_configs", "pip_api_configuration_main_2.py"))
    sys.argv = ['pip_api_make.py', '--pip_api_configuration', pip_api_configuration_file_path]
    configs = pip_api_make.init_configuration()
    assert configs["multi_package_repositories"] is None
    assert configs["venv_dir_path"] == os.path.abspath(os.path.join(this_dir, "venv"))


@pytest.mark.done
def test_init_configuration_no_main():
    pip_api_configuration_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "pip_api_configs", "pip_api_configuration_no_main.py"))
    sys.argv = ['pip_api_make.py', '--pip_api_configuration', pip_api_configuration_file_path]
    configs = pip_api_make.init_configuration()
    assert configs["multi_package_repositories"] == [os.path.abspath(os.path.dirname(os.path.dirname(this_dir)))]
    assert configs["venv_dir_path"] == os.path.abspath(os.path.join(this_dir, "venv"))


@pytest.mark.done
def test_init_configuration_no_main_1():
    pip_api_configuration_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "pip_api_configs", "pip_api_configuration_no_main_1.py"))
    sys.argv = ['pip_api_make.py', '--pip_api_configuration', pip_api_configuration_file_path]
    configs = pip_api_make.init_configuration()
    assert configs["multi_package_repositories"] == [os.path.abspath(os.path.dirname(os.path.dirname(this_dir)))]
    assert configs["venv_dir_path"] is None


@pytest.mark.done
def test_init_configuration_no_main_2():
    pip_api_configuration_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "pip_api_configs", "pip_api_configuration_no_main_2.py"))
    sys.argv = ['pip_api_make.py', '--pip_api_configuration', pip_api_configuration_file_path]
    configs = pip_api_make.init_configuration()
    assert configs["multi_package_repositories"] is None
    assert configs["venv_dir_path"] == os.path.abspath(os.path.join(this_dir, "venv"))


@pytest.mark.done
def test_download_https_file_horey_file(tmp_dir_path):
    file_path = os.path.join(tmp_dir_path, "static_methods.py")
    pip_api_make.download_https_file(file_path, "https://raw.githubusercontent.com/AlexeyBeley/horey/main/pip_api/horey/pip_api/static_methods.py")
    assert os.path.isfile(file_path)


@pytest.mark.wip
def test_get_static_methods(tmp_dir_path):
    static_methods = pip_api_make.get_static_methods(tmp_dir_path)
    assert static_methods is not None

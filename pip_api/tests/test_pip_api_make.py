"""
Static method tests

"""

import os
import shutil
import sys
import pytest

this_dir = os.path.dirname(__file__)
horey_sub_path = os.path.abspath(os.path.join(os.path.dirname(this_dir), "horey"))

sys.path.insert(0, os.path.join(horey_sub_path, "pip_api"))
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


@pytest.mark.wip
def test_init_configuration_main():
    pip_api_configuration_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "pip_api_configs", "pip_api_configuration_main.py"))
    sys.argv = ['pip_api_make.py', '--pip_api_configuration', pip_api_configuration_file_path]
    configs = pip_api_make.init_configuration()
    assert configs["multi_package_repositories"] == [os.path.abspath(os.path.dirname(os.path.dirname(this_dir)))]
    assert configs["venv_dir_path"] == os.path.abspath(os.path.join(this_dir, "venv"))


@pytest.mark.wip
def test_init_configuration_main_1():
    pip_api_configuration_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "pip_api_configs", "pip_api_configuration_main_1.py"))
    sys.argv = ['pip_api_make.py', '--pip_api_configuration', pip_api_configuration_file_path]
    configs = pip_api_make.init_configuration()
    assert configs["multi_package_repositories"] == [os.path.abspath(os.path.dirname(os.path.dirname(this_dir)))]
    assert configs["venv_dir_path"] is None


@pytest.mark.wip
def test_init_configuration_main_2():
    pip_api_configuration_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "pip_api_configs", "pip_api_configuration_main_2.py"))
    sys.argv = ['pip_api_make.py', '--pip_api_configuration', pip_api_configuration_file_path]
    configs = pip_api_make.init_configuration()
    assert configs["multi_package_repositories"] is None
    assert configs["venv_dir_path"] == os.path.abspath(os.path.join(this_dir, "venv"))


@pytest.mark.wip
def test_init_configuration_no_main():
    pip_api_configuration_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "pip_api_configs", "pip_api_configuration_no_main.py"))
    sys.argv = ['pip_api_make.py', '--pip_api_configuration', pip_api_configuration_file_path]
    configs = pip_api_make.init_configuration()
    assert configs["multi_package_repositories"] == [os.path.abspath(os.path.dirname(os.path.dirname(this_dir)))]
    assert configs["venv_dir_path"] == os.path.abspath(os.path.join(this_dir, "venv"))


@pytest.mark.wip
def test_init_configuration_no_main_1():
    pip_api_configuration_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "pip_api_configs", "pip_api_configuration_no_main_1.py"))
    sys.argv = ['pip_api_make.py', '--pip_api_configuration', pip_api_configuration_file_path]
    configs = pip_api_make.init_configuration()
    assert configs["multi_package_repositories"] == [os.path.abspath(os.path.dirname(os.path.dirname(this_dir)))]
    assert configs["venv_dir_path"] is None


@pytest.mark.wip
def test_init_configuration_no_main_2():
    pip_api_configuration_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "pip_api_configs", "pip_api_configuration_no_main_2.py"))
    sys.argv = ['pip_api_make.py', '--pip_api_configuration', pip_api_configuration_file_path]
    configs = pip_api_make.init_configuration()
    assert configs["multi_package_repositories"] is None
    assert configs["venv_dir_path"] == os.path.abspath(os.path.join(this_dir, "venv"))


@pytest.mark.wip
def test_download_https_file_horey_file(tmp_dir_path):
    file_path = os.path.join(tmp_dir_path, "standalone_methods.py")
    pip_api_make.download_https_file(file_path,
                                     "https://raw.githubusercontent.com/AlexeyBeley/horey/pip_api_make_provision/pip_api/horey/pip_api/standalone_methods.py")
    assert os.path.isfile(file_path)


@pytest.mark.wip
def test_get_standalone_methods():
    standalone_methods = pip_api_make.get_standalone_methods({"horey_dir_path": os.path.dirname(horey_sub_path)})
    assert standalone_methods is not None


@pytest.mark.wip
def test_install_pip_global():
    assert pip_api_make.install_pip({"horey_dir_path": os.path.dirname(horey_sub_path)})


@pytest.mark.wip
def test_provision_venv(tmp_dir_path):
    assert pip_api_make.provision_venv({"venv_dir_path": tmp_dir_path})


@pytest.mark.wip
def test_install_wheel_venv(tmp_dir_path):
    pip_api_make.provision_venv({"venv_dir_path": tmp_dir_path})
    assert pip_api_make.install_wheel({"venv_dir_path": tmp_dir_path})


@pytest.mark.wip
def test_install_wheel_global():
    assert pip_api_make.install_wheel({})


@pytest.mark.wip
def test_install_requests_venv_with_horey_dir_path(tmp_dir_path):
    pip_api_make.provision_venv({"venv_dir_path": tmp_dir_path})
    pip_api_make.install_wheel({"venv_dir_path": tmp_dir_path})
    assert pip_api_make.install_requests({"venv_dir_path": tmp_dir_path})


@pytest.mark.wip
def test_provision_pip_api_venv_with_horey_dir_path(tmp_dir_path):
    pip_api_make.provision_venv({"venv_dir_path": tmp_dir_path})
    pip_api_make.install_wheel({"venv_dir_path": tmp_dir_path})
    standalone_methods = pip_api_make.provision_pip_api({"horey_dir_path": os.path.dirname(os.path.dirname(os.path.dirname(horey_sub_path))),
                                                     "venv_dir_path": tmp_dir_path})
    assert standalone_methods is not None


@pytest.mark.wip
def test_provision_pip_api_venv_without_horey_dir_path(tmp_dir_path):
    pip_api_make.provision_venv({"venv_dir_path": tmp_dir_path})
    pip_api_make.install_wheel({"venv_dir_path": tmp_dir_path})
    standalone_methods = pip_api_make.provision_pip_api({"horey_dir_path": tmp_dir_path,
                                                     "venv_dir_path": tmp_dir_path})
    assert standalone_methods is not None


@pytest.mark.todo
def test_provision_pip_api_global(tmp_dir_path):
    standalone_methods = pip_api_make.provision_pip_api({"horey_dir_path": tmp_dir_path})
    assert standalone_methods is not None

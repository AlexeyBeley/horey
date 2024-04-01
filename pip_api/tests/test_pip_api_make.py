"""
Static method tests

"""

import os
import shutil
import sys
import pytest
this_dir = os.path.dirname(__file__)
horey_sub_path = os.path.abspath(os.path.join(os.path.dirname(this_dir), "horey"))
horey_parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(horey_sub_path)))
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


@pytest.fixture(name="provisioned_venv_parent_dir_path")
def provisioned_parent_venv_dir_path_fixture(tmp_dir_path):
    pip_api_make.provision_venv({"venv_dir_path": tmp_dir_path})
    yield tmp_dir_path


@pytest.fixture(name="default_configs")
def default_configs_fixture():
    sys.argv = ['pip_api_make.py']
    _default_configs = pip_api_make.init_configuration()
    if os.path.exists(_default_configs["venv_dir_path"]):
        shutil.rmtree(_default_configs["venv_dir_path"])
    os.makedirs(_default_configs["venv_dir_path"])
    yield _default_configs
    if os.path.exists(_default_configs["venv_dir_path"]):
        shutil.rmtree(_default_configs["venv_dir_path"])


@pytest.fixture(name="provisioned_venv_default_configs")
def provisioned_venv_default_configs_fixture(default_configs):
    shutil.rmtree(default_configs["venv_dir_path"])
    os.makedirs(default_configs["venv_dir_path"])
    pip_api_make.provision_venv(default_configs)
    yield default_configs
    shutil.rmtree(default_configs["venv_dir_path"])


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
def test_download_https_file_requests_horey_file_from_remote_source_code(provisioned_venv_parent_dir_path):
    configs = {"venv_dir_path": provisioned_venv_parent_dir_path}
    file_path = os.path.join(provisioned_venv_parent_dir_path, "standalone_methods.py")
    pip_api_make.install_requests(configs)

    pip_api_make.download_https_file_requests(configs, file_path,
                                              "https://raw.githubusercontent.com/AlexeyBeley/horey/main/pip_api/horey/pip_api/standalone_methods.py")
    assert os.path.isfile(file_path)


@pytest.mark.done
def test_download_https_file_requests_horey_file_from_local_source_code(provisioned_venv_parent_dir_path):
    file_path = os.path.join(provisioned_venv_parent_dir_path, "standalone_methods.py")
    configs = {"venv_dir_path": provisioned_venv_parent_dir_path, "horey_parent_dir_path": horey_parent_dir}
    pip_api_make.install_requests(configs)
    pip_api_make.download_https_file_requests(configs, file_path,
                                              "https://raw.githubusercontent.com/AlexeyBeley/horey/main/pip_api/horey/pip_api/standalone_methods.py")
    assert os.path.isfile(file_path)


@pytest.mark.done
def test_download_https_file_urllib_horey_file(tmp_dir_path):
    file_path = os.path.join(tmp_dir_path, "standalone_methods.py")
    pip_api_make.download_https_file_urllib(file_path,
                                            "https://raw.githubusercontent.com/AlexeyBeley/horey/main/pip_api/horey/pip_api/standalone_methods.py")
    assert os.path.isfile(file_path)


@pytest.mark.done
def test_get_standalone_methods():
    standalone_methods = pip_api_make.get_standalone_methods({"horey_parent_dir_path": os.path.dirname(horey_sub_path)})
    assert standalone_methods is not None


@pytest.mark.done
def test_install_pip_global():
    assert pip_api_make.install_pip({"horey_parent_dir_path": os.path.dirname(horey_sub_path)})


@pytest.mark.done
def test_provision_venv(tmp_dir_path):
    assert pip_api_make.provision_venv({"venv_dir_path": tmp_dir_path})


@pytest.mark.done
def test_install_wheel_venv(provisioned_venv_parent_dir_path):
    assert pip_api_make.install_wheel({"venv_dir_path": provisioned_venv_parent_dir_path})


@pytest.mark.done
def test_install_wheel_global():
    assert pip_api_make.install_wheel({})


@pytest.mark.done
def test_install_setuptools_venv(provisioned_venv_parent_dir_path):
    assert pip_api_make.install_setuptools({"venv_dir_path": provisioned_venv_parent_dir_path})


@pytest.mark.done
def test_install_setuptools_global():
    assert pip_api_make.install_setuptools({})


@pytest.mark.done
def test_install_requests_venv_with_horey_parent_dir_path(provisioned_venv_parent_dir_path):
    config = {"venv_dir_path": provisioned_venv_parent_dir_path, "horey_parent_dir_path": horey_parent_dir}
    assert pip_api_make.install_requests(config)


@pytest.mark.done
def test_install_requests_global():
    config = {"horey_parent_dir_path": horey_parent_dir}
    assert pip_api_make.install_requests(config)


@pytest.mark.done
def test_install_requests_venv_download_horey(provisioned_venv_parent_dir_path):
    config = {"venv_dir_path": provisioned_venv_parent_dir_path}
    assert pip_api_make.install_requests(config)


@pytest.mark.done
def test_provision_pip_api_venv_with_horey_parent_dir_path(provisioned_venv_parent_dir_path):
    pip_api_make.install_wheel({"venv_dir_path": provisioned_venv_parent_dir_path})
    standalone_methods = pip_api_make.provision_pip_api({"horey_parent_dir_path": horey_parent_dir,
                                                         "multi_package_repositories": {
                                                             "horey.": os.path.join(provisioned_venv_parent_dir_path,
                                                                                    "horey")},
                                                         "venv_dir_path": provisioned_venv_parent_dir_path})
    assert standalone_methods is not None


@pytest.mark.done
def test_provision_pip_api_venv_without_horey_parent_dir_path(provisioned_venv_parent_dir_path):
    config = {"horey_parent_dir_path": provisioned_venv_parent_dir_path,
              "multi_package_repositories": {"horey.": os.path.join(provisioned_venv_parent_dir_path, "horey")},
              "venv_dir_path": provisioned_venv_parent_dir_path}
    pip_api_make.install_wheel(config)
    pip_api_make.install_requests(config)
    standalone_methods = pip_api_make.provision_pip_api(config)
    assert standalone_methods is not None


@pytest.mark.done
def test_provision_pip_api_global(tmp_dir_path):
    config = {"horey_parent_dir_path": tmp_dir_path,
              "multi_package_repositories": {"horey.": os.path.join(tmp_dir_path, "horey")},}
    standalone_methods = pip_api_make.provision_pip_api(config)
    assert standalone_methods is not None


@pytest.mark.done
def test_default_configs_init_configuration_main(default_configs):
    base_dir = os.path.join(os.path.dirname(pip_api_make.__file__), pip_api_make.get_default_dir())
    assert os.path.isdir(base_dir)
    assert default_configs["venv_dir_path"] == base_dir
    assert default_configs["multi_package_repositories"] == {"horey.": os.path.join(base_dir, "horey")}
    assert default_configs["horey_parent_dir_path"] == base_dir


@pytest.mark.done
def test_default_configs_download_https_file_requests_horey_file_from_remote_source_code(default_configs,
                                                                                         provisioned_venv_default_configs):
    file_path = os.path.join(provisioned_venv_default_configs["venv_dir_path"], "standalone_methods.py")
    pip_api_make.install_requests(default_configs)

    pip_api_make.download_https_file_requests(default_configs, file_path,
                                              "https://raw.githubusercontent.com/AlexeyBeley/horey/main/pip_api/horey/pip_api/standalone_methods.py")
    assert os.path.isfile(file_path)


@pytest.mark.done
def test_default_configs_get_standalone_methods(default_configs):
    standalone_methods = pip_api_make.get_standalone_methods(default_configs)
    assert standalone_methods is not None


@pytest.mark.done
def test_default_configs_install_pip_global(default_configs):
    assert pip_api_make.install_pip(default_configs)


@pytest.mark.done
def test_default_configs_provision_venv(default_configs):
    assert pip_api_make.provision_venv(default_configs)


@pytest.mark.done
def test_default_configs_install_wheel_venv(provisioned_venv_default_configs):
    assert pip_api_make.install_wheel(provisioned_venv_default_configs)


@pytest.mark.done
def test_default_configs_install_setuptools_venv(provisioned_venv_default_configs):
    assert pip_api_make.install_setuptools(provisioned_venv_default_configs)


@pytest.mark.done
def test_default_configs_install_requests_venv_with_horey_parent_dir_path(provisioned_venv_default_configs):
    assert pip_api_make.install_requests(provisioned_venv_default_configs)


@pytest.mark.done
def test_default_configs_install_requests_global(provisioned_venv_default_configs):
    provisioned_venv_default_configs["horey_parent_dir_path"] = horey_parent_dir
    provisioned_venv_default_configs["multi_package_repositories"] = {"horey.": os.path.join(horey_parent_dir, "horey")}
    assert pip_api_make.install_requests(provisioned_venv_default_configs)


@pytest.mark.done
def test_default_configs_install_requests_venv_download_horey(provisioned_venv_default_configs):
    assert pip_api_make.install_requests(provisioned_venv_default_configs)


@pytest.mark.done
def test_default_configs_provision_pip_api_venv_with_horey_parent_dir_path(provisioned_venv_default_configs):
    provisioned_venv_default_configs["horey_parent_dir_path"] = horey_parent_dir
    pip_api_make.install_wheel(provisioned_venv_default_configs)
    pip_api_make.install_requests(provisioned_venv_default_configs)
    standalone_methods = pip_api_make.provision_pip_api(provisioned_venv_default_configs)
    assert standalone_methods is not None


@pytest.mark.done
def test_default_configs_provision_pip_api_venv_without_horey_parent_dir_path(provisioned_venv_default_configs):
    pip_api_make.install_wheel(provisioned_venv_default_configs)
    pip_api_make.install_requests(provisioned_venv_default_configs)
    standalone_methods = pip_api_make.provision_pip_api(provisioned_venv_default_configs)
    assert standalone_methods is not None


@pytest.mark.done
def test_install_requirement_venv_force_reinstall_true():
    pip_api_configuration_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "pip_api_configs", "pip_api_configuration_main.py"))
    sys.argv = f"pip_api_make.py --bootstrap --pip_api_configuration {pip_api_configuration_file_path}".split(" ")
    _default_configs = pip_api_make.main()
    sys.argv = f"pip_api_make.py --force_reinstall --install horey.docker_api --pip_api_configuration {pip_api_configuration_file_path}".split(" ")
    _default_configs = pip_api_make.main()


@pytest.mark.done
def test_install_requirement_venv_force_reinstall_false():
    pip_api_configuration_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "pip_api_configs", "pip_api_configuration_main.py"))
    sys.argv = f"pip_api_make.py --bootstrap --pip_api_configuration {pip_api_configuration_file_path}".split(
        " ")
    _default_configs = pip_api_make.main()
    sys.argv = f"pip_api_make.py --install horey.docker_api --pip_api_configuration {pip_api_configuration_file_path}".split(
        " ")
    _default_configs = pip_api_make.main()


@pytest.mark.done
def test_install_requirement_global_force_reinstall_true():
    pip_api_configuration_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "pip_api_configs", "pip_api_configuration_main_1.py"))
    sys.argv = f"pip_api_make.py --bootstrap --pip_api_configuration {pip_api_configuration_file_path}".split(
        " ")
    _default_configs = pip_api_make.main()
    sys.argv = f"pip_api_make.py --force_reinstall --install horey.docker_api --pip_api_configuration {pip_api_configuration_file_path}".split(
        " ")
    _default_configs = pip_api_make.main()


@pytest.mark.done
def test_install_requirement_global_force_reinstall_false():
    pip_api_configuration_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "pip_api_configs", "pip_api_configuration_main_1.py"))
    sys.argv = f"pip_api_make.py --bootstrap --pip_api_configuration {pip_api_configuration_file_path}".split(
        " ")
    _default_configs = pip_api_make.main()
    sys.argv = f"pip_api_make.py --install horey.docker_api --pip_api_configuration {pip_api_configuration_file_path}".split(
        " ")
    _default_configs = pip_api_make.main()


@pytest.mark.skip
def test_upgrade_requirement():
    pass

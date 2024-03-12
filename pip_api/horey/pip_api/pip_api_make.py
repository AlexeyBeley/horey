"""
The entry point script to run authorization.
python3 pip_api_make.py --pip_api_configuration config/config.py

"""

import argparse
import importlib
import os
import sys
import logging
import urllib.request

handler = logging.StreamHandler()
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s:%(filename)s:%(lineno)s: %(message)s"
)
handler.setFormatter(formatter)
logger = logging.getLogger("pip_api_make")
logger.setLevel("INFO")
logger.addHandler(handler)


class Static:
    """
    Static data. A.K.A. global
    """
    methods = None


def init_configuration_from_py(file_path):
    """
    Init basic config from python file.

    :param file_path:
    :return:
    """

    data = load_module(file_path)
    data = getattr(data, "main")() if hasattr(data, "main") else data

    ret = {}
    for arg_name in ["venv_dir_path", "multi_package_repositories"]:
        ret[arg_name] = getattr(data, arg_name) if hasattr(data, arg_name) else None
    return ret


def load_module(module_full_path):
    """
    Dynamically load python module.

    @param module_full_path:
    @return:
    """

    module_path = os.path.dirname(module_full_path)
    sys.path.insert(0, module_path)
    module_name = os.path.splitext(os.path.basename(module_full_path))[0]
    module = importlib.import_module(module_name)
    module = importlib.reload(module)

    popped_path = sys.path.pop(0)
    if popped_path != module_path:
        raise RuntimeError(
            f"System Path must not be changed while importing configuration_policy: {module_full_path}. "
            f"Changed from {module_path} to {popped_path}"
        )

    return module


def init_configuration():
    """
    Provision
    :return:
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--pip_api_configuration", type=str)
    arguments, rest_args = parser.parse_known_args()
    print(f"Ignoring {rest_args}")
    if arguments.pip_api_configuration is not None:
        if arguments.pip_api_configuration.endswith(".py"):
            return init_configuration_from_py(arguments.pip_api_configuration)
    raise ValueError(arguments.pip_api_configuration)


def download_https_file(local_file_path, url):
    """
    Download file from url.

    :param local_file_path:
    :param url:
    :return:
    """

    urllib.request.urlretrieve(url, local_file_path)


def get_static_methods(configs):
    """
    Get StaticMethods class either from local source code of from horey github

    :return:
    """

    if Static.methods is not None:
        return Static.methods
    dst_dir_path = configs.get("horey_dir_path") or "."
    horey_repo = os.path.join(dst_dir_path, "horey")
    if os.path.isdir(horey_repo):
        module = load_module(os.path.join(horey_repo, "pip_api", "horey", "pip_api", "static_methods.py"))
    else:
        file_path = os.path.join(dst_dir_path, "requirement.py")
        download_https_file(file_path, "https://raw.githubusercontent.com/AlexeyBeley/horey/pip_api_make/pip_api/horey/pip_api/requirement.py")

        file_path = os.path.join(dst_dir_path, "static_methods.py")
        download_https_file(file_path, "https://raw.githubusercontent.com/AlexeyBeley/horey/pip_api_make/pip_api/horey/pip_api/static_methods.py")
        module = load_module(file_path)

    Static.methods = module.StaticMethods
    Static.methods.logger = logger

    return Static.methods


def install_pip_raw():
    """
    Get pip and install

    :return:
    """


def install_pip(configs):
    """
    Install pip in global python.

    :param configs:
    :return:
    """

    horey_dir_path = configs.get("horey_dir_path") or "."
    StaticMethods = get_static_methods(configs)

    command = f"{sys.executable} -m pip -V"
    ret = StaticMethods.execute(command, ignore_on_error_callback=lambda error: "No module named pip" in repr(error))
    stderr = ret.get("stderr")
    if "No module named pip" in stderr:
        pip_installer = os.path.join(horey_dir_path, "get-pip.py")
        download_https_file(pip_installer, "https://bootstrap.pypa.io/get-pip.py")
        command = f"{sys.executable} {pip_installer}"
        ret = StaticMethods.execute(command)
        if "Successfully installed pip" not in ret.get("stdout").strip("\r\n").split("\n")[-1]:
            raise ValueError(ret)
        command = f"{sys.executable} -m pip -V"
        ret = StaticMethods.execute(command)
    elif stderr:
        raise RuntimeError(ret)

    if "pip" not in ret.get("stdout") or "from" not in ret.get("stdout"):
        raise RuntimeError(ret)


def install_venv(configs):
    """
    Install venv module

    :return:
    """

    StaticMethods = get_static_methods(configs)

    command = f"{sys.executable} -m virtualenv --version"
    ret = StaticMethods.execute(command, ignore_on_error_callback=lambda error: "No module named virtualenv" in repr(error))
    stderr = ret.get("stderr")
    if "No module named virtualenv" in stderr:
        command = f"{sys.executable} -m pip install virtualenv"
        ret = StaticMethods.execute(command)
        if "Successfully installed virtualenv" not in ret.get("stdout").strip("\r\n").split("\n")[-1]:
            raise ValueError(ret)
        command = f"{sys.executable} -m virtualenv --version"
        ret = StaticMethods.execute(command)
    elif stderr:
        raise RuntimeError(ret)

    if "virtualenv" not in ret.get("stdout") or "from" not in ret.get("stdout"):
        raise RuntimeError(ret)


def provision_venv(configs):
    """
    Provision new venv in the desired dir

    :return:
    """

    if configs.get("venv_dir_path") is None:
        return

    install_venv(configs)
    StaticMethods = get_static_methods(configs)
    ret = StaticMethods.execute(f"{sys.executable} -m venv {configs.get('venv_dir_path')}")
    print(ret)


def provision_pip_api(configs):
    """
    Provision pip api package in the venv or global python.

    "https://github.com/AlexeyBeley/horey/archive/refs/heads/main.zip"
    "https://github.com/AlexeyBeley/horey/archive/refs/heads/pip_api_make.zip"
    "pip_api_make"
    :return:
    """
    print(configs)


def bootstrap():
    """
    Prepare the environment or venv.

    :return:
    """

    configs = init_configuration()
    install_pip(configs)
    provision_venv(configs)
    provision_pip_api(configs)


if __name__ == "__main__":
    print(sys.argv)
    bootstrap()

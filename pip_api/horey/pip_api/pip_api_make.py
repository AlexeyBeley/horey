"""
The entry point script to run authorization.

"""

import argparse
import importlib
import os
import sys
import urllib3


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

    http = urllib3.PoolManager()
    chunk_size = 16 * 1024
    r = http.request("GET", url, preload_content=False)

    with open(local_file_path, "wb", encoding="utf-8") as out:
        while True:
            data = r.read(chunk_size)
            if not data:
                break
            out.write(data)

    r.release_conn()


def get_static_methods(dst_dir_path):
    """
    Get source static_methods module

    :return:
    """
    file_path = os.path.join(dst_dir_path, "static_methods.py")
    download_https_file(file_path, "https://raw.githubusercontent.com/AlexeyBeley/horey/main/pip_api/horey/pip_api/static_methods.py")
    module = load_module(file_path)
    return module.StaticMethods


def install_pip(configs):
    """
    Install pip in global python.

    :param configs:
    :return:
    """


    horey_dir_path = configs.get("horey_dir_path") or "."
    StaticMethods = get_static_methods(horey_dir_path)

    command = f"{sys.executable} -m pip freeze"
    ret = StaticMethods.execute(command)
    print(ret)

    pip_installer = os.path.join(horey_dir_path, "get-pip.py")
    download_https_file(pip_installer, "https://bootstrap.pypa.io/get-pip.py")


def install_venv():
    """
    Install venv module

    :return:
    """


def provision_venv(configs):
    """
    Provision new venv in the desired dir

    :return:
    """
    print(configs)


def provision_pip_api(configs):
    """
    Provision pip api package in the venv or global python.

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
    install_venv()
    provision_venv(configs)
    provision_pip_api(configs)


if __name__ == "__main__":
    print(sys.argv)
    bootstrap()

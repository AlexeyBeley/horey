"""
The entry point script to run authorization.
python3 pip_api_make.py --pip_api_configuration config/config.py

"""

import argparse
import importlib
import json
import os
import shutil
import sys
import logging
import urllib.request
import zipfile
from time import perf_counter

handler = logging.StreamHandler()
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s:%(filename)s:%(lineno)s: %(message)s"
)
handler.setFormatter(formatter)
logger = logging.getLogger("pip_api_make")
logger.setLevel("INFO")
logger.addHandler(handler)


class Standalone:
    """
    Standalone data. A.K.A. global
    """
    methods = None


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


def get_default_dir():
    """
    Generate default build directory for downloads.

    :return:
    """

    pip_api_default_dir_name = "pip_api_default_dir"
    pip_api_default_dir_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), pip_api_default_dir_name)
    if not os.path.exists(pip_api_default_dir_path):
        os.makedirs(pip_api_default_dir_path, exist_ok=True)
    return pip_api_default_dir_path


def init_configuration():
    """
    Provision
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip_api_configuration", type=str)
    parser.add_argument("--install", type=str)
    parser.add_argument("--bootstrap",  action=argparse.BooleanOptionalAction)
    parser.add_argument("--force_reinstall", action=argparse.BooleanOptionalAction, default=False)
    arguments = parser.parse_args()

    if arguments.pip_api_configuration is not None:
        if arguments.pip_api_configuration.endswith(".py"):
            ret = init_configuration_from_py(arguments.pip_api_configuration)
        else:
            raise RuntimeError("Not supported pip_api_configuration file extension")
    else:
        pip_api_default_dir_path = get_default_dir()

        ret = {"venv_dir_path": pip_api_default_dir_path,
            "multi_package_repositories": {"horey.": os.path.join(pip_api_default_dir_path, "horey")},
            "horey_parent_dir_path": pip_api_default_dir_path,
            }

    ret.update(vars(arguments))
    return ret


def init_configuration_from_py(file_path):
    """
    Init basic config from python file.

    :param file_path:
    :return:
    """

    data = load_module(file_path)
    data = getattr(data, "main")() if hasattr(data, "main") else data

    ret = {}
    for arg_name in ["venv_dir_path", "multi_package_repositories", "horey_parent_dir_path"]:
        ret[arg_name] = getattr(data, arg_name) if hasattr(data, arg_name) else None

    if not ret.get("horey_parent_dir_path"):
        if ret.get("multi_package_repositories"):
            for repo_path in ret.get("multi_package_repositories").values():
                if not repo_path.strip("/").endswith("horey"):
                    continue
                ret["horey_parent_dir_path"] = os.path.dirname(repo_path)
                break

    return ret


def download_https_file_requests(configs, local_file_path, url):
    """
    Download file from url.
    Why should I use two methods and import requests in the middle of the script?
    Because Microsoft is SHIT, that is why. It fails on SSL validation.

    Shamelessly stolen from: https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests

    :param local_file_path:
    :param url:
    :return:
    """

    StandaloneMethods = get_standalone_methods(configs)
    return StandaloneMethods.download_https_file_requests(local_file_path, url)


def download_https_file_urllib(local_file_path, url):
    """
    Download file from url.

    :param local_file_path:
    :param url:
    :return:
    """

    urllib.request.urlretrieve(url, local_file_path)


def get_standalone_methods(configs):
    """
    Get StandaloneMethods class either from local source code of from horey github

    :return:
    """

    dst_dir_path = configs.get("horey_parent_dir_path") or get_default_dir()

    horey_repo = os.path.join(dst_dir_path, "horey")
    venv_dir_path = configs.get("venv_dir_path")
    multi_package_map = configs.get("multi_package_repositories") or {"horey.": horey_repo}

    if Standalone.methods is not None and \
        Standalone.methods.venv_dir_path == venv_dir_path and \
        Standalone.methods.multi_package_repo_to_prefix_map == multi_package_map:
        return Standalone.methods

    if os.path.isdir(horey_repo):
        module = load_module(os.path.join(horey_repo, "pip_api", "horey", "pip_api", "standalone_methods.py"))
    else:
        branch_name = "main"
        file_path = os.path.join(dst_dir_path, "package.py")
        download_https_file_urllib(file_path, f"https://raw.githubusercontent.com/AlexeyBeley/horey/{branch_name}/pip_api/horey/pip_api/package.py")

        file_path = os.path.join(dst_dir_path, "requirement.py")
        download_https_file_urllib(file_path, f"https://raw.githubusercontent.com/AlexeyBeley/horey/{branch_name}/pip_api/horey/pip_api/requirement.py")

        file_path = os.path.join(dst_dir_path, "standalone_methods.py")
        download_https_file_urllib(file_path, f"https://raw.githubusercontent.com/AlexeyBeley/horey/{branch_name}/pip_api/horey/pip_api/standalone_methods.py")
        module = load_module(file_path)

    Standalone.methods = module.StandaloneMethods(venv_dir_path, multi_package_map)
    module.StandaloneMethods.logger = logger

    logger.info(f"StandaloneMethods initialized with python command: {Standalone.methods.python_interpreter_command=}")
    try:
        response = Standalone.methods.execute(f'{Standalone.methods.python_interpreter_command} -c "import sys; print(sys.executable)"')
        logger.info(f"Going to use this python: {response}")
    except RuntimeError:
        # This error can happend when venv is not yet initialized
        pass

    return Standalone.methods


def install_pip(configs):
    """
    Install pip in global python.

    :param configs:
    :return:
    """

    logger.info("Installing pip")
    horey_parent_dir_path = configs.get("horey_parent_dir_path") or get_default_dir()
    StandaloneMethods = get_standalone_methods(configs)

    command = f"{sys.executable} -m pip -V"
    ret = StandaloneMethods.execute(command, ignore_on_error_callback=lambda error: "No module named pip" in repr(error))
    stderr = ret.get("stderr")
    if "No module named pip" in stderr:
        pip_installer = os.path.join(horey_parent_dir_path, "get-pip.py")
        download_https_file_urllib(pip_installer, "https://bootstrap.pypa.io/get-pip.py")
        command = f"{sys.executable} {pip_installer}"
        ret = StandaloneMethods.execute(command)
        if "Successfully installed pip" not in ret.get("stdout").strip("\r\n").split("\n")[-1]:
            raise ValueError(ret)
        command = f"{sys.executable} -m pip -V"
        ret = StandaloneMethods.execute(command)
    elif stderr:
        raise RuntimeError(ret)

    if "pip" not in ret.get("stdout") or "from" not in ret.get("stdout"):
        raise RuntimeError(ret)
    return True


def check_package_installed(command_output, package_name):
    """

    :param command_output:
    :return:
    """
    installed_packages = json.loads(command_output["stdout"])
    for dict_package in installed_packages:
        if dict_package.get("name") == package_name:
            return True
    return False


def install_requests(configs):
    """
    Install wheel in global python or venv

    :param configs:
    :return:
    """

    logger.info("Installing requests")

    StandaloneMethods = get_standalone_methods(configs)
    return StandaloneMethods.install_requirement_from_string(os.path.abspath(__file__), "requests==2.31.0")


def install_requests_old(configs):
    """
    Install pip in global python.

    :param configs:
    :return:
    """

    logger.info("Installing requests")

    StandaloneMethods = get_standalone_methods(configs)
    # check if possible command = f"{StandaloneMethods.python_interpreter_command} -m pip list --format json"
    command = f"{sys.executable} -m pip list --format json"
    ret = StandaloneMethods.execute(command)
    if check_package_installed(ret, "requests"):
        return True

    command = f"{sys.executable} -m pip install requests==2.31.0"
    ret = StandaloneMethods.execute(command)
    if "Successfully installed " not in ret.get("stdout").strip("\r\n").split("\n")[-1]:
        raise ValueError(ret)
    command = f"{sys.executable} -m pip list --format json"
    ret = StandaloneMethods.execute(command)
    if check_package_installed(ret, "requests"):
        return True

    raise RuntimeError("Was not able to install requests")


def install_wheel(configs):
    """
    Install wheel in global python or venv

    :param configs:
    :return:
    """

    logger.info("Installing wheel")

    StandaloneMethods = get_standalone_methods(configs)
    return StandaloneMethods.install_requirement_from_string(os.path.abspath(__file__), "wheel")


def install_setuptools(configs):
    """
    Install setuptools in global python or venv

    :param configs:
    :return:
    """

    logger.info("Installing setuptools")
    StandaloneMethods = get_standalone_methods(configs)

    return StandaloneMethods.install_requirement_from_string(os.path.abspath(__file__), "setuptools")


def install_venv(configs):
    """
    Install venv module

    :return:
    """

    logger.info("Installing venv")

    StandaloneMethods = get_standalone_methods(configs)

    command = f"{sys.executable} -m virtualenv --version"
    ret = StandaloneMethods.execute(command, ignore_on_error_callback=lambda error: "No module named virtualenv" in repr(error))
    stderr = ret.get("stderr")
    if "No module named virtualenv" in stderr:
        command = f"{sys.executable} -m pip install virtualenv"
        ret = StandaloneMethods.execute(command)
        if "Successfully installed" not in ret.get("stdout").strip("\r\n").split("\n")[-1]:
            raise ValueError(ret)
        command = f"{sys.executable} -m virtualenv --version"
        ret = StandaloneMethods.execute(command)
    elif stderr:
        raise RuntimeError(ret)

    if "virtualenv" not in ret.get("stdout") or "from" not in ret.get("stdout"):
        raise RuntimeError(ret)


def provision_venv(configs):
    """
    Provision new venv in the desired dir

    :return:
    """

    logger.info("Provisioning venv")

    if configs.get("venv_dir_path") is None:
        return True
    try:
        install_venv(configs)
    except Exception as inst_error:
        logger.error(inst_error)
        breakpoint()

    StandaloneMethods = get_standalone_methods(configs)
    venv_path = os.path.abspath(configs.get("venv_dir_path"))
    logger.info(f"Creating new venv in: '{venv_path}'")
    ret = StandaloneMethods.execute(f"{sys.executable} -m venv {venv_path}")
    logger.info(ret)
    return True


def provision_pip_api(configs):
    """
    Provision pip api package in the venv or global python.

    "https://github.com/AlexeyBeley/horey/archive/refs/heads/main.zip"
    "https://github.com/AlexeyBeley/horey/archive/refs/heads/main.zip"
    "pip_api_make"
    :return:
    """
    logger.info("Provisioning pip_api")
    horey_parent_dir_path = configs.get("horey_parent_dir_path") or get_default_dir()
    if not os.path.isdir(os.path.join(horey_parent_dir_path, "horey")):
        branch_name = "main"
        file_path = os.path.join(horey_parent_dir_path, "main.zip")
        download_https_file_requests(configs, file_path,
                            f"https://github.com/AlexeyBeley/horey/archive/refs/heads/{branch_name}.zip")
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(horey_parent_dir_path)
        shutil.copytree(os.path.join(horey_parent_dir_path, f"horey-{branch_name}"), os.path.join(horey_parent_dir_path, "horey"))

    StandaloneMethods = get_standalone_methods(configs)
    if not StandaloneMethods.install_requirement_from_string(os.path.abspath(__file__), "horey.pip_api"):
        raise RuntimeError(f"Installation failed: {os.path.abspath(__file__)}, 'horey.pip_api'")
    return StandaloneMethods


def bootstrap(configs):
    """
    Prepare the environment or venv.

    :return:
    """

    install_pip(configs)
    provision_venv(configs)
    install_requests(configs)
    install_setuptools(configs)
    install_wheel(configs)
    provision_pip_api(configs)


def install(configs):
    """
    Run install

    :param configs:
    :return:
    """
    start = perf_counter()
    logger.info(f"Starting installation: {configs}")
    StandaloneMethods = get_standalone_methods(configs)
    force_reinstall = configs.get("force_reinstall")
    if force_reinstall is None:
        force_reinstall = False

    if requirement := configs.get("install"):
        response = StandaloneMethods.install_requirement_from_string(os.path.abspath(__file__), requirement, force_reinstall=force_reinstall)
        logger.info(f"Installation took {perf_counter()-start}")
        return response

    raise ValueError(f"Parameter 'install' must be valid: {configs}")


def main():
    """
    Entrypoint

    :return:
    """

    configs = init_configuration()
    if configs.get("bootstrap"):
        return bootstrap(configs)

    if configs.get("install"):
        venv_path = configs.get("venv_dir_path")
        if venv_path and not os.path.isdir(venv_path):
            bootstrap(configs)
        return install(configs)

    raise ValueError(f"Expecting for 'bootstrap' or 'install' command: {configs}")


if __name__ == "__main__":
    logger.info(sys.argv)
    main()

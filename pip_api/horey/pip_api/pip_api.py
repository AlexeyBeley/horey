"""
PIP API module.

"""

import os
import subprocess
import uuid
import json

from horey.h_logger import get_logger
from horey.pip_api.requirement import Requirement
from horey.pip_api.pip_api_configuration_policy import PipAPIConfigurationPolicy
from horey.common_utils.common_utils import CommonUtils

logger = get_logger()


class Package:
    """
    Installed package.

    """

    def __init__(self, dict_src):
        self.name = dict_src["name"]
        self.version = dict_src["version"]
        self.multi_package_repo_prefix = None
        self.multi_package_repo_path = None

    def check_version_requirements(self, requirement: Requirement):
        """
        Check req.
        :param requirement:
        :return:
        """
        self_int_version_lst = [int(sub_ver) for sub_ver in self.version.split(".")]

        return self.check_version_min_requirement(
            requirement, self_int_version_lst
        ) and self.check_version_max_requirement(requirement, self_int_version_lst)

    def check_version_min_requirement(self, requirement, self_int_version_lst):
        """
        Check self version against min required version

        :param requirement:
        :param self_int_version_lst:
        :return:
        """

        if requirement.min_version == self.version:
            if requirement.include_min:
                return True
            return False
        if requirement.min_version is None:
            return True

        requirement_int_version_lst = [
            int(sub_ver) for sub_ver in requirement.min_version.split(".")
        ]
        for index, package_sub_ver_value in enumerate(self_int_version_lst):
            try:
                if package_sub_ver_value > requirement_int_version_lst[index]:
                    break
            except IndexError:
                break

            if package_sub_ver_value < requirement_int_version_lst[index]:
                return False

        return True

    def check_version_max_requirement(self, requirement, self_int_version_lst):
        """
        Check max req.

        :param requirement:
        :param self_int_version_lst:
        :return:
        """
        print(self_int_version_lst)
        if requirement.max_version is None:
            return True

        if requirement.max_version == self.version:
            if requirement.include_max:
                return True
            return False
        raise NotImplementedError(f"todo: requirement.name: {requirement.name}, requirement.max_version: {requirement.max_version}, "
                                  f"self.version: {self.version}")


class PipAPI:
    """
    API to pip functionality

    """

    REQUIREMENTS = {}

    def __init__(self, configuration: PipAPIConfigurationPolicy = None):
        self.packages = None
        self.configuration = configuration
        self.multi_package_repos_prefix_map = {}
        self.init_configuration()

    def init_configuration(self):
        """
        Init multi package repositories data.

        :return:
        """

        if self.configuration is None:
            return

        for repo_path in self.configuration.multi_package_repositories:
            self.init_multi_package_repository(repo_path)

        if self.configuration.venv_dir_path is not None:
            if not os.path.exists(
                os.path.join(self.configuration.venv_dir_path, "bin", "activate")
            ):
                self.execute(
                    f"python3.8 -m venv {self.configuration.venv_dir_path} --system-site-packages",
                    ignore_venv=True,
                )

                self.execute("pip3.8 install --upgrade pip")
                self.execute("pip3.8 install setuptools>=45")

                # todo:
                #self.execute("wget https://bootstrap.pypa.io/get-pip.py")
                #self.execute("python3.8 get-pip.py")

    def init_multi_package_repository(self, repo_path):
        """
        Init configuration.

        :param repo_path:
        :return:
        """
        try:
            repo_package_prefix = CommonUtils.load_object_from_module(
                os.path.join(repo_path, "multi_package_repository_configuration.py"), "main"
            )
        except Exception as exception_inst:
            raise RuntimeError(f"Can not load multi package repo config from: '{repo_path}'") from exception_inst

        self.multi_package_repos_prefix_map[repo_package_prefix.prefix] = repo_path

    def init_packages(self):
        """
        Initialize packages with their repo paths and versions

        :return:
        """

        response = self.execute("pip3.8 list --format json")
        # response = self.execute("pip3.8 uninstall -y horey.common-utils")
        # response = self.execute("pip3.8 uninstall -y horey.h-logger")
        # response = self.execute("pip3.8 uninstall -y horey.configuration_policy")
        lst_packages = json.loads(response)

        objects = []
        for dict_package in lst_packages:
            package = Package(dict_package)
            objects.append(package)
            for prefix, repo_path in self.multi_package_repos_prefix_map.items():
                if package.name.startswith(prefix):
                    package.multi_package_repo_prefix = prefix
                    package.multi_package_repo_path = repo_path

        self.packages = objects

    class BashError(RuntimeError):
        """
        Failed to run bash

        """

    def run_bash(
        self, command, ignore_on_error_callback=None, timeout=60 * 10, debug=True
    ):
        """
        Run bash command, return stdout, stderr and return code.
        Timeout is used fot stuck commands - for example if the command expects for user input.
        Like dpkg installation approve - happens all the time with logstash package.

        @param timeout: In seconds. Default 10 minutes
        @param debug: print return code, stdout and stderr
        @param command:
        @param ignore_on_error_callback:
        @return:
        """

        logger.info(f"run_bash: {command}")

        file_name = f"tmp-{str(uuid.uuid4())}.sh"
        with open(file_name, "w", encoding="utf-8") as file_handler:
            file_handler.write(command)
            command = f"/bin/bash {file_name}"

        ret = subprocess.run(
            [command], capture_output=True, shell=True, timeout=timeout, check=False
        )

        os.remove(file_name)

        return_dict = {
            "stdout": ret.stdout.decode().strip("\n"),
            "stderr": ret.stderr.decode().strip("\n"),
            "code": ret.returncode,
        }
        if debug:
            logger.info(f"return_code: {return_dict['code']}")

            stdout_log = "stdout:\n" + str(return_dict["stdout"])
            for line in stdout_log.split("\n"):
                logger.info(f"stdout_log line: {line}")

            stderr_log = "stderr:\n" + str(return_dict["stderr"])
            for line in stderr_log.split("\n"):
                logger.info(f"stderr_log line: {line}")

        if ret.returncode != 0:
            if ignore_on_error_callback is None:
                raise self.BashError(json.dumps(return_dict))

            if not ignore_on_error_callback(return_dict):
                raise self.BashError(json.dumps(return_dict))

        return return_dict

    def execute(self, command, ignore_venv=False):
        """
        Execute bash command.

        :param command:
        :param ignore_venv: do not run in venv
        :return:
        """
        logger.info(f"executing: '{command}'")
        if (
            not ignore_venv
            and self.configuration is not None
            and self.configuration.venv_dir_path is not None
        ):
            command = f"source {os.path.join(self.configuration.venv_dir_path, 'bin/activate')} && {command}"
        ret = self.run_bash(command)

        return ret["stdout"]

    def install_requirements(
        self, requirements_file_path, update=False, update_from_source=False
    ):
        """
        Prepare list of requirements to be installed and install those missing.

        :param requirements_file_path:
        :return:
        """
        logger.info(f"Installing requirements from file: '{requirements_file_path}'")
        self.init_packages()
        self.compose_requirements_recursive(requirements_file_path)

        if not self.REQUIREMENTS:
            return
        for requirement in reversed(self.REQUIREMENTS.values()):
            if not self.requirement_satisfied(requirement):
                self.install_requirement(requirement)
                continue

            if update:
                self.install_requirement(requirement)
                continue

            if update_from_source:
                for prefix in self.multi_package_repos_prefix_map:
                    if requirement.name.startswith(prefix):
                        self.install_requirement(requirement)
                        break

    def get_installed_packages(self):
        """

        :return:
        """
        raise DeprecationWarning("Use init")

    def install_requirement(self, requirement: Requirement):
        """
        Install single requirement.

        :param requirement:
        :return:
        """

        for prefix, repo_path in self.multi_package_repos_prefix_map.items():
            if requirement.name.startswith(prefix):
                requirement.multi_package_repo_prefix = prefix
                requirement.multi_package_repo_path = repo_path
                return self.install_multi_package_repo_requirement(requirement)

        return self.execute(f"pip3.8 install {requirement.generate_install_string()}")

    def install_multi_package_repo_requirement(self, requirement):
        """
        Build package and install it.

        :param requirement:
        :return:
        """

        package_dirname = requirement.name.split(".")[-1]
        ret = self.execute(
            f"cd {requirement.multi_package_repo_path} && make install_wheel-{package_dirname}"
        )
        lines = ret.split("\n")

        index = -2 if "Leaving directory" in lines[-1] else -1
        if lines[index] != f"done installing {package_dirname}":
            raise RuntimeError(
                f"Could not install {package_dirname} from source code:\n {ret}"
            )

    def requirement_satisfied(self, requirement: Requirement):
        """
        Check weather the requirement is already installed.

        :param requirement:
        :return:
        """

        for package in self.packages:
            if package.name.replace("_", "-") != requirement.name.replace("_", "-"):
                continue
            return package.check_version_requirements(requirement)

        return False

    def compose_requirements_recursive(self, requirements_file_path):
        """
        Compose requirements based on multi package repos map.

        :param requirements_file_path:
        :return:
        """

        requirements = self.init_requirements_raw(requirements_file_path)
        for requirement in requirements:
            if requirement.name in self.REQUIREMENTS:
                self.update_existing_requirement(requirement)
                continue

            self.REQUIREMENTS[requirement.name] = requirement

            for prefix, repo_path in self.multi_package_repos_prefix_map.items():
                if requirement.name.startswith(prefix):
                    package_dir_name = requirement.name.split(".")[-1]
                    multi_package_repo_requirements_file_path = os.path.join(
                        repo_path, package_dir_name, "requirements.txt"
                    )
                    self.compose_requirements_recursive(
                        multi_package_repo_requirements_file_path
                    )
                    break
            else:
                self.REQUIREMENTS[requirement.name] = requirement

    @staticmethod
    def init_requirements_raw(requirements_file_path):
        """
        Init requirements from single file.

        :param requirements_file_path:
        :return:
        """

        if not os.path.exists(requirements_file_path):
            return []

        requirements = []

        with open(requirements_file_path, "r", encoding="utf-8") as file_handler:
            lines = [
                line.strip("\n") for line in file_handler.readlines() if line != "\n"
            ]

        for line in lines:
            requirements.append(Requirement(line))

        return requirements

    def update_existing_requirement(self, requirement: Requirement):
        """
        Update with new requirements.

        """
        current = self.REQUIREMENTS[requirement.name]

        if (
            requirement.min_version is not None
            and current.min_version != requirement.min_version
        ):
            if current.min_version is None:
                current.min_version = requirement.min_version
                current.include_min = requirement.include_min
            else:
                raise NotImplementedError(f"requirement.name: {requirement.name} current.min_version: {current.min_version}, requirement.min_version: {requirement.min_version}")
        if (
            requirement.include_min is not None
            and current.include_min != requirement.include_min
        ):
            if current.include_min is None:
                current.include_min = requirement.include_min
            else:
                raise NotImplementedError()

        if (
            requirement.max_version is not None
            and current.max_version != requirement.max_version
        ):
            if current.max_version is None:
                current.max_version = requirement.max_version
                current.include_max = requirement.include_max
            else:
                raise NotImplementedError(
                    f"{current.max_version}/{requirement.max_version}"
                )

        if (
            requirement.include_max is not None
            and current.include_max != requirement.include_max
        ):
            if current.include_max is None:
                current.include_max = requirement.include_max
            else:
                raise NotImplementedError()

    def get_horey_package_requirements(self, package_name):
        """

        :param package_name:
        :return:
        _, package_name = package_name.split(".")
        horey_package_requirements_path = os.path.join(self.horey_repo_path, package_name, "requirements.txt")
        return self.init_requirements_raw(horey_package_requirements_path)
        """
        raise NotImplementedError("Old code.")

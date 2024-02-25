"""
Methods which can be used without package installation.
"""
import json
import os
import uuid

import sys
import shutil
import subprocess
from requirement import Requirement
from package import Package


class StaticMethods:
    """
    Static methods, can be used both from package and directly.
    """

    HOREY_REPO_PATH = os.path.abspath(os.path.join(__file__, "..", "..", "..", ".."))
    PYTHON_INTERPRETER_COMMAND = sys.executable if "win" not in sys.platform.lower() else f'"{sys.executable}"'
    logger = None

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
            StaticMethods.logger.info(f"Initializing requirement '{line}' from file '{requirements_file_path}'")
            requirements.append(Requirement(requirements_file_path, line))

        return requirements

    @staticmethod
    def get_requirements_file_path(repo_path, package_name):
        """
        Multipackage repo packages requirements.txt

        :param repo_path:
        :param package_name:
        :return:
        """

        return os.path.join(repo_path, package_name, "requirements.txt")

    @staticmethod
    def compose_requirements_recursive(requirements_file_path, requirements_aggregator, multi_package_repos_prefix_map):
        """
        Compose requirements based on multi package repos map.

        :param multi_package_repos_prefix_map:
        :param requirements_aggregator:
        :param requirements_file_path:
        :return:
        """

        requirements = StaticMethods.init_requirements_raw(requirements_file_path)
        for requirement in requirements:
            if requirement.name in requirements_aggregator:
                StaticMethods.update_existing_requirement(requirement, requirements_aggregator)
                continue

            requirements_aggregator[requirement.name] = requirement

            for prefix, repo_path in multi_package_repos_prefix_map.items():
                if requirement.name.startswith(prefix):
                    package_dir_name = requirement.name.split(".")[-1]
                    multi_package_repo_requirements_file_path = os.path.join(
                        repo_path, package_dir_name, "requirements.txt"
                    )
                    StaticMethods.compose_requirements_recursive(
                        multi_package_repo_requirements_file_path, requirements_aggregator,
                        multi_package_repos_prefix_map
                    )
                    break
            else:
                requirements_aggregator[requirement.name] = requirement

    # pylint: disable= too-many-branches
    @staticmethod
    def update_existing_requirement(requirement: Requirement, requirements_aggregator: dict):
        """
        Update with new requirements.

        """

        error_requirement = f"requirement.name: {requirement.name}"

        current = requirements_aggregator[requirement.name]
        common_min_requirement = StaticMethods.get_common_min_requirement(current, requirement)
        common_max_requirement = StaticMethods.get_common_max_requirement(current, requirement)
        if common_min_requirement.min_version is None:
            if current.min_version is not None:
                raise RuntimeError(f"Unreachable state: Current min version: {current.min_version} "
                                   f"required min version: {common_min_requirement.min_version}, ")

        if common_max_requirement.max_version is None:
            if current.max_version is not None:
                raise RuntimeError(f"Unreachable state: Current max version: {current.max_version} "
                                   f"required max version: {common_max_requirement.max_version}, ")

        current.min_version = common_min_requirement.min_version
        current.include_min = common_min_requirement.include_min
        current.max_version = common_max_requirement.max_version
        current.include_max = common_max_requirement.include_max

        min_is_none = False
        if current.min_version is None:
            if current.include_min is not None:
                raise RuntimeError(
                    f"current.min_version: {current.min_version}, current.include_min: {current.include_min}")
            min_is_none = True

        if current.max_version is None:
            if current.include_max is not None:
                raise RuntimeError(
                    f"current.max_version: {current.max_version}, current.include_max: {current.include_max}")
            return

        if min_is_none:
            return

        if current.min_version == current.max_version:
            if not current.include_min or not current.include_max:
                raise RuntimeError(f"common_requirement min_version: {current.min_version}, "
                                   f"common_requirement max_version: {current.max_version}, "
                                   f"common_requirement include_min: {current.include_min}, "
                                   f"common_requirement include_max: {current.include_max}, "
                                   f"first requirements file: {current.requirements_file_path}, "
                                   f"second requirements file: {requirement.requirements_file_path}")

            return

        lst_min = common_min_requirement.min_version.split(".")
        lst_max = common_max_requirement.max_version.split(".")

        if len(lst_min) != len(lst_max):
            raise RuntimeError(f"{error_requirement} len min {lst_min} != len max {lst_max}")

        for x, y in zip(lst_min, lst_max):
            if x < y:
                return

            if x > y:
                raise ValueError(f"{error_requirement} min {lst_min} > max {lst_max}")

    @staticmethod
    def get_common_min_requirement(this: Requirement, other: Requirement):
        """
        Get the common requirement for minimum version.

        :param this:
        :param other:
        :return:
        """

        if this.min_version is None:
            return other

        if other.min_version is None:
            return this

        if this.min_version == other.min_version:
            return this if not this.include_min else other

        lst_this = [int(x) for x in this.min_version.split(".")]
        lst_other = [int(x) for x in other.min_version.split(".")]
        if len(lst_other) != len(lst_this):
            raise NotImplementedError(
                f"Requirement for '{this.name}' in {os.path.abspath(this.requirements_file_path)}:{lst_this} vs {os.path.abspath(other.requirements_file_path)}:{lst_other}")
        for i, this_part in enumerate(lst_this):
            if lst_other[i] > this_part:
                return other
            if this_part > lst_other[i]:
                return this
        raise RuntimeError(f"This should be unreachable: this_min: {this.min_version}, other_min: {other.min_version}")

    @staticmethod
    def get_common_max_requirement(this: Requirement, other: Requirement):
        """
        Get the common requirement for maximum version.

        :param this:
        :param other:
        :return:
        """
        if this.max_version is None:
            return other

        if other.max_version is None:
            return this

        if this.max_version == other.max_version:
            return this if not this.include_max else other

        lst_this = [int(x) for x in this.min_version.split(".")]
        lst_other = [int(x) for x in other.min_version.split(".")]
        if len(lst_other) != len(lst_this):
            raise NotImplementedError()
        for i, this_part in enumerate(lst_this):
            if lst_other[i] < this_part:
                return other
            if this_part < lst_other[i]:
                return this
        raise RuntimeError(f"This should be unreachable: this_min: {this.min_version}, other_min: {other.min_version}")

    @staticmethod
    def install_requirements(
            requirements_file_path, multi_package_repos_prefix_map, update=False, update_from_source=False
    ):
        """
        Prepare list of requirements to be installed and install those missing.

        :param requirements_file_path:
        :return:
        """

        StaticMethods.logger.info(f"Installing requirements from file: '{requirements_file_path}'")
        requirements_aggregator = {}
        StaticMethods.compose_requirements_recursive(requirements_file_path, requirements_aggregator,
                                                     multi_package_repos_prefix_map)
        if not requirements_aggregator:
            return
        installed_packages = StaticMethods.init_packages()

        for requirement in reversed(requirements_aggregator.values()):
            if not StaticMethods.requirement_satisfied(requirement, installed_packages):
                StaticMethods.install_requirement(requirement, multi_package_repos_prefix_map)
                continue

            if update:
                StaticMethods.install_requirement(requirement, multi_package_repos_prefix_map)
                continue

            if update_from_source:
                for prefix in multi_package_repos_prefix_map:
                    if requirement.name.startswith(prefix):
                        StaticMethods.install_requirement(requirement, multi_package_repos_prefix_map)
                        break

    @staticmethod
    def init_packages(multi_package_repos_prefix_map=None):
        """
        Initialize packages with their repo paths and versions

        :return:
        """

        response = StaticMethods.execute(f"{StaticMethods.PYTHON_INTERPRETER_COMMAND} -m pip list --format json")
        lst_packages = json.loads(response["stdout"])

        objects = []
        for dict_package in lst_packages:
            package = Package(dict_package)
            objects.append(package)
            if multi_package_repos_prefix_map:
                for prefix, repo_path in multi_package_repos_prefix_map.items():
                    if package.name.startswith(prefix):
                        package.multi_package_repo_prefix = prefix
                        package.multi_package_repo_path = repo_path
        return objects

    @staticmethod
    def install_requirement(requirement: Requirement, multi_package_repos_prefix_map):
        """
        Install single requirement.

        :param multi_package_repos_prefix_map:
        :param requirement:
        :return:
        """

        for prefix, repo_path in multi_package_repos_prefix_map.items():
            if requirement.name.startswith(prefix):
                requirement.multi_package_repo_prefix = prefix
                requirement.multi_package_repo_path = repo_path
                return StaticMethods.install_multi_package_repo_requirement(requirement)

        return StaticMethods.execute(
            f"{StaticMethods.PYTHON_INTERPRETER_COMMAND} -m pip install --force-reinstall {requirement.generate_install_string()}")

    @staticmethod
    def install_multi_package_repo_requirement(requirement):
        """
        Build package and install it.

        :param requirement:
        :return:
        """

        package_dir_name = requirement.name.split(".")[-1]
        StaticMethods.build_and_install_package(requirement.multi_package_repo_path, package_dir_name)

    @staticmethod
    def build_and_install_package(multi_package_repo_path, package_dir_name):
        """
        Build the wheel and install it.

        :param multi_package_repo_path:
        :param package_dir_name:
        :return:
        """

        breakpoint()
        tmp_build_dir = os.path.join(multi_package_repo_path, "build", "_build")
        os.makedirs(tmp_build_dir, exist_ok=True)

        build_dir_path = os.path.join(tmp_build_dir, package_dir_name)
        response = StaticMethods.create_wheel(os.path.join(multi_package_repo_path, package_dir_name), build_dir_path)
        breakpoint()

        ret = StaticMethods.execute(
            f"cd {multi_package_repo_path} && make install_wheel-{package_dir_name}"
        )
        lines = ret["stdout"].split("\n")
        index = -2 if "Leaving directory" in lines[-1] else -1
        if lines[index] != f"done installing {package_dir_name}":
            raise RuntimeError(
                f"Could not install {package_dir_name} from source code:\n {ret}"
            )

    @staticmethod
    def requirement_satisfied(requirement: Requirement, packages):
        """
        Check weather the requirement is already installed.

        :param packages:
        :param requirement:
        :return:
        """

        for package in packages:
            if package.name.replace("_", "-") != requirement.name.replace("_", "-"):
                continue
            return package.check_version_requirements(requirement)

        return False

    @staticmethod
    def create_wheel(source_code_path, build_dir_path, branch_name=None):
        """
        Create wheel.

        :param source_code_path: Path to the directory with setup.py
        :param build_dir_path: Tmp build dir
        :return:
        """

        old_cwd = os.getcwd()

        try:
            shutil.rmtree(build_dir_path)
        except FileNotFoundError:
            pass

        if branch_name:
            os.chdir(source_code_path)
            StaticMethods.checkout_branch(branch_name)

        shutil.copytree(source_code_path, build_dir_path)
        os.chdir(build_dir_path)

        try:
            command = f"{sys.executable} setup.py sdist bdist_wheel"
            response = StaticMethods.execute(command)
        finally:
            os.chdir(old_cwd)

        return response

    @staticmethod
    def execute(command, ignore_on_error_callback=None, timeout=60 * 10, debug=True):
        """
        Execute command in OS.

        :param command:
        :param ignore_on_error_callback:
        :param timeout:
        :param debug:
        :return:
        """

        if "win" in sys.platform.lower():
            return StaticMethods.run_bat(command,
                                         ignore_on_error_callback=ignore_on_error_callback,
                                         timeout=timeout,
                                         debug=debug)

        return StaticMethods.run_bash(command, ignore_on_error_callback=ignore_on_error_callback, timeout=timeout,
                                      debug=debug)

    @staticmethod
    def run_raw(command, file_name, ignore_on_error_callback=None, timeout=60 * 10, debug=True):
        """
        Run bash command, return stdout, stderr and return code.
        Timeout is used fot stuck commands - for example if the command expects for user input.
        Like dpkg installation approve - happens all the time with logstash package.

        @param timeout: In seconds. Default 10 minutes
        @param debug: print return code, stdout and stderr
        @param command:
        @param ignore_on_error_callback:
        @param file_name:
        @return:
        """

        StaticMethods.logger.info(f"run raw: {command}")

        try:
            ret = subprocess.run(
                [command], capture_output=True, shell=True, timeout=timeout, check=False
            )
        except subprocess.TimeoutExpired as error:
            return_dict = {
                "stdout": "",
                "stderr": "TimeoutExpired: " + repr(error),
                "code": 1,
            }
            raise RuntimeError(json.dumps(return_dict)) from error

        os.remove(file_name)
        return_dict = {
            "stdout": ret.stdout.decode().strip("\n"),
            "stderr": ret.stderr.decode().strip("\n"),
            "code": ret.returncode,
        }
        if debug:
            StaticMethods.logger.info(f"return_code:{return_dict['code']}")

            stdout_log = "stdout:\n" + str(return_dict["stdout"])
            for line in stdout_log.split("\n"):
                StaticMethods.logger.info(line)

            error_str = str(return_dict["stderr"])
            if error_str:
                stderr_log = "stderr:\n" + error_str
                for line in stderr_log.split("\n"):
                    StaticMethods.logger.info(line)

        if ret.returncode != 0:
            if ignore_on_error_callback is None:
                raise RuntimeError(json.dumps(return_dict))

            if not ignore_on_error_callback(return_dict):
                raise RuntimeError(json.dumps(return_dict))

        return return_dict

    @staticmethod
    def run_bash(command, ignore_on_error_callback=None, timeout=60 * 10, debug=True):
        """
        Generate file and run it.

        :param command:
        :param ignore_on_error_callback:
        :param timeout:
        :param debug:
        :return:
        """

        file_name = f"tmp-{str(uuid.uuid4())}.sh"
        with open(file_name, "w", encoding="utf-8") as file_handler:
            file_handler.write(command)
            command = f"/bin/bash {file_name}"

        return StaticMethods.run_raw(command, file_name,
                                     ignore_on_error_callback=ignore_on_error_callback,
                                     timeout=timeout,
                                     debug=debug)

    @staticmethod
    def run_bat(command, ignore_on_error_callback=None, timeout=60 * 10, debug=True):
        """
        Generate file and run it.

        :param command:
        :param ignore_on_error_callback:
        :param timeout:
        :param debug:
        :return:
        """

        file_name = f"tmp-{str(uuid.uuid4())}.bat"
        with open(file_name, "w", encoding="utf-8") as file_handler:
            file_handler.write("@echo off\r\n" + command)
            new_command = file_name
        breakpoint()
        return StaticMethods.run_raw(new_command, file_name,
                                     ignore_on_error_callback=ignore_on_error_callback,
                                     timeout=timeout,
                                     debug=debug)

    @staticmethod
    def checkout_branch(branch_name):
        """
        Checkout branch.

        :param branch_name:
        :return:
        """

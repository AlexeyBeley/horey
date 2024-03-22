"""
Methods which can be used without package installation.
"""
import contextlib
import json
import os
import uuid
import subprocess
import sys
import shutil
import platform


from requirement import Requirement
from package import Package


class StandaloneMethods:
    """
    Static methods, can be used both from package and directly.
    """

    INSTALLED_PACKAGES = None

    logger = None

    def generate_python_interpreter_command(self):
        """
        Consider venv and OS.

        :return: 
        """

        if self.venv_dir_path is not None:
            if platform.system().lower() != "windows":
                command = f"source {os.path.join(self.venv_dir_path, 'bin/activate')} && python"
            else:
                command = f'{os.path.join(self.venv_dir_path, "Scripts", "activate")} && "python"'
        else:
            command = sys.executable if platform.system().lower() != "windows" else f'"{sys.executable}"'

        return command

    def __init__(self, venv_dir_path, multi_package_repo_to_prefix_map):
        self.multi_package_repo_to_prefix_map = multi_package_repo_to_prefix_map
        self.venv_dir_path = venv_dir_path
        self.python_interpreter_command = self.generate_python_interpreter_command()

    def init_requirements_raw(self, requirements_file_path):
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
            self.logger.info(f"Initializing requirement '{line}' from file '{requirements_file_path}'")
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

    def compose_requirements_recursive(self, requirements_file_path, requirements_aggregator):
        """
        Compose requirements based on multi package repos map.

        :param requirements_aggregator:
        :param requirements_file_path:
        :return:
        """

        requirements = self.init_requirements_raw(requirements_file_path)
        for requirement in requirements:
            if requirement.name in requirements_aggregator:
                self.update_existing_requirement(requirement, requirements_aggregator)
                continue

            requirements_aggregator[requirement.name] = requirement

            for prefix, repo_path in self.multi_package_repo_to_prefix_map.items():
                if requirement.name.startswith(prefix):
                    package_dir_name = requirement.name.split(".")[-1]
                    multi_package_repo_requirements_file_path = os.path.join(
                        repo_path, package_dir_name, "requirements.txt"
                    )
                    self.compose_requirements_recursive(
                        multi_package_repo_requirements_file_path, requirements_aggregator,
                    )
                    break
            else:
                requirements_aggregator[requirement.name] = requirement

    # pylint: disable= too-many-branches
    def update_existing_requirement(self, requirement: Requirement, requirements_aggregator: dict):
        """
        Update with new requirements.

        """

        error_requirement = f"requirement.name: {requirement.name}"

        current = requirements_aggregator[requirement.name]
        common_min_requirement = self.get_common_min_requirement(current, requirement)
        common_max_requirement = self.get_common_max_requirement(current, requirement)
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

    def install_requirements(self,
            requirements_file_path, update=False, update_from_source=False
    ):
        """
        Prepare list of requirements to be installed and install those missing.

        :param requirements_file_path:
        :return:
        """

        self.logger.info(f"Installing requirements from file: '{requirements_file_path}'")
        requirements_aggregator = {}
        self.compose_requirements_recursive(requirements_file_path, requirements_aggregator)
        if not requirements_aggregator:
            return
        installed_packages = self.get_installed_packages()

        for requirement in reversed(requirements_aggregator.values()):
            if not self.requirement_satisfied(requirement, installed_packages):
                self.install_requirement(requirement)
                continue

            if update:
                self.install_requirement(requirement)
                continue

            if update_from_source:
                for prefix in self.multi_package_repo_to_prefix_map:
                    if requirement.name.startswith(prefix):
                        self.install_requirement(requirement)
                        break

    def get_installed_packages(self):
        """
        Initialize packages with their repo paths and versions

        :return:
        """
        if self.INSTALLED_PACKAGES:
            return self.INSTALLED_PACKAGES

        response = self.execute(f"{self.python_interpreter_command} -m pip list --format json")
        lst_packages = json.loads(response["stdout"])

        objects = []
        for dict_package in lst_packages:
            package = Package(dict_package)
            objects.append(package)
            for prefix, repo_path in self.multi_package_repo_to_prefix_map.items():
                if package.name.startswith(prefix):
                    package.multi_package_repo_prefix = prefix
                    package.multi_package_repo_path = repo_path

        self.INSTALLED_PACKAGES = objects
        return self.INSTALLED_PACKAGES

    def install_requirement(self, requirement: Requirement):
        """
        Install single requirement.

        :param requirement:
        :return:
        """

        for prefix, repo_path in self.multi_package_repo_to_prefix_map.items():
            if requirement.name.startswith(prefix):
                requirement.multi_package_repo_prefix = prefix
                requirement.multi_package_repo_path = repo_path
                return self.install_multi_package_repo_requirement(requirement)

        return self.install_requirement_standard(requirement)

    def install_requirement_standard(self, requirement, force_reinstall=False, name=None):
        """
        Default pip install

        :param name:
        :param force_reinstall:
        :param requirement:
        :return:
        """

        requirement_name = name or requirement.name
        packages = self.get_installed_packages()
        for package in packages:
            if package.name == requirement_name and not force_reinstall:
                return True

        self.INSTALLED_PACKAGES = None
        requirement_string = name or requirement.generate_install_string()
        ret = self.execute(
        f"{self.python_interpreter_command} -m pip install --force-reinstall {requirement_string}")
        last_line = ret.get("stdout").strip("\r\n").split("\n")[-1]
        if "Successfully installed" not in last_line or requirement_name not in last_line:
            raise ValueError(ret)
        return True

    def install_multi_package_repo_requirement(self, requirement):
        """
        Build package and install it.

        :param requirement:
        :return:
        """

        package_dir_name = requirement.name.split(".")[-1]
        return self.build_and_install_package(requirement.multi_package_repo_path, package_dir_name)

    def build_and_install_package(self, multi_package_repo_path, package_dir_name):
        """
        Build the wheel and install it.

        :param multi_package_repo_path:
        :param package_dir_name:
        :return:
        """

        tmp_build_dir = os.path.join(multi_package_repo_path, "build", "_build")
        os.makedirs(tmp_build_dir, exist_ok=True)

        build_dir_path = os.path.join(tmp_build_dir, package_dir_name)
        self.create_wheel(os.path.join(multi_package_repo_path, package_dir_name), build_dir_path)
        wheel_file_name = None
        dist_dir_path = os.path.join(build_dir_path, "dist")
        for wheel_file_name in os.listdir(dist_dir_path):
            if wheel_file_name.endswith(".whl"):
                break

        command = f"{self.python_interpreter_command} -m pip install --force-reinstall {os.path.join(dist_dir_path, wheel_file_name)}"
        response = self.execute(command)

        lines = response["stdout"].split("\n")
        index = -2 if "Leaving directory" in lines[-1] else -1
        if lines[index] != f"done installing {package_dir_name}" and "Successfully installed " not in lines[index]:
            raise RuntimeError(
                f"Could not install {package_dir_name} from source code:\n {response}"
            )
        self.INSTALLED_PACKAGES = None
        return True

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

    def create_wheel(self, source_code_path, build_dir_path, branch_name=None):
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
            self.checkout_branch(branch_name)

        shutil.copytree(source_code_path, build_dir_path)
        os.chdir(build_dir_path)

        try:
            command = f"{self.python_interpreter_command} setup.py sdist bdist_wheel"
            response = self.execute(command)
        finally:
            os.chdir(old_cwd)

        return response

    def execute(self, command, ignore_on_error_callback=None, timeout=60 * 10, debug=True):
        """
        Execute command in OS.

        :param command:
        :param ignore_on_error_callback:
        :param timeout:
        :param debug:
        :return:
        """

        if platform.system().lower() == "windows":
            return self.run_bat(command,
                                         ignore_on_error_callback=ignore_on_error_callback,
                                         timeout=timeout,
                                         debug=debug)

        return self.run_bash(command, ignore_on_error_callback=ignore_on_error_callback, timeout=timeout,
                                      debug=debug)

    # pylint: disable= too-many-arguments

    def run_raw(self, command, file_name, ignore_on_error_callback=None, timeout=60 * 10, debug=True):
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

        self.logger.info(f"run raw: {command}")
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
            self.logger.info(f"return_code:{return_dict['code']}")

            stdout_log = "stdout:\n" + str(return_dict["stdout"])
            for line in stdout_log.split("\n"):
                self.logger.info(line)

            error_str = str(return_dict["stderr"])
            if error_str:
                stderr_log = "stderr:\n" + error_str
                for line in stderr_log.split("\n"):
                    self.logger.info(line)

        if ret.returncode != 0:
            if ignore_on_error_callback is None:
                raise RuntimeError(json.dumps(return_dict))

            if not ignore_on_error_callback(return_dict):
                raise RuntimeError(json.dumps(return_dict))

        return return_dict

    def run_bash(self, command, ignore_on_error_callback=None, timeout=60 * 10, debug=True):
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

        return self.run_raw(command, file_name,
                                     ignore_on_error_callback=ignore_on_error_callback,
                                     timeout=timeout,
                                     debug=debug)

    def run_bat(self, command, ignore_on_error_callback=None, timeout=60 * 10, debug=True):
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
        return self.run_raw(new_command, file_name,
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

    @contextlib.contextmanager
    def tmp_file(self, file_path, flags="w"):
        """
        Create tmp file.

        :param file_path:
        :param flags:
        :return:
        """
        with open(file_path, flags) as file_handler:
            yield file_handler
        os.remove(file_path)

    def download_https_file_requests(self, local_file_path, url):
        """
        Download file from url.
        Why should I use two methods and import requests in the middle of the script?
        Because Microsoft is SHIT, that is why. It fails on SSL validation.

        Shamelessly stolen from: https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests

        :param local_file_path:
        :param url:
        :return:
        """
        with self.tmp_file("requests_doenloader.py", flags="wb") as file_handler:
            file_handler.write(
         """
        import requests
        with requests.get(url, stream=True, timeout=180) as r:
            r.raise_for_status()
            with open(local_file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        """)
            breakpoint()

        return local_file_path
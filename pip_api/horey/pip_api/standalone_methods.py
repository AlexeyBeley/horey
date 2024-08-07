"""
Methods which can be used without package installation.
"""
import importlib
import json
import os
import uuid
import subprocess
import sys
import shutil
import platform


this_dir_name = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, this_dir_name)
from requirement import Requirement
from package import Package
pop_value = sys.path.pop(0)
if pop_value != this_dir_name:
    raise ValueError(f"{pop_value} should be {this_dir_name}")


class StandaloneMethods:
    """
    Static methods, can be used both from package and directly.
    """

    INSTALLED_PACKAGES = None
    SOURCE_CODE_PACKAGE_VERSIONS = {}

    logger = None

    @staticmethod
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
                line.strip("\n") for line in file_handler.readlines() if line != "\n" and not line.startswith("#")
            ]

        for line in lines:
            self.logger.info(f"Initializing requirement '{line}' from file '{requirements_file_path}'")
            requirements.append(self.init_requirement_from_string(requirements_file_path, line))

        return requirements

    def init_requirement_from_string(self, src_file_path, str_src):
        """
        Init from standard requirement string.

        :param src_file_path:
        :param str_src:
        :return:
        """

        requirement = Requirement(src_file_path, str_src)
        for prefix, repo_path in self.multi_package_repo_to_prefix_map.items():
            if requirement.name.startswith(prefix):
                requirement.multi_package_repo_prefix = prefix
                requirement.multi_package_repo_path = repo_path
                break
        return requirement

    @staticmethod
    def get_requirements_file_path(repo_path, package_name):
        """
        Multipackage repo packages requirements.txt

        :param repo_path:
        :param package_name:
        :return:
        """

        return os.path.join(repo_path, package_name, "requirements.txt")

    def compose_requirements_recursive_from_file(self, requirements_file_path, requirements_aggregator):
        """
        Compose requirements based on multi package repos map.

        :param requirements_aggregator:
        :param requirements_file_path:
        :return:
        """

        requirements = self.init_requirements_raw(requirements_file_path)
        self.compose_requirements_recursive(requirements, requirements_aggregator)

    def compose_requirements_recursive(self, requirements, requirements_aggregator):
        """
        Standard and multi-package source requirements

        :param requirements:
        :param requirements_aggregator:
        :return:
        """

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
                    self.compose_requirements_recursive_from_file(
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

    def install_source_code_requirement(self, requirement):
        """
        Prepare list of requirements to be installed and install those missing.

        :param requirement:
        :return:
        """

        self.logger.info(f"install_source_code_requirement '{requirement.name}'")

        requirements_file_path = os.path.join(requirement.multi_package_repo_path, requirement.name[len(requirement.multi_package_repo_prefix):], "requirements.txt")
        self.logger.info(f"Installing requirements from file: '{requirements_file_path}'")
        requirements_aggregator = {requirement.name: requirement}
        self.compose_requirements_recursive_from_file(requirements_file_path, requirements_aggregator)
        self.logger.info(f"Aggregated: {requirements_aggregator}")
        self.init_source_code_metadata(requirements_aggregator)
        all_reversed = list(reversed(requirements_aggregator.values()))
        for aggregated_requirement in all_reversed[:-1]:
            if aggregated_requirement.multi_package_repo_path:
                self.install_source_code_requirement_raw(aggregated_requirement)
            else:
                self.install_requirement_standard(aggregated_requirement)

        self.install_source_code_requirement_raw(requirement)

        return True

    def init_source_code_metadata(self, requirements_aggregator):
        """
        Init versions from source code.
        Init per package pip api configuration.

        :param requirements_aggregator:
        :return:
        """

        for requirement_name, requirement in requirements_aggregator.items():
            self.logger.info(f"Looking source version code for {requirement_name}")
            for prefix in self.multi_package_repo_to_prefix_map:
                if requirement_name.startswith(prefix):
                    version = self.init_source_code_version(self.multi_package_repo_to_prefix_map.get(prefix), requirement_name, prefix)
                    package_pip_api_config = self.init_package_pip_api_configuration(self.multi_package_repo_to_prefix_map.get(prefix), requirement_name)
                    if package_pip_api_config:
                        requirement.force = package_pip_api_config.get("force") or requirement.force

                    self.logger.info(f"{requirement_name} source code version initialized: {version}")

                    if not version:
                        raise ValueError(f"Uninitialized {version=}")
                    StandaloneMethods.SOURCE_CODE_PACKAGE_VERSIONS[requirement_name] = version

    def init_package_pip_api_configuration(self, multi_package_repo_path: str, requirement_name: str):
        """
        Init per package configuration.

        :param multi_package_repo_path:
        :param requirement_name:
        :return:
        """

        repo_pip_api_config_file = os.path.join(multi_package_repo_path, "pip_api_configuration.py")
        module = self.load_module(repo_pip_api_config_file)
        if not hasattr(module, "main"):
            raise NotImplementedError(f"No 'main' in {repo_pip_api_config_file}")
        repo_pip_api_configs = module.main()
        for prefix in repo_pip_api_configs.multi_package_repositories.keys():
            if requirement_name.startswith(prefix):
                break
        else:
            raise ValueError(f"Was unable to find proper prefix in multipackage repo pip api configuration file: '{multi_package_repo_path}' ")

        if requirement_name.count(prefix) != 1:
            raise ValueError(f"{requirement_name=} {requirement_name.count(prefix)=} in {multi_package_repo_path=}")

        package_dir_name = requirement_name.replace(prefix, "").split(".")[0]
        package_pip_api_config_file = os.path.join(multi_package_repo_path, package_dir_name, "pip_api_package_config.py")
        if os.path.exists(package_pip_api_config_file):
            module = self.load_module(package_pip_api_config_file)
            if hasattr(module, "main"):
                raise NotImplementedError(f"No 'main' in {package_pip_api_config_file}")
            return {key: value for key, value in module.__dict__.items() if not key.startswith("_")}
        return None

    @staticmethod
    def init_source_code_version(path_to_repo, requirement_name, prefix):
        """
        Fetch the version:

        :param prefix:
        :param path_to_repo:
        :param requirement_name:
        :return:
        """

        package_root_folder_name = requirement_name[len(prefix):]
        package_main_folder_path = os.path.join(path_to_repo, package_root_folder_name)
        if not os.path.exists(package_main_folder_path):
            raise ValueError(f"Package folder with name '{package_root_folder_name}' does not exist in {path_to_repo}")

        module_path = os.path.abspath(os.path.join(package_main_folder_path, requirement_name.replace(".", "/"), "__init__.py"))

        if not os.path.exists(module_path):
            raise ValueError(f"__init__.py module does not exist '{module_path}'")
        with open(module_path, encoding="utf-8") as file_handler:
            lines = file_handler.readlines()

        for line in lines:
            line = line.strip("\n")
            if line.strip(" ").startswith("__version__"):
                break
        else:
            raise RuntimeError(f"Can not find version line in {module_path}")

        _, version_value = line.split("=")
        version_value = version_value.strip(" ").strip('"').strip("'")
        for x in version_value.split("."):
            if not x.isdigit():
                raise ValueError(f"Version from {line=} in {module_path}")
        return version_value

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
            self.logger.info(f"Existing package '{package.name=}'")
            objects.append(package)
            for prefix, repo_path in self.multi_package_repo_to_prefix_map.items():
                if package.name.startswith(prefix):
                    package.multi_package_repo_prefix = prefix
                    package.multi_package_repo_path = repo_path

        self.INSTALLED_PACKAGES = objects
        return self.INSTALLED_PACKAGES

    def install_requirements_from_file(self, src_file_path, force_reinstall=False):
        """
        For example requirements.txt

        :param src_file_path:
        :param force_reinstall:
        :return:
        """

        with open(src_file_path, encoding="utf-8") as file_handler:
            lines = file_handler.readlines()

        for line in lines:
            self.install_requirement_from_string(src_file_path, line.strip("\n"), force_reinstall=force_reinstall)

    def install_requirement_from_string(self, src_file_path, str_src, force_reinstall=False):
        """
        Entrypoint.

        :param src_file_path: Requirement source file
        :param str_src: line to initialize
        :param force_reinstall:
        :return:
        """
        self.logger.info(f"install_requirement_from_string {src_file_path}, {str_src}")
        requirement = self.init_requirement_from_string(src_file_path, str_src)
        requirement.force = force_reinstall
        return self.install_requirement(requirement)

    def install_requirement(self, requirement: Requirement):
        """
        Install single requirement.

        :param requirement:
        :return:
        """

        if requirement.multi_package_repo_path:
            return self.install_source_code_requirement(requirement)

        return self.install_requirement_standard(requirement)

    def install_requirement_standard(self, requirement):
        """
        Default pip install

        :param requirement:
        :return:
        """
        if self.requirement_satisfied(requirement) and not requirement.force:
            return True
        self.INSTALLED_PACKAGES = None
        requirement_string = requirement.generate_install_string()
        if ">" in requirement_string:
            requirement_string = requirement_string.replace(">", r"\>")
        if "<" in requirement_string:
            requirement_string = requirement_string.replace("<", r"\<")

        ret = self.execute(
            f"{self.python_interpreter_command} -m pip install --force-reinstall {requirement_string}")

        last_line = ret.get("stdout").strip("\r\n").split("\n")[-1]
        if ret.get("stdout") and ("Successfully installed" not in last_line or requirement.name not in last_line):
            raise ValueError(ret)
        return True

    def install_source_code_requirement_raw(self, requirement):
        """
        Build package and install it.

        :param requirement:
        :return:
        """

        requirement_setup_tools = Requirement("horey_auto_generated", "setuptools")
        requirement_setup_tools.force = False
        self.install_requirement_standard(requirement_setup_tools)

        if requirement.force or not self.requirement_satisfied(requirement):
            package_lower_dir_name = requirement.name.split(".")[-1]
            package_upper_dir_name = requirement.name.split(".")[0]
            self.build_and_install_package(requirement.multi_package_repo_path, package_upper_dir_name, package_lower_dir_name)
            self.INSTALLED_PACKAGES = None

    def build_and_install_package(self, multi_package_repo_path, package_upper_dir_name, package_lower_dir_name):
        """
        Build the wheel and install it.

        :param multi_package_repo_path:
        :param package_upper_dir_name: in horey.h_logger is horey
        :param package_lower_dir_name: in horey.h_logger h_logger
        :return:
        """
        self.logger.info(f"Building and installing package from source code {multi_package_repo_path} -> {package_lower_dir_name}")

        tmp_build_dir = os.path.join(multi_package_repo_path, "build", "_build")
        os.makedirs(tmp_build_dir, exist_ok=True)

        build_dir_path = os.path.join(tmp_build_dir, package_lower_dir_name)

        self.create_wheel(os.path.join(multi_package_repo_path, package_lower_dir_name), package_upper_dir_name, build_dir_path)
        wheel_file_name = None
        dist_dir_path = os.path.join(build_dir_path, "dist")
        for wheel_file_name in os.listdir(dist_dir_path):
            if wheel_file_name.endswith(".whl"):
                break

        command = f"{self.python_interpreter_command} -m pip install --force-reinstall {os.path.join(dist_dir_path, wheel_file_name)}"
        response = self.execute(command)

        lines = response["stdout"].split("\n")
        index = -2 if "Leaving directory" in lines[-1] else -1
        if lines[index] != f"done installing {package_upper_dir_name}" and "Successfully installed " not in lines[index]:
            raise RuntimeError(
                f"Could not install {package_upper_dir_name} from source code:\n {response}"
            )
        self.INSTALLED_PACKAGES = None
        return True

    def requirement_satisfied(self, requirement: Requirement):
        """
        Check weather the requirement is already installed.

        :param requirement:
        :return:
        """
        self.logger.info(f"Checking if requirement satisfied '{requirement.name}'")
        self.logger.info(f"self.SOURCE_CODE_PACKAGE_VERSIONS: '{self.SOURCE_CODE_PACKAGE_VERSIONS}'")

        for package in self.get_installed_packages():
            if package.name.lower().replace("_", "-") != requirement.name.lower().replace("_", "-"):
                continue
            self.logger.info(f"Found installed '{package.name=}'")

            if not package.check_version_requirements(requirement):
                self.logger.info(f"Installed version do not much requirement '{package.name=}'")
                return False

            for source_code_package_name, source_code_version in self.SOURCE_CODE_PACKAGE_VERSIONS.items():
                if package.name == source_code_package_name:
                    self.logger.info(f"Comparing installed '{package.name}' package version '{package.version}' VS source code version {source_code_version}")
                    return package.version == source_code_version
            return True

        self.logger.info(f"Was not able to find installed package for requirement '{requirement.name=}'")
        return False

    def create_wheel(self, source_code_path, package_upper_dir_name, build_dir_path, branch_name=None):
        """
        Create wheel.

        :param package_upper_dir_name: The dir containing actual source code needed in the package.
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

        shutil.copytree(os.path.join(source_code_path, package_upper_dir_name), os.path.join(build_dir_path, package_upper_dir_name))
        for file_name in ["LICENSE", "README.md", "setup.py"]:
            shutil.copy(os.path.join(source_code_path, file_name), build_dir_path)
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

        StandaloneMethods.logger.info(f"Executing OS command: '{command}'")

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

        self.logger.info(f"Running bash: '{command}'")
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

        tmp_file_name = "requests_downloader.py"

        try:
            with open(tmp_file_name, "w", encoding="utf-8") as file_handler:
                file_handler.write("\n".join([
                    "import requests",
                    f"with requests.get('{url}', stream=True, timeout=180) as r:",
                    "    r.raise_for_status()",
                    f"    with open('{local_file_path}', 'wb') as f:",
                    "        for chunk in r.iter_content(chunk_size=8192):",
                    "            f.write(chunk)"
                ]))

            self.execute(f"{self.python_interpreter_command} {tmp_file_name}")
        finally:
            os.remove(tmp_file_name)

        return local_file_path

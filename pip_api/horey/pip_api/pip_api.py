"""
PIP API module.

"""

import sys
import os
import shutil

from horey.h_logger import get_logger
from horey.pip_api.requirement import Requirement
from horey.pip_api.pip_api_configuration_policy import PipAPIConfigurationPolicy
from horey.common_utils.common_utils import CommonUtils
from horey.common_utils.bash_executor import BashExecutor
from horey.pip_api.standalone_methods import StandaloneMethods

logger = get_logger()
StandaloneMethods.logger = logger


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
        self.standalone_methods = StandaloneMethods(self.configuration.venv_dir_path, self.configuration.multi_package_repositories)

    def init_configuration(self):
        """
        Init multi package repositories data.

        :return:
        """

        if self.configuration is None:
            return

        if self.configuration.multi_package_repositories is not None:
            for repo_path in self.configuration.multi_package_repositories.values():
                self.init_multi_package_repository(repo_path)

        if self.configuration.venv_dir_path is not None:
            self.install_venv()

    def install_venv(self):
        """
        Install venv if does not exist

        :return:
        """
        logger.info(f"Installing Venv if needed: {self.configuration.venv_dir_path}")
        if not os.path.exists(
                os.path.join(self.configuration.venv_dir_path, "bin", "activate")
            ):
            logger.info(f"Installing new Venv: {self.configuration.venv_dir_path}")
            options = ""
            if self.configuration.system_site_packages:
                options += " --system-site-packages"

            self.run_bash(
                f"{sys.executable} -m venv {self.configuration.venv_dir_path}{options}"
            )

            self.execute("python -m pip install --upgrade pip")
            self.execute("python -m pip install --upgrade setuptools>=45")
            self.execute("python -m pip install -U packaging>=24.2")
            self.execute("python -m pip install wheel")

    def install_venv_old(self):
        """
        Install venv if does not exist

        :return:
        """
        logger.info(f"Installing Venv if needed: {self.configuration.venv_dir_path}")
        if not os.path.exists(
                os.path.join(self.configuration.venv_dir_path, "bin", "activate")
        ):
            self.run_bash(
                f"{sys.executable} -m venv {self.configuration.venv_dir_path} --system-site-packages",
            )

            self.execute("python -m pip install --upgrade pip")
            self.execute("python -m pip install --upgrade setuptools>=45")
            self.execute("python -m pip install -U packaging>=24.2")
            self.execute("python -m pip install wheel")
        else:
            logger.info(f"Installing Venv ignore. Venv already exists: {self.configuration.venv_dir_path}")

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
        response = self.execute(f"{self.get_python_interpreter_command()} -m pip list --format json")

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
        :return:
        """

        self.packages = self.standalone_methods.get_installed_packages()
        return self.packages

    class BashError(RuntimeError):
        """
        Failed to run bash

        """

    @staticmethod
    def run_bash(command, ignore_on_error_callback=None, timeout=60 * 10, debug=True):
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
        return BashExecutor.run_bash(command, ignore_on_error_callback=ignore_on_error_callback, timeout=timeout, debug=debug,
                              logger=logger)

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
            self.install_venv()
            venv_bin_dir = os.path.join(self.configuration.venv_dir_path, 'bin')
            command = f"source {os.path.join(venv_bin_dir, 'activate')} && {command}"
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

    def install_requirements_from_file(self, file_path, force_reinstall=False):
        """
        File like requirements.txt.

        :param file_path:
        :param force_reinstall:
        :return:
        """

        self.standalone_methods.install_requirements_from_file(file_path, force_reinstall=force_reinstall)

    def install_requirement_from_string(self, file_path, str_src, force_reinstall=False):
        """
        Install string from requirements.txt file format.

        :param file_path:
        :param str_src:
        :param force_reinstall:
        :return:
        """

        self.standalone_methods.install_requirement_from_string(file_path, str_src, force_reinstall=force_reinstall)

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

        return self.execute(f"{self.get_python_interpreter_command()} -m pip install --force-reinstall {requirement.generate_install_string()}")

    def get_python_interpreter_command(self):
        """
        Generate "python" command depends on whether running in venv.

        :return:
        """

        if self.configuration is not None and self.configuration.venv_dir_path is not None:
            return "python"

        return sys.executable

    def install_multi_package_repo_requirement(self, requirement):
        """
        Build package and install it.

        :param requirement:
        :return:
        """

        package_dirname = requirement.name.split(".")[-1]
        ret = self.execute(
            f"cd {requirement.multi_package_repo_path} && make raw_install_wheel-{package_dirname}"
        )
        lines = ret.split("\n")

        index = -2 if "Leaving directory" in lines[-1] else -1
        if lines[index] != f"done installing {package_dirname}" and "Successfully installed" not in lines[index]:
            raise RuntimeError(
                f"Could not install {package_dirname} from source code:\n {ret}"
            )

    def requirement_satisfied(self, requirement: Requirement):
        """
        Check weather the requirement is already installed.
        for package in self.packages:
            if package.name.replace("_", "-") != requirement.name.replace("_", "-"):
                continue
            return package.check_version_requirements(requirement)

        return False
        :param requirement:
        :return:
        """

        return self.standalone_methods.requirement_satisfied(requirement)

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

    def init_requirements_raw(self, requirements_file_path):
        """
        Init requirements from single file.
        if not os.path.exists(requirements_file_path):
            return []

        requirements = []

        with open(requirements_file_path, "r", encoding="utf-8") as file_handler:
            lines = [
                line.strip("\n") for line in file_handler.readlines() if line != "\n"
            ]

        for line in lines:
            logger.info(f"Initializing requirement '{line}' from file '{requirements_file_path}'")
            requirements.append(Requirement(requirements_file_path, line))

        return requirements
        :param requirements_file_path:
        :return:
        """

        return self.standalone_methods.init_requirements_raw(requirements_file_path)

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
            raise NotImplementedError(f"Requirement for '{this.name}' in {os.path.abspath(this.requirements_file_path)}:{lst_this} vs {os.path.abspath(other.requirements_file_path)}:{lst_other}")
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

    # pylint: disable= too-many-branches
    def update_existing_requirement(self, requirement: Requirement):
        """
        Update with new requirements.

        """

        error_requirement = f"requirement.name: {requirement.name}"

        current = self.REQUIREMENTS[requirement.name]
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
                raise RuntimeError(f"current.min_version: {current.min_version}, current.include_min: {current.include_min}")
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

    def get_horey_package_requirements(self, package_name):
        """

        :param package_name:
        :return:
        _, package_name = package_name.split(".")
        horey_package_requirements_path = os.path.join(self.horey_repo_path, package_name, "requirements.txt")
        return self.init_requirements_raw(horey_package_requirements_path)
        """
        raise NotImplementedError("Old code.")

    def create_wheel(self, setup_dir_path, build_dir_path, branch_name=None):
        """
        Create wheel.

        :param setup_dir_path: Path to the directory with setup.py
        :param build_dir_path: Tmp build dir
        :return:
        """

        old_cwd = os.getcwd()

        try:
            shutil.rmtree(build_dir_path)
        except FileNotFoundError:
            pass

        if branch_name:
            os.chdir(setup_dir_path)
            self.checkout_branch(branch_name)

        shutil.copytree(setup_dir_path, build_dir_path)
        os.chdir(build_dir_path)

        try:
            command = f"{sys.executable} setup.py sdist bdist_wheel;"
            self.run_bash(command, debug=True)
        finally:
            os.chdir(old_cwd)

        return os.path.join(build_dir_path, "dist")

    def checkout_branch(self, branch_name):
        """
        Checkout remote branch.

        :param branch_name:
        :return:
        """

        self.run_bash(f"chmod 400 {self.configuration.git_ssh_key_file_path}")
        script = f"eval `ssh-agent -s` && ssh-add {self.configuration.git_ssh_key_file_path} && git fetch"
        self.run_bash(script)
        ret = self.run_bash("git branch")
        branches = ret["stdout"].replace(" ", "").split()
        if "*main" in branches or "main" in branches:
            main_branch = "main"
        elif "*master" in branches or "master" in branches:
            main_branch = "master"
        else:
            raise RuntimeError(f"Can not find main/master branch in {branches}")

        self.run_bash(f"git checkout {main_branch}")
        self.run_bash(f"git branch -D {branch_name}",
                      ignore_on_error_callback=lambda return_dict: f"error: branch '{branch_name}' not found." in return_dict["stderr"])
        self.run_bash(f"git checkout origin/{branch_name}")

    def upload(self, username, password, repo_url, dist_path):
        """
        Upload package to pypi repo

        :param username:
        :param password:
        :param repo_url:
        :param dist_path:
        :return:
        """

        command = f"{sys.executable} -m twine upload -u {username} -p {password} --repository-url {repo_url} {dist_path}/*"
        self.run_bash(command, debug=True)

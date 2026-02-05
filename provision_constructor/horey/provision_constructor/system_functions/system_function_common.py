"""
Common functionality to all system_functions.

"""
# pylint: disable=too-many-lines
import json
import shutil
import datetime
import os
import argparse
import subprocess
import time
from pathlib import Path

from horey.common_utils.actions_manager import ActionsManager
from horey.replacement_engine.replacement_engine import ReplacementEngine

from horey.common_utils.storage_service import StorageService
from horey.provision_constructor.system_functions.apt_package import APTPackage
from horey.provision_constructor.system_functions.apt_repository import APTRepository
from horey.h_logger import get_logger
from horey.common_utils.bash_executor import BashExecutor
from horey.common_utils.remoter import Remoter

logger = get_logger()
BashExecutor.set_logger(logger, override=False)


class SystemFunctionCommon:
    """
    Common functionality to all system_functions.

    """

    ACTION_MANAGER = ActionsManager()
    APT_PACKAGES = []
    APT_REPOSITORIES = []
    APT_PACKAGES_UPDATED = False
    PIP_PACKAGES = []

    def __init__(self, deployment_dir, force, upgrade, **kwargs):
        self.action = kwargs.get("action")
        try:
            self.storage_service: StorageService = kwargs.pop("storage_service")
        except KeyError:
            self.storage_service = None

        self.deployment_dir = deployment_dir
        self.kwargs = kwargs
        self.validate_provisioned_ancestor = True
        self.venv_path = None
        self.force = force
        self.upgrade = upgrade
        self.remoter: Remoter = None

    @classmethod
    def get_system_function_name(cls):
        """
        Find the name.

        :return:
        """

        name = cls.__module__[len("horey.provision_constructor.system_functions."):]

        # example: name = 'logstash.provisioner'
        return name[: name.rfind(".")]

    def provision(self):
        """
        Provision logic entrypoint.

        :return:
        """

        if not self.force:
            if self.test_provisioned():
                return

        self._provision()

        self.test_provisioned()

    def add_trigger(self, dst_file_path):
        """
        Check input and add the trigger to file

        :param dst_file_path:
        :return:
        """

        with open(dst_file_path, encoding="utf-8") as file_handler:
            contents = file_handler.read()
        if "provision_constructor=ProvisionConstructor()" not in contents.replace(" ", ""):
            raise ValueError("Expecting 'provision_constructor=ProvisionConstructor()'")

        str_kwargs = ""
        for key, value in self.kwargs.items():
            if isinstance(value, str):
                str_kwargs += f', {key} = "{value}"'
            elif isinstance(value, bool):
                str_kwargs += f', {key} = {value}'
            else:
                raise NotImplementedError(f"Unknown type {type(value)}")
        contents += f'\nprovision_constructor.provision_system_function("{self.get_system_function_name()}", upgrade = {bool(self.upgrade)}, force = {bool(self.force)}{str_kwargs})'
        with open(dst_file_path, "w", encoding="utf-8") as file_handler:
            file_handler.write(contents)

    def test_provisioned(self):
        """
        Test the system_function was provisioned.

        :return:
        """

        raise NotImplementedError("test_provisioned not implemented")

    def _provision(self):
        """
        Each sytem_function implements its _provision.

        :return:
        """

        raise NotImplementedError("_provision not implemented")

    @property
    def activate(self):
        """
        Generate activate venv string.

        @return:
        """

        return f"source {self.venv_path}/bin/activate"

    def init_pip_packages(self):
        """
        Init installed packages.

        @return:
        """

        command = "pip3 freeze"

        if self.venv_path is not None:
            command = self.activate + " && " + command

        ret = SystemFunctionCommon.run_bash(command)
        SystemFunctionCommon.PIP_PACKAGES = ret["stdout"].split("\n")

    def check_pip_installed(self, package_name):
        """
        Check weather the package is installed.

        @param package_name:
        @return:
        """

        if not SystemFunctionCommon.PIP_PACKAGES:
            self.init_pip_packages()

        for pip_package in self.PIP_PACKAGES:
            if package_name in pip_package:
                return True

        return False

    @staticmethod
    def empty_parser():
        """
        Old code.

        @return:
        """
        return argparse.ArgumentParser()

    @staticmethod
    def current_subpath(subpath=None):
        """
        Sub path of this current file + subpath from input.

        @param subpath:
        @return:
        """
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        if subpath is None:
            return cur_dir
        return os.path.join(cur_dir, *(subpath.split("/")))

    @staticmethod
    def run_bash(command, ignore_on_error_callback=None, timeout=60 * 10, debug=True):
        """
        Use bash executor to run the bash command.

        :param command:
        :param ignore_on_error_callback:
        :param timeout:
        :param debug:
        :return:
        """

        return BashExecutor.run_bash(command, ignore_on_error_callback=ignore_on_error_callback, timeout=timeout, debug=debug, logger=logger)

    @staticmethod
    def check_file_contains(file_path, str_content):
        """
        Self explanatory.

        @param file_path:
        @param str_content:
        @return:
        """

        if not os.path.isfile(file_path):
            return False

        with open(file_path, encoding="utf-8") as file_handler:
            file_contents = file_handler.read()

        return str_content in file_contents

    @staticmethod
    def check_files_exist_parser():
        """
        Self explanatory.

        @return:
        """

        description = "Returns true if all files exist"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(
            "--files_paths",
            required=True,
            type=str,
            help="Comma separated string file list",
        )
        return parser

    @staticmethod
    def check_files_exist_action(arguments) -> None:
        """
        Self explanatory.

        @param arguments:
        @return:
        """

        SystemFunctionCommon.check_files_exist(arguments.files_paths.split(","))

    @staticmethod
    def check_files_exist(files_paths, sudo=False) -> bool:
        """
        Self explanatory.

        @param files_paths: [str, str]
        @param sudo:
        @return:
        """

        errors = []
        for file_path in files_paths:
            try:
                SystemFunctionCommon.check_file_exists(file_path, sudo=sudo)
            except SystemFunctionCommon.FailedCheckError as error_handler:
                errors.append(repr(error_handler))

        if errors:
            raise SystemFunctionCommon.FailedCheckError("\n".join(errors))

        return True

    @staticmethod
    def check_file_exists(file_path, sudo=False) -> bool:
        """
        Check file exists.

        @param file_path: str
        @param sudo:
        @return:
        """
        if not sudo:
            if not os.path.exists(file_path):
                raise SystemFunctionCommon.FailedCheckError(f"File '{file_path}' does not exist")
            if not os.path.isfile(file_path):
                raise SystemFunctionCommon.FailedCheckError(f"Path '{file_path}' is not a file")
            return True

        command = f'if sudo test -f "{file_path}"; then echo "true"; else echo "false"; fi'
        ret = SystemFunctionCommon.run_bash(command)
        return SystemFunctionCommon.check_file_exists_output_validator(file_path, ret["stdout"], ret["stderr"])

    @staticmethod
    def check_file_exists_output_validator(file_path, stdout, stderr):
        """
        Validate output
        :param file_path:
        :param stderr:
        :param stdout:
        :return:
        """

        if stdout[-1] == "true":
            return True

        if stdout[-1] == "false":
            raise SystemFunctionCommon.FailedCheckError(f"File '{file_path}' does not exist or is not a file")

        raise RuntimeError(f"Expected true/false, received: {stdout=} {stderr=}")


    @staticmethod
    def remove_file(file_path, sudo=False):
        """
        Delete file.

        :param file_path:
        :param sudo:
        :return:
        """

        try:
            if SystemFunctionCommon.check_file_exists(file_path, sudo=sudo):
                SystemFunctionCommon.run_bash(f"sudo rm -rf {file_path}")
        except SystemFunctionCommon.FailedCheckError:
            pass

        return True

    @staticmethod
    def action_move_file_parser():
        """
        Self explanatory.

        @return:
        """

        description = "move_file from src_path to dst_path"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(
            "--src_file_path", required=True, type=str, help="Source file path"
        )
        parser.add_argument(
            "--dst_file_path", required=True, type=str, help="Destination file path"
        )

        parser.epilog = f"Usage: python {__file__} [options]"
        return parser

    @staticmethod
    def action_move_file(arguments):
        """
        Self explanatory.

        @param arguments:
        @return:
        """

        arguments_dict = vars(arguments)
        SystemFunctionCommon.move_file(**arguments_dict)

    @staticmethod
    def move_file(src_file_path=None, dst_file_path=None):
        """
        Move code using current privileges.

        @param src_file_path:
        @param dst_file_path:
        @return:
        """
        os.makedirs(os.path.dirname(dst_file_path), exist_ok=True)
        shutil.copyfile(src_file_path, dst_file_path)

    def provision_file(self, src_file_path, dst_file_path, sudo=False):
        """
        Self explanatory.

        @param sudo:
        @param src_file_path:
        @param dst_file_path:
        @return:
        """

        if src_file_path.startswith("./"):
            raise DeprecationWarning(f"Use absolute file path: {src_file_path}")

        prefix = "sudo " if sudo else ""
        SystemFunctionCommon.run_bash(
            f"{prefix}mkdir -p {os.path.dirname(dst_file_path)}"
        )
        SystemFunctionCommon.run_bash(f"{prefix}rm -rf {dst_file_path}")
        SystemFunctionCommon.run_bash(f"{prefix}cp {src_file_path} {dst_file_path}")

    # region compare_files
    @staticmethod
    def action_compare_files_parser():
        """
        Self explanatory.

        @return:
        """

        description = "compare_files from src_path to dst_path"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(
            "--src_file_path", required=True, type=str, help="Source file path"
        )
        parser.add_argument(
            "--dst_file_path", required=True, type=str, help="Destination file path"
        )

        parser.epilog = f"Usage: python {__file__} [options]"
        return parser

    @staticmethod
    def action_compare_files(arguments):
        """
        Self explanatory.

        @param arguments:
        @return:
        """

        arguments_dict = vars(arguments)
        SystemFunctionCommon.compare_files(**arguments_dict)

    @staticmethod
    def compare_files(src_file_path=None, dst_file_path=None):
        """
        Compare two files.

        @param src_file_path:
        @param dst_file_path:
        @return:
        """

        with open(src_file_path, encoding="utf-8") as file_handler:
            src_file_string = file_handler.read()

        with open(dst_file_path, encoding="utf-8") as file_handler:
            dst_file_string = file_handler.read()

        if src_file_string == dst_file_string:
            return True

        raise RuntimeError(f"{src_file_path} not equals to {dst_file_path}")

    # endregion

    # region perform_comment_line_replacement
    @staticmethod
    def action_perform_comment_line_replacement_parser():
        """
        Parser.

        @return:
        """

        description = "perform_comment_line_replacement from src_path in dst_path above comment line"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(
            "--src_file_path", required=True, type=str, help="Source file path"
        )
        parser.add_argument(
            "--dst_file_path", required=True, type=str, help="Destination file path"
        )
        parser.add_argument(
            "--comment_line", required=True, type=str, help="Destination file path"
        )

        parser.epilog = f"Usage: python {__file__} [options]"
        return parser

    @staticmethod
    def action_perform_comment_line_replacement(arguments):
        """
        Self explanatory.

        @param arguments:
        @return:
        """

        arguments_dict = vars(arguments)
        SystemFunctionCommon.perform_comment_line_replacement(**arguments_dict)

    @staticmethod
    def perform_comment_line_replacement(
        src_file_path=None, dst_file_path=None, comment_line=None
    ):
        """
        Comment line being replaced with contents of a file.

        @param src_file_path:
        @param dst_file_path:
        @param comment_line:
        @return:
        """

        replacement_engine = ReplacementEngine()
        with open(src_file_path, encoding="utf-8") as file_handler:
            replacement_string = file_handler.read()

        replacement_engine.perform_comment_line_replacement(
            dst_file_path, comment_line, replacement_string, keep_comment=True
        )

    # endregion

    # region check_systemd_service_status
    @staticmethod
    def action_check_systemd_service_status_parser():
        """
        Parser.

        @return:
        """
        description = "check_systemd_service_status for specific duration"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(
            "--service_name", required=True, type=str, help="Service name to check"
        )
        parser.add_argument(
            "--min_uptime",
            required=True,
            type=str,
            help="Check running duration in seconds",
        )

        parser.epilog = f"Usage: python {__file__} [options]"
        return parser

    @staticmethod
    def action_check_systemd_service_status(arguments):
        """
        Action to check service status.

        @param arguments:
        @return:
        """

        arguments_dict = vars(arguments)
        SystemFunctionCommon.check_systemd_service_status(**arguments_dict)

    @staticmethod
    def check_systemd_service_status(service_name=None, min_uptime=None):
        """
        Check service managed by systemd is up for minimum min uptime seconds.

        @param service_name:
        @param min_uptime:
        @return:
        """

        min_uptime = int(min_uptime)
        desired_status_name = "active"
        status_change_seconds_limit = 120
        service_status_raw = SystemFunctionCommon.get_systemd_service_status(
            service_name
        )
        service_status = SystemFunctionCommon.extract_service_status_value(
            service_status_raw
        )

        if service_status in ["inactive", "failed"]:
            return False

        _, seconds_duration = SystemFunctionCommon.extract_service_status_times(
            service_status_raw
        )

        time_limit = datetime.datetime.now() + datetime.timedelta(
            seconds=status_change_seconds_limit
        )
        while (
            service_status != desired_status_name
            and datetime.datetime.now() < time_limit
        ):
            logger.info(
                f"Waiting for status to change from {service_status} to {desired_status_name}. Going to sleep for 5 sec"
            )
            time.sleep(5)
            service_status_raw = SystemFunctionCommon.get_systemd_service_status(
                service_name
            )
            service_status = SystemFunctionCommon.extract_service_status_value(
                service_status_raw
            )

            if service_status == "inactive":
                raise RuntimeError("Service is inactive. Should be something else.")

            if service_status == "failed":
                return False

            _, seconds_duration = SystemFunctionCommon.extract_service_status_times(
                service_status_raw
            )

        if service_status != desired_status_name:
            raise TimeoutError(
                f"service {service_name} did not reach {desired_status_name} in {status_change_seconds_limit} seconds"
            )

        if min_uptime <= seconds_duration:
            return True

        logger.info(
            f"Waiting for status duration time: {min_uptime}. Going to sleep for {min_uptime - seconds_duration} sec"
        )
        time.sleep(min_uptime - seconds_duration)
        service_status_raw = SystemFunctionCommon.get_systemd_service_status(
            service_name
        )
        service_status = SystemFunctionCommon.extract_service_status_value(
            service_status_raw
        )

        if service_status == "inactive":
            raise RuntimeError("Service is inactive. Should be something else.")

        _, seconds_duration = SystemFunctionCommon.extract_service_status_times(
            service_status_raw
        )
        if service_status != desired_status_name:
            raise TimeoutError(f"service {service_name} seams to be in restart loop")

        if min_uptime <= seconds_duration:
            return True

        raise TimeoutError(
            f"service {service_name} seams to be in restart loop after cause it can not keep {desired_status_name} "
            f"status for {min_uptime} seconds. Current status duration is {seconds_duration} "
        )

    # endregion
    def apt_install(self, package_name, package_names=None, needrestart_mode="a"):
        """
        Run apt install or upgrade.

        @param package_name:
        @param package_names:
        @return:
        :param needrestart_mode:
        """

        if package_name is not None:
            if package_names is not None:
                raise ValueError(f"Either package_name or package_names must be set but not both: {package_name}/{package_names} ")
            package_names = [package_name]
        SystemFunctionCommon.init_apt_packages()

        logger.info(f"Installing apt packages: {package_names}")

        command = f"sudo NEEDRESTART_MODE={needrestart_mode} apt{' --upgrade ' if self.upgrade else ' '}install -y {' '.join(package_names)}"

        def raise_on_error_callback(response):
            return (
                "has no installation candidate" in response["stdout"]
                or "is not available, but is referred to by another package"
                in response["stdout"]
            )

        SystemFunctionCommon.run_apt_bash_command(
            command, raise_on_error_callback=raise_on_error_callback
        )

        self.reinit_apt_packages()

    @staticmethod
    def apt_check_installed(package_name):
        """
        Check if the package or prefix+wildcard was installed.

        @param package_name:
        @return:
        """
        SystemFunctionCommon.init_apt_packages()
        if "*" in package_name:
            return SystemFunctionCommon.apt_check_installed_regex(package_name)

        for package in SystemFunctionCommon.APT_PACKAGES:
            if package.name == package_name:
                return True
        return False

    @staticmethod
    def apt_check_installed_regex(package_name: str):
        """
        Check installed by prefix and wildcard. e.g. 'logstash*'

        @param package_name:
        @return:
        """
        if package_name.count("*") == 1 and package_name.endswith("*"):
            package_name = package_name[:-1]
            for package in SystemFunctionCommon.APT_PACKAGES:
                if package_name in package.name:
                    return True
            return False

        raise NotImplementedError()

    @staticmethod
    def apt_purge(str_regex_name):
        """
        Self explanatory.

        @param str_regex_name:
        @return:
        """
        return SystemFunctionCommon.run_apt_bash_command(
            f"sudo apt purge -y {str_regex_name}"
        )

    def apt_check_repository_exists(self, repo_name):
        """
        Check weather we already have this repo.

        @param repo_name:
        @return:
        """

        self.init_apt_repositories()
        for repo in self.APT_REPOSITORIES:
            if repo_name in repo.str_src:
                return True
        return False

    def apt_add_repository(self, repo_name):
        """
        Apt add repo by name.

        @param repo_name:
        @return:
        """

        self.run_apt_bash_command(f"sudo add-apt-repository -y {repo_name}")

    @staticmethod
    def run_apt_bash_command(command, raise_on_error_callback=None):
        """
        Run apt commands with status checks unlocking the frontend.lock file and retries.

        @param command:
        @param raise_on_error_callback:
        @return:
        """

        for _ in range(3):
            for __ in range(10):
                try:
                    ret = SystemFunctionCommon.run_bash(command)
                    return ret
                except BashExecutor.BashError as inst:
                    dict_inst = json.loads(str(inst))
                    if "TimeoutExpired" in dict_inst["stderr"]:
                        SystemFunctionCommon.unlock_dpckg_lock()
                    elif "sudo dpkg --configure -a" in dict_inst["stderr"]:
                        _command = "echo Y | sudo dpkg --configure -a"
                        SystemFunctionCommon.run_bash(_command)
                    elif raise_on_error_callback is not None and raise_on_error_callback(
                        dict_inst
                    ):
                        raise
                    logger.warning(f"Failed to run command '{command}' Retrying...")

                    time.sleep(0.5)
            SystemFunctionCommon.unlock_dpckg_lock()

        raise TimeoutError(f"Timeout reached retrying '{command}'")

    @staticmethod
    def unlock_dpckg_lock():
        """
        Force unlocking - kill processes using the lock.
        @return:
        """
        ret = SystemFunctionCommon.run_bash(
            "sudo lsof /var/lib/dpkg/lock-frontend | awk '/[0-9]+/{print $2}'"
        )
        logger.info(ret)
        if ret["stdout"]:
            ret = SystemFunctionCommon.run_bash(
                f'sudo kill -s 9 {ret["stdout"]} || true'
            )
            logger.info(ret)

    @staticmethod
    def kill_process(str_pid):
        """
        @param str_pid:
        @return:
        """
        ret = SystemFunctionCommon.run_bash(f'sudo kill -s 9 "{str_pid}" || true')
        return ret

    def update_packages(self):
        """
        Update the information from apt repositories.
        If we update the repo list we need to run update.

        @return:
        """
        if SystemFunctionCommon.APT_PACKAGES_UPDATED:
            return

        ret = SystemFunctionCommon.run_bash("sudo DEBIAN_FRONTEND=noninteractive apt update")
        output = ret["stdout"]
        lines =  output.split("\n")

        self.validate_apt_update_output(lines)

        SystemFunctionCommon.APT_PACKAGES_UPDATED = True
        SystemFunctionCommon.APT_PACKAGES = []
        self.init_apt_packages()

    @staticmethod
    def validate_apt_update_output(stdout_lines):
        """
        Validate apt update output.

        @param lines:
        @return:
        """

        last_line = stdout_lines[-1]
        if (
            "can be upgraded" not in last_line
            and "All packages are up to date." not in last_line
        ):
            raise RuntimeError(stdout_lines)

    def reinit_apt_packages(self):
        """
        After we modify the apt packages' statuses (install, update, remove...) we need to reinit.

        @return:
        """
        SystemFunctionCommon.APT_PACKAGES = []
        SystemFunctionCommon.APT_PACKAGES_UPDATED = None
        self.init_apt_packages()

    def init_apt_packages(self):
        """
        Init installed packages list.

        @return:
        """

        self.update_packages()
        if not SystemFunctionCommon.APT_PACKAGES:
            response = SystemFunctionCommon.run_bash("sudo apt list --installed")
            packages = self.init_apt_packages_from_output(response["stdout"].split("\n"))
            SystemFunctionCommon.APT_PACKAGES = packages

    @staticmethod
    def init_apt_packages_from_output(stdout_lines):
        """
        Init packages

        :param stdout_lines:
        :return:
        """

        packages = []
        for line in stdout_lines:
            if "Listing..." in line:
                continue
            package = APTPackage()
            package.init_from_line(line)
            packages.append(package)
        return packages

    @staticmethod
    def init_apt_repositories():
        """
        Init all repositories from all .list files.
        Used to validate we have all the needed repos added already.

        @return:
        """
        if not SystemFunctionCommon.APT_REPOSITORIES:

            repos = SystemFunctionCommon.init_apt_repositories_from_file(
                "/etc/apt/sources.list"
            )
            SystemFunctionCommon.APT_REPOSITORIES.extend(repos)

            for root, _, files in os.walk("/etc/apt/sources.list.d"):
                for file_name in files:
                    if os.path.splitext(file_name)[1] != ".list":
                        continue
                    file_path = os.path.join(root, file_name)
                    repos = SystemFunctionCommon.init_apt_repositories_from_file(
                        file_path
                    )
                    SystemFunctionCommon.APT_REPOSITORIES.extend(repos)

    @staticmethod
    def init_apt_repositories_from_file(file_path):
        """
        Init the list of repositories from files.
        Repos are being used by APT for 'update' functionality.
        These repositories can be added manually by changing sources.list files.

        @param file_path:
        @return:
        """
        ret = []
        with open(file_path, encoding="utf-8") as file_handler:
            lines = file_handler.readlines()

        for line in lines:
            if not line.startswith("deb "):
                continue
            line = line.strip()
            repo = APTRepository()
            repo.init_from_line(line, file_path)
            ret.append(repo)

        return ret

    # endregion

    @staticmethod
    def get_systemd_service_status(service_name):
        """
        Check system status.

        @param service_name:
        @return:
        """
        # pylint: disable= subprocess-run-check
        command = f"systemctl status {service_name}"
        ret = subprocess.run([command], capture_output=True, shell=True)
        decoded_ret = ret.stdout.decode().strip("\n")
        return decoded_ret

    @staticmethod
    def extract_service_status_value(service_status_raw):
        """
        Find service status value.

        @param service_status_raw:
        @return:
        """

        lst_line = SystemFunctionCommon.extract_service_status_line_raw(
            service_status_raw
        )
        status = lst_line[1]
        if status not in ["active", "failed", "activating", "inactive"]:
            raise NotImplementedError(f"status is '{status}'")
        return status

    @staticmethod
    def extract_service_status_times(service_status_raw):
        """
        # 'Active: active (running) since Tue 2022-04-12 18:32:04 GMT; 2h 33min ago'

        @param service_status_raw:
        @return: server_time, duration
        """
        lst_line = SystemFunctionCommon.extract_service_status_line_raw(
            service_status_raw
        )
        since_index = lst_line.index("since")
        str_time_data = " ".join(lst_line[since_index + 1 :])
        start_date_str, duration_string = str_time_data.split("; ")
        if "GMT" in start_date_str:
            timezone = "GMT"
        elif "UTC" in start_date_str:
            timezone = "UTC"
        else:
            raise ValueError(start_date_str)
        start_date = datetime.datetime.strptime(
            start_date_str, f"%a %Y-%m-%d %H:%M:%S {timezone}"
        )
        return start_date, SystemFunctionCommon.extract_service_status_seconds_duration(
            duration_string
        )

    @staticmethod
    def extract_service_status_seconds_duration(duration_string):
        """
        2h 33min ago'
        3 months 19 days ago
        6s ago
        @param duration_string:
        @return:
        """
        # pylint: disable=too-many-statements, too-many-branches
        logger.info(f"Duration string '{duration_string}'")

        duration_lst = duration_string.lower().split(" ")
        hours = 0
        minutes = 0
        seconds = 0
        days = 0

        try:
            index = duration_lst.index("days")
            days = int(duration_lst[index - 1])
            duration_lst = duration_lst[: index - 1] + duration_lst[index + 1 :]
        except ValueError:
            pass

        try:
            index = duration_lst.index("weeks")
            weeks = int(duration_lst[index - 1])
            duration_lst = duration_lst[: index - 1] + duration_lst[index + 1 :]
            days += weeks * 7
        except ValueError:
            pass

        try:
            index = duration_lst.index("week")
            weeks = int(duration_lst[index - 1])
            duration_lst = duration_lst[: index - 1] + duration_lst[index + 1:]
            days += weeks * 7
        except ValueError:
            pass

        try:
            index = duration_lst.index("day")
            days = int(duration_lst[index - 1])
            duration_lst = duration_lst[: index - 1] + duration_lst[index + 1 :]
        except ValueError:
            pass

        try:
            index = duration_lst.index("months")
            months = int(duration_lst[index - 1])
            duration_lst = duration_lst[: index - 1] + duration_lst[index + 1 :]
        except ValueError:
            months = 0

        try:
            index = duration_lst.index("month")
            months = int(duration_lst[index - 1])
            duration_lst = duration_lst[: index - 1] + duration_lst[index + 1 :]
        except ValueError:
            pass

        try:
            index = duration_lst.index("years")
            years = int(duration_lst[index - 1])
            duration_lst = duration_lst[: index - 1] + duration_lst[index + 1 :]
        except ValueError:
            years = 0

        try:
            index = duration_lst.index("year")
            years = int(duration_lst[index - 1])
            duration_lst = duration_lst[: index - 1] + duration_lst[index + 1 :]
        except ValueError:
            pass

        if duration_lst[-1] != "ago":
            raise RuntimeError(f"{duration_lst} has no 'ago'")

        for duration_part in duration_lst[:-1]:
            if duration_part.endswith("ms"):
                seconds = int(duration_part[:-2]) / 1000
            elif duration_part.endswith("s"):
                seconds = int(duration_part[:-1])
            elif duration_part.endswith("h"):
                hours = int(duration_part[:-1])
            elif duration_part.endswith("min"):
                minutes = int(duration_part[:-3])
            else:
                raise ValueError(f"{duration_part} in {duration_lst}")

        days = days + 365 * years + months * 30
        return days * 24 * 60 * 60 + 60 * 60 * hours + minutes * 60 + seconds

    @staticmethod
    def extract_service_status_line_raw(service_status_raw):
        """
        Extract service status from bash output.

        @param service_status_raw:
        @return:
        """

        for line in service_status_raw.split("\n"):
            line = line.strip(" ")
            if line.startswith("Active:"):
                lst_line = line.split(" ")
                return lst_line
        return None

    # region files
    def check_file_provisioned(self, src_file_path: str, dst_file_path: str):
        """
        Check the files exist and equal in content.

        @param src_file_path:
        @param dst_file_path:
        @return:
        """

        if not os.path.isfile(dst_file_path):
            return False

        if src_file_path.startswith("./"):
            raise DeprecationWarning(f"Use absolute file path: {src_file_path}")

        replacement_engine = ReplacementEngine()
        with open(src_file_path, encoding="utf-8") as file_handler:
            replacement_string = file_handler.read()

        return replacement_engine.check_file_contains(dst_file_path, replacement_string)

    # endregion

    @staticmethod
    def action_add_line_to_file_parser():
        """
        Self explanatory.

        @return:
        """

        description = "add_line_to_file"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--line", required=True, type=str, help="Line to be added")
        parser.add_argument(
            "--file_path", required=True, type=str, help="Path to the file"
        )

        parser.epilog = f"Usage: python {__file__} [options]"
        return parser

    @staticmethod
    def action_add_line_to_file(arguments):
        """
        Self explanatory.

        @param arguments:
        @return:
        """

        arguments_dict = vars(arguments)
        SystemFunctionCommon.add_line_to_file(**arguments_dict)

    @staticmethod
    def add_line_to_file(line=None, file_path=None, sudo=False):
        """
        Self explanatory.

        @param line:
        @param file_path:
        @param sudo:
        @return:
        """

        if not isinstance(line, str):
            raise ValueError(line)

        if not isinstance(file_path, str):
            raise ValueError(file_path)

        if sudo:
            return SystemFunctionCommon.add_line_to_file_sudo(
                line=line, file_path=file_path
            )
        if not line.endswith("\n"):
            line = line + "\n"

        try:
            with open(file_path, "r", encoding="utf-8") as file_handler:
                lines = file_handler.readlines()
                if line in lines:
                    return None
        except FileNotFoundError:
            pass

        with open(file_path, "a+", encoding="utf-8") as file_handler:
            file_handler.write(line)

        return None

    @staticmethod
    def add_line_to_file_sudo(line=None, file_path=None):
        """
        Self explanatory.

        @param line:
        @param file_path:
        @return:
        """

        if not isinstance(line, str):
            raise ValueError(line)

        if not isinstance(file_path, str):
            raise ValueError(file_path)

        try:
            SystemFunctionCommon.check_file_exists(file_path, sudo=True)
        except SystemFunctionCommon.FailedCheckError:
            return SystemFunctionCommon.run_bash(
                f'echo "{line}" | sudo tee -a {file_path} > /dev/null'
            )

        try:
            response = SystemFunctionCommon.run_bash(
                f"sudo grep -F '{line}' {file_path}"
            )
            if response["stdout"]:
                return response
        except BashExecutor.BashError as inst:
            dict_inst = json.loads(str(inst))
            if dict_inst["stderr"] and "No such file or directory" not in dict_inst["stderr"]:
                raise

        return SystemFunctionCommon.run_bash(
            f'echo "{line}" | sudo tee -a {file_path} > /dev/null'
        )

    def test_local_port(self):
        """
        TBD
        Check if local port is listening.

        @return:
        """

        print(self)
        command = "netstat - na"

        ret = SystemFunctionCommon.run_bash(command)

        return ret["todo"]

    def test_remote_port(self):
        """
        TBD
               import socket
                 sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                  result = sock.connect_ex(('127.0.0.1',80))
                  if result == 0:
                  print "Port is open"
                  else:
                  print "Port is not open"
                  sock.close()

        @return:
        """

        print(self)
        command = "netstat - na"

        ret = SystemFunctionCommon.run_bash(command)

        return ret["todo"]

    class FailedCheckError(RuntimeError):
        """
        System function test has failed.
        """

    @staticmethod
    def last_line_validator(string_to_look_for, convert_to_lower=True):
        """
        Check latest nonempty line contains the string.

        :param convert_to_lower:
        :param string_to_look_for:
        :return:
        """

        if convert_to_lower:
            string_to_look_for = string_to_look_for.lower()

        def helper(lst_stdout, lst_stderr, error_code):
            """
            Helper function

            :param lst_stdout:
            :param lst_stderr:
            :param error_code:
            :return:
            """

            logger.info(f"Helper ignoring {lst_stderr=}, {error_code=}")

            line = ""
            for line in reversed(lst_stdout):
                if not line or line == "\n":
                    continue
                if convert_to_lower:
                    line = line.lower()
                if string_to_look_for in line:
                    return True

            raise ValueError(f"Can not find '{line}' in the last line {line}")
        return helper

    @staticmethod
    def grep_validator(strings_to_look_for, convert_to_lower=True):
        """
        Check latest nonempty line contains the string.

        :param strings_to_look_for:
        :param convert_to_lower:
        :return:
        """

        if convert_to_lower:
            strings_to_look_for = [string_to_look_for.lower() for string_to_look_for in strings_to_look_for]

        def helper(lst_stdout, lst_stderr, error_code):
            """
            Helper function

            :param lst_stdout:
            :param lst_stderr:
            :param error_code:
            :return:
            """

            logger.info(f"Helper ignoring {lst_stderr=}, {error_code=}")
            errors = []
            output = "".join(lst_stdout)
            if convert_to_lower:
                output = output.lower()

            for string_to_look_for in strings_to_look_for:
                if string_to_look_for not in output:
                    errors.append(f"No string '{string_to_look_for}' in output")

            if errors:
                raise RuntimeError("\n".join(errors))

            return True

        return helper

    def check_systemd_service_status_remote(self, service_name: str, min_uptime: int = 60):
        """
        Check the service uptime.

        :param service_name:
        :param min_uptime:
        :return:
        """

        command = f'servicestartsec=$(date -d "$(systemctl show --property=ActiveEnterTimestamp {service_name} | cut -d= -f2)" +%s) && serviceelapsedsec=$(( $(date +%s) - servicestartsec )) && echo $serviceelapsedsec'
        sleep_time = 10
        retries = min_uptime * 2 // sleep_time
        for i in range(retries):
            lst_stdout, _, _ = self.remoter.execute(command)
            str_seconds = lst_stdout[-1].strip("\n")
            int_seconds = int(str_seconds)
            if int_seconds >= min_uptime:
                return True

            logger.info(f"Service is up for {str_seconds} seconds {min_uptime=}. Going to sleep for {sleep_time} [{i}/{retries}]")

            time.sleep(sleep_time)
        raise TimeoutError(f"Waited for {min_uptime} seconds")

    def systemctl_restart_service_and_wait_remote(self, service_name: str):
        """
        Restart and wait for service to be up and healthy.

        :param service_name:
        :return:
        """

        self.remoter.execute(f"sudo systemctl restart {service_name}")

        self.check_systemd_service_status_remote(service_name)

    def remove_file_remote(self, remoter:Remoter, file_path, sudo=False):
        """
        Delete file.

        :param remoter:
        :param file_path:
        :param sudo:
        :return:
        """

        if self.check_file_exists_remote(remoter, file_path, sudo=sudo):
            command = f"rm -rf {file_path}"
            if sudo:
                command = "sudo " + command
            remoter.execute(command)
            return self.check_file_exists_remote(remoter, file_path, sudo=sudo)

        return True

    @staticmethod
    def check_file_exists_remote(remoter: Remoter, file_path, sudo=False):
        """
        Check exists file.

        :param remoter:
        :param file_path:
        :param sudo:
        :return:
        """
        use_sudo = 'sudo ' if sudo else ''
        command = f'if {use_sudo}test -f "{file_path}"; then echo "true"; else echo "false"; fi'
        ret = remoter.execute(command)
        logger.info(f"check_file_exists_remote: {ret}")
        return SystemFunctionCommon.check_file_exists_output_validator(file_path, [line.strip("\n") for line in ret[0]], [line.strip("\n") for line in ret[1]])

    @staticmethod
    def add_line_to_file_remote(remoter: Remoter, line=None, file_path:Path=None, sudo=False):
        """
        Standard

        @param line:
        @param file_path:
        @return:
        """

        if not isinstance(line, str):
            raise ValueError(line)

        sudo_prefix = "sudo " if sudo else ""
        try:
            SystemFunctionCommon.check_file_exists_remote(remoter, file_path, sudo=sudo)
        except SystemFunctionCommon.FailedCheckError:
            remoter.execute(
               f" {sudo_prefix}touch {file_path}"
            )
            SystemFunctionCommon.check_file_exists_remote(remoter, file_path, sudo=sudo)

        try:
            return SystemFunctionCommon.check_line_in_file_remote(remoter, line, file_path, sudo=sudo)
        except SystemFunctionCommon.FailedCheckError:
            remoter.execute(
            f'echo "{line}" | {sudo_prefix}tee -a {file_path} > /dev/null'
            )

        return SystemFunctionCommon.check_line_in_file_remote(remoter, line, file_path, sudo=sudo)


    @staticmethod
    def check_line_in_file_remote(remoter: Remoter, line:str, file_path:Path, sudo=False):
        """
        Check exists file.

        :param line:
        :param remoter:
        :param file_path:
        :param sudo:
        :return:
        """
        sudo_prefix = "sudo " if sudo else ""
        response = remoter.execute(

                f"{sudo_prefix}grep -F '{line}' {file_path} || true"
            )

        if response[0]:
            return True
        raise SystemFunctionCommon.FailedCheckError(f"Line: '{line}' was not found in the file: '{file_path}'")

    def unlock_dpckg_lock_remote(self):
        """
        Force unlocking - kill processes using the lock.
        @return:
        """

        self.remoter.execute(
            "ls"
        )

        ret = self.remoter.execute(
            "sudo lsof /var/lib/dpkg/lock-frontend | awk '/[0-9]+/{print $2}'"
        )

        if ret[0]:
            pid = int(ret[0][-1].strip("\n"))
            self.remoter.execute(
                f'sudo kill -s 9 {pid} || true'
            )
            # if "sudo dpkg --configure -a" in repr(inst_error):
            self.remoter.execute("yes n | sudo DEBIAN_FRONTEND=noninteractive dpkg --configure -a")


SystemFunctionCommon.ACTION_MANAGER.register_action(
    "check_files_exist",
    SystemFunctionCommon.check_files_exist_parser,
    SystemFunctionCommon.check_files_exist_action,
)

SystemFunctionCommon.ACTION_MANAGER.register_action(
    "add_line_to_file",
    SystemFunctionCommon.action_add_line_to_file_parser,
    SystemFunctionCommon.action_add_line_to_file,
)

SystemFunctionCommon.ACTION_MANAGER.register_action(
    "move_file",
    SystemFunctionCommon.action_move_file_parser,
    SystemFunctionCommon.action_move_file,
)

SystemFunctionCommon.ACTION_MANAGER.register_action(
    "compare_files",
    SystemFunctionCommon.action_compare_files_parser,
    SystemFunctionCommon.action_compare_files,
)

SystemFunctionCommon.ACTION_MANAGER.register_action(
    "perform_comment_line_replacement",
    SystemFunctionCommon.action_perform_comment_line_replacement_parser,
    SystemFunctionCommon.action_perform_comment_line_replacement,
)

SystemFunctionCommon.ACTION_MANAGER.register_action(
    "check_systemd_service_status",
    SystemFunctionCommon.action_check_systemd_service_status_parser,
    SystemFunctionCommon.action_check_systemd_service_status,
)

if __name__ == "__main__":
    SystemFunctionCommon.ACTION_MANAGER.call_action()

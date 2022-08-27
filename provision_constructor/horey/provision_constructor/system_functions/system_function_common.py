"""
Common functionality to all system_functions.

"""

import json
import shutil
import datetime
import uuid
import os
import argparse
import subprocess
import time

from horey.common_utils.actions_manager import ActionsManager
from horey.replacement_engine.replacement_engine import ReplacementEngine
from horey.provision_constructor.system_functions.apt_package import APTPackage
from horey.provision_constructor.system_functions.apt_repository import APTRepository
from horey.h_logger import get_logger

logger = get_logger()


class SystemFunctionCommon:
    """
    Common functionality to all system_functions.

    """

    ACTION_MANAGER = ActionsManager()
    APT_PACKAGES = None
    APT_REPOSITORIES = None
    APT_PACKAGES_UPDATED = False
    PIP_PACKAGES = None

    def __init__(self, system_function_provisioner_dir_path):
        self.system_function_provisioner_dir_path = system_function_provisioner_dir_path
        self.validate_provisioned_ancestor = True

    @staticmethod
    def init_pip_packages():
        """
        Init installed packages.

        @return:
        """

        ret = SystemFunctionCommon.run_bash("pip3 freeze")
        SystemFunctionCommon.PIP_PACKAGES = ret["stdout"].split("\n")

    def check_pip_installed(self, package_name):
        """
        Check weather the package is installed.

        @param package_name:
        @return:
        """

        if SystemFunctionCommon.PIP_PACKAGES is None:
            SystemFunctionCommon.init_pip_packages()

        for pip_package in self.PIP_PACKAGES:
            if package_name in pip_package:
                return True

        for line in SystemFunctionCommon.PIP_PACKAGES:
            logger.info(f"Installed: {line}")

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
    def run_bash(command, ignore_on_error_callback=None, debug=True):
        """
        Run bash command, return stdout, stderr and return code.

        @param debug:
        @param command:
        @param ignore_on_error_callback:
        @return:
        """

        logger.info(f"run_bash: {command}")

        file_name = f"tmp-{str(uuid.uuid4())}.sh"
        with open(file_name, "w") as file_handler:
            file_handler.write(command)
            command = f"/bin/bash {file_name}"
        ret = subprocess.run([command], capture_output=True, shell=True)

        os.remove(file_name)
        return_dict = {"stdout": ret.stdout.decode().strip("\n"),
                       "stderr": ret.stderr.decode().strip("\n"),
                       "code": ret.returncode}
        if debug:
            logger.info("stdout:")
            logger.info(return_dict["stdout"])
            logger.info("stderr:")
            logger.info(return_dict["stderr"])
        if ret.returncode != 0:
            if ignore_on_error_callback is not None and not ignore_on_error_callback(return_dict):
                raise SystemFunctionCommon.BashError(json.dumps(return_dict))

        return return_dict

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

        with open(file_path) as file_handler:
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
        parser.add_argument("--files_paths", required=True, type=str, help=f"Comma separated string file list")
        return parser

    @staticmethod
    def check_files_exist(arguments) -> None:
        """
        Self explanatory.

        @param arguments:
        @return:
        """

        errors = []
        for file_path in arguments.files_paths.split(","):
            if not os.path.exists(file_path):
                errors.append(f"File '{file_path}' does not exist")
                continue

            if not os.path.isfile(file_path):
                errors.append(f"Path '{file_path}' is not a file")

        if errors:
            raise SystemFunctionCommon.FailedCheckError("\n".join(errors))

    @staticmethod
    def action_move_file_parser():
        """
        Self explanatory.

        @return:
        """

        description = "move_file from src_path to dst_path"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--src_file_path", required=True, type=str, help="Source file path")
        parser.add_argument("--dst_file_path", required=True, type=str, help="Destination file path")

        parser.epilog = f"Usage: python3 {__file__} [options]"
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

    def provision_file(self, src_file_path, dst_file_path):
        """
        Self explanatory.

        @param src_file_path:
        @param dst_file_path:
        @return:
        """

        if src_file_path.startswith("./"):
            src_file_path = os.path.join(self.system_function_provisioner_dir_path, src_file_path)

        os.makedirs(os.path.dirname(dst_file_path), exist_ok=True)
        SystemFunctionCommon.run_bash(f"sudo rm -rf {dst_file_path}")
        SystemFunctionCommon.run_bash(f"sudo cp {src_file_path} {dst_file_path}")

    # region compare_files
    @staticmethod
    def action_compare_files_parser():
        """
        Self explanatory.

        @return:
        """

        description = "compare_files from src_path to dst_path"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--src_file_path", required=True, type=str, help="Source file path")
        parser.add_argument("--dst_file_path", required=True, type=str, help="Destination file path")

        parser.epilog = f"Usage: python3 {__file__} [options]"
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

        with open(src_file_path) as file_handler:
            src_file_string = file_handler.read()

        with open(dst_file_path) as file_handler:
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
        parser.add_argument("--src_file_path", required=True, type=str, help="Source file path")
        parser.add_argument("--dst_file_path", required=True, type=str, help="Destination file path")
        parser.add_argument("--comment_line", required=True, type=str, help="Destination file path")

        parser.epilog = f"Usage: python3 {__file__} [options]"
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
    def perform_comment_line_replacement(src_file_path=None, dst_file_path=None, comment_line=None):
        """
        Comment line being replaced with contents of a file.

        @param src_file_path:
        @param dst_file_path:
        @param comment_line:
        @return:
        """

        replacement_engine = ReplacementEngine()
        with open(src_file_path) as file_handler:
            replacement_string = file_handler.read()

        replacement_engine.perform_comment_line_replacement(dst_file_path, comment_line, replacement_string,
                                                            keep_comment=True)

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
        parser.add_argument("--service_name", required=True, type=str, help="Service name to check")
        parser.add_argument("--min_uptime", required=True, type=str, help="Check running duration in seconds")

        parser.epilog = f"Usage: python3 {__file__} [options]"
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
        status_name = "active"
        status_change_seconds_limit = 120
        service_status_raw = SystemFunctionCommon.get_systemd_service_status(service_name)
        service_status = SystemFunctionCommon.extract_service_status_value(service_status_raw)
        server_time, seconds_duration = SystemFunctionCommon.extract_service_status_times(service_status_raw)

        time_limit = datetime.datetime.now() + datetime.timedelta(seconds=status_change_seconds_limit)
        while service_status != status_name and datetime.datetime.now() < time_limit:
            logger.info(
                f"Waiting for status to change from {service_status} to {status_name}. Going to sleep for 5 sec")
            time.sleep(5)
            service_status_raw = SystemFunctionCommon.get_systemd_service_status(service_name)
            service_status = SystemFunctionCommon.extract_service_status_value(service_status_raw)
            server_time, seconds_duration = SystemFunctionCommon.extract_service_status_times(service_status_raw)

        if service_status != status_name:
            raise TimeoutError(
                f"service {service_name} did not reach {status_name} in {status_change_seconds_limit} seconds")

        if min_uptime <= seconds_duration:
            return True

        logger.info(
            f"Waiting for status duration time: {min_uptime}. Going to sleep for {min_uptime - seconds_duration} sec")
        time.sleep(min_uptime - seconds_duration)
        service_status_raw = SystemFunctionCommon.get_systemd_service_status(service_name)
        service_status = SystemFunctionCommon.extract_service_status_value(service_status_raw)
        server_time, seconds_duration = SystemFunctionCommon.extract_service_status_times(service_status_raw)
        if service_status != status_name:
            raise TimeoutError(f"service {service_name} seams to be in restart loop")

        if min_uptime <= seconds_duration:
            return True

        raise TimeoutError(
            f"service {service_name} seams to be in restart loop after cause it can not keep {status_name} "
            f"status for {min_uptime} seconds. Current status duration is {seconds_duration} ")

    # endregion

    # region apt_install
    @staticmethod
    def action_apt_install_parser():
        description = "apt_install"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--packages", required=True, type=str, help="Service name to check")

        parser.epilog = f"Usage: python3 {__file__} [options]"
        return parser

    @staticmethod
    def action_apt_install(arguments):
        arguments_dict = vars(arguments)
        SystemFunctionCommon.apt_install(**arguments_dict)

    @staticmethod
    def apt_install(package_name=None, upgrade_version=True):
        SystemFunctionCommon.init_apt_packages()

        logger.info(f"Installing apt package: '{package_name}'")

        if upgrade_version or not SystemFunctionCommon.apt_check_installed(package_name):
            command = f"sudo apt install -y {package_name}"
        else:
            command = f"sudo apt --only-upgrade install -y {package_name}"

        def raise_on_error_callback(response):
            return "has no installation candidate" in response["stdout"] or \
                   "is not available, but is referred to by another package" in response["stdout"]

        SystemFunctionCommon.run_apt_bash_command(command, raise_on_error_callback=raise_on_error_callback)

    @staticmethod
    def apt_check_installed(package_name):
        SystemFunctionCommon.init_apt_packages()
        if "*" in package_name:
            return SystemFunctionCommon.apt_check_installed_regex(package_name)

        for package in SystemFunctionCommon.APT_PACKAGES:
            if package.name == package_name:
                return True
        return False

    @staticmethod
    def apt_check_installed_regex(package_name: str):
        if package_name.count("*") == 1 and package_name.endswith("*"):
            package_name = package_name[:-1]
            for package in SystemFunctionCommon.APT_PACKAGES:
                if package_name in package.name:
                    return True
            return False

        raise NotImplementedError()

    @staticmethod
    def apt_purge(str_regex_name):
        return SystemFunctionCommon.run_apt_bash_command(f"sudo apt purge -y {str_regex_name}")

    def apt_check_repository_exists(self, repo_name):
        self.init_apt_repositories()
        for repo in self.APT_REPOSITORIES:
            if repo_name in repo.str_src:
                return True
        return False

    def apt_add_repository(self, repo_name):
        self.run_apt_bash_command(f"sudo add-apt-repository -y {repo_name}")

    @staticmethod
    def run_apt_bash_command(command, raise_on_error_callback=None):
        for unlock_counter in range(3):
            for counter in range(10):
                try:
                    ret = SystemFunctionCommon.run_bash(command)
                    return ret
                except SystemFunctionCommon.BashError as inst:
                    dict_inst = json.loads(str(inst))
                    if raise_on_error_callback is not None and raise_on_error_callback(dict_inst):
                        raise
                    str_uid = str(uuid.uuid4())
                    logger.warning(f"Failed to run command '{command}' with str_uid: '{str_uid}'")
                    try:
                        logger.warning(f"output_uid_start_{str_uid}\n{json.load(dict_inst['stdout'])}\noutput_uid_end{str_uid}")
                        logger.warning(f"error_uid_start_{str_uid}\n{json.load(dict_inst['stderr'])}\nerror_uid_end{str_uid}")
                    except Exception:
                        logger.warning(f"output_uid_start_{str_uid}\n{dict_inst['stdout']}\noutput_uid_end{str_uid}")
                        logger.warning(f"error_uid_start_{str_uid}\n{dict_inst['stderr']}\nerror_uid_end{str_uid}")

                    time.sleep(0.5)
            SystemFunctionCommon.unlock_dpckg_lock()

        raise TimeoutError(f"Timeout reached retrying '{command}'")

    @staticmethod
    def unlock_dpckg_lock():
        ret = SystemFunctionCommon.run_bash("sudo lsof /var/lib/dpkg/lock-frontend | awk '/[0-9]+/{print $2}'")
        logger.info(ret)
        if ret["stdout"]:
            ret = SystemFunctionCommon.run_bash(f'sudo kill -s 9 {ret["stdout"]} || true')
            logger.info(ret)

    def kill_process(self, str_pid):
        """
        @param str_pid:
        @return:
        """
        ret = SystemFunctionCommon.run_bash(f'sudo kill -s 9 "{str_pid}" || true')
        return ret

    @staticmethod
    def update_packages():
        if SystemFunctionCommon.APT_PACKAGES_UPDATED:
            return

        ret = SystemFunctionCommon.run_bash("sudo apt update")
        output = ret["stdout"]
        if "can be upgraded" not in output.split("\n")[-1]:
            raise RuntimeError(output)

        SystemFunctionCommon.APT_PACKAGES_UPDATED = True
        SystemFunctionCommon.APT_PACKAGES = None
        SystemFunctionCommon.init_apt_packages()

    @staticmethod
    def reinit_apt_packages():
        SystemFunctionCommon.APT_PACKAGES = None
        SystemFunctionCommon.APT_PACKAGES_UPDATED = None
        SystemFunctionCommon.init_apt_packages()

    @staticmethod
    def init_apt_packages():
        SystemFunctionCommon.update_packages()
        if SystemFunctionCommon.APT_PACKAGES is None:
            SystemFunctionCommon.APT_PACKAGES = []
            response = SystemFunctionCommon.run_bash("sudo apt list --installed")
            for line in response["stdout"].split("\n"):
                if "Listing..." in line:
                    continue
                package = APTPackage()
                package.init_from_line(line)
                SystemFunctionCommon.APT_PACKAGES.append(package)

    @staticmethod
    def init_apt_repositories():
        if SystemFunctionCommon.APT_REPOSITORIES is None:

            SystemFunctionCommon.APT_REPOSITORIES = []

            repos = SystemFunctionCommon.init_apt_repositories_from_file("/etc/apt/sources.list")
            SystemFunctionCommon.APT_REPOSITORIES.extend(repos)

            for root, dirs, files in os.walk("/etc/apt/sources.list.d"):
                for file_name in files:
                    if os.path.splitext(file_name)[1] != ".list":
                        continue
                    file_path = os.path.join(root, file_name)
                    repos = SystemFunctionCommon.init_apt_repositories_from_file(file_path)
                    SystemFunctionCommon.APT_REPOSITORIES.extend(repos)

    @staticmethod
    def init_apt_repositories_from_file(file_path):
        ret = []
        with open(file_path) as file_handler:
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

        lst_line = SystemFunctionCommon.extract_service_status_line_raw(service_status_raw)
        status = lst_line[1]
        if status not in ["active", "failed", "activating"]:
            raise NotImplementedError(f"status is {status}")
        return status

    @staticmethod
    def extract_service_status_times(service_status_raw):
        """
        # 'Active: active (running) since Tue 2022-04-12 18:32:04 GMT; 2h 33min ago'

        @param service_status_raw:
        @return: server_time, duration
        """
        lst_line = SystemFunctionCommon.extract_service_status_line_raw(service_status_raw)
        since_index = lst_line.index("since")
        str_time_data = " ".join(lst_line[since_index + 1:])
        start_date_str, duration_string = str_time_data.split("; ")
        if "GMT" in start_date_str:
            timezone = "GMT"
        elif "UTC" in start_date_str:
            timezone = "UTC"
        else:
            raise ValueError(start_date_str)
        start_date = datetime.datetime.strptime(start_date_str, f"%a %Y-%m-%d %H:%M:%S {timezone}")
        return start_date, SystemFunctionCommon.extract_service_status_seconds_duration(duration_string)

    @staticmethod
    def extract_service_status_seconds_duration(duration_string):
        """
        2h 33min ago'
        3 months 19 days ago
        6s ago
        @param duration_string:
        @return:
        """

        logger.info(f"Duration string '{duration_string}'")

        duration_lst = duration_string.lower().split(" ")
        hours = 0
        minutes = 0
        seconds = 0
        days = 0

        try:
            index = duration_lst.index("days")
            days = int(duration_lst[index - 1])
            duration_lst = duration_lst[:index - 1] + duration_lst[index + 1:]
        except ValueError:
            pass

        try:
            index = duration_lst.index("weeks")
            weeks = int(duration_lst[index - 1])
            duration_lst = duration_lst[:index - 1] + duration_lst[index + 1:]
            days += weeks * 7
        except ValueError:
            pass

        try:
            index = duration_lst.index("day")
            days = int(duration_lst[index - 1])
            duration_lst = duration_lst[:index - 1] + duration_lst[index + 1:]
        except ValueError:
            pass

        try:
            index = duration_lst.index("months")
            months = int(duration_lst[index - 1])
            duration_lst = duration_lst[:index - 1] + duration_lst[index + 1:]
        except ValueError:
            months = 0

        try:
            index = duration_lst.index("month")
            months = int(duration_lst[index - 1])
            duration_lst = duration_lst[:index - 1] + duration_lst[index + 1:]
        except ValueError:
            pass

        try:
            index = duration_lst.index("years")
            years = int(duration_lst[index - 1])
            duration_lst = duration_lst[:index - 1] + duration_lst[index + 1:]
        except ValueError:
            years = 0

        try:
            index = duration_lst.index("year")
            years = int(duration_lst[index - 1])
            duration_lst = duration_lst[:index - 1] + duration_lst[index + 1:]
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
            src_file_path = os.path.join(self.system_function_provisioner_dir_path, src_file_path)

        replacement_engine = ReplacementEngine()
        with open(src_file_path) as file_handler:
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
        parser.add_argument("--file_path", required=True, type=str, help="Path to the file")

        parser.epilog = f"Usage: python3 {__file__} [options]"
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
            return SystemFunctionCommon.add_line_to_file_sudo(line=line, file_path=file_path)
        if not line.endswith("\n"):
            line = line + "\n"

        try:
            with open(file_path, "r") as file_handler:
                lines = file_handler.readlines()
                if line in lines:
                    return
        except FileNotFoundError:
            pass

        with open(file_path, "a+") as file_handler:
            file_handler.write(line)

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
            response = SystemFunctionCommon.run_bash(f"sudo grep -F '{line}' {file_path}")
            if response["stdout"]:
                return
        except SystemFunctionCommon.BashError as inst:
            dict_inst = json.loads(str(inst))
            if "No such file or directory" not in dict_inst["stderr"]:
                raise

        return SystemFunctionCommon.run_bash(f'echo "{line}" | sudo tee -a {file_path} > /dev/null')

    class BashError(RuntimeError):
        """
        Running bash command returned != 0 code.

        """

        pass

    def test_local_port(self):
        """
        Cehck if local port is listening.

        @return:
        """

        raise NotImplementedError("TBD")

    def test_remote_port(self):
        """
         import socket
           sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1',80))
            if result == 0:
            print "Port is open"
            else:
            print "Port is not open"
            sock.close()
        """
        raise NotImplementedError("TBD")

    class FailedCheckError(RuntimeError):
        pass


SystemFunctionCommon.ACTION_MANAGER.register_action("check_files_exist",
                                                    SystemFunctionCommon.check_files_exist_parser,
                                                    SystemFunctionCommon.check_files_exist)

SystemFunctionCommon.ACTION_MANAGER.register_action("add_line_to_file",
                                                    SystemFunctionCommon.action_add_line_to_file_parser,
                                                    SystemFunctionCommon.action_add_line_to_file)

SystemFunctionCommon.ACTION_MANAGER.register_action("move_file",
                                                    SystemFunctionCommon.action_move_file_parser,
                                                    SystemFunctionCommon.action_move_file)

SystemFunctionCommon.ACTION_MANAGER.register_action("compare_files",
                                                    SystemFunctionCommon.action_compare_files_parser,
                                                    SystemFunctionCommon.action_compare_files)

SystemFunctionCommon.ACTION_MANAGER.register_action("perform_comment_line_replacement",
                                                    SystemFunctionCommon.action_perform_comment_line_replacement_parser,
                                                    SystemFunctionCommon.action_perform_comment_line_replacement)

SystemFunctionCommon.ACTION_MANAGER.register_action("check_systemd_service_status",
                                                    SystemFunctionCommon.action_check_systemd_service_status_parser,
                                                    SystemFunctionCommon.action_check_systemd_service_status)

SystemFunctionCommon.ACTION_MANAGER.register_action("apt_install",
                                                    SystemFunctionCommon.action_apt_install_parser,
                                                    None)

if __name__ == "__main__":
    SystemFunctionCommon.ACTION_MANAGER.call_action()

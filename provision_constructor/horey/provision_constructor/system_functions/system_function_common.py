import pdb
import shutil
import datetime
import uuid
import os

import time
from horey.common_utils.actions_manager import ActionsManager
from horey.replacement_engine.replacement_engine import ReplacementEngine
import argparse
import subprocess


class SystemFunctionCommon:
    ACTION_MANAGER = ActionsManager()

    def __init__(self):
        return

    @staticmethod
    def empty_parser():
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
    def run_bash(command):
        file_name = f"tmp-{str(uuid.uuid4())}.sh"
        with open(file_name, "w") as file_handler:
            file_handler.write(command)
            command = f"/bin/bash {file_name}"
        ret = subprocess.run([command], capture_output=True, shell=True)
        return ret.stdout.decode().strip("\n")

    @staticmethod
    def check_files_exist_parser():
        description = "Returns true if all files exist"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--files_paths", required=True, type=str, help=f"Comma separated string file list")
        return parser

    @staticmethod
    def check_files_exist(arguments) -> None:
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
        description = "move_file from src_path to dst_path"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--src_file_path", required=True, type=str, help="Source file path")
        parser.add_argument("--dst_file_path", required=True, type=str, help="Destination file path")

        parser.epilog = f"Usage: python3 {__file__} [options]"
        return parser

    @staticmethod
    def action_move_file(arguments):
        arguments_dict = vars(arguments)
        SystemFunctionCommon.move_file(**arguments_dict)

    @staticmethod
    def move_file(src_file_path=None, dst_file_path=None):
        os.makedirs(os.path.dirname(dst_file_path), exist_ok=True)
        shutil.copyfile(src_file_path, dst_file_path)
      
# region compare_files
    @staticmethod
    def action_compare_files_parser():
        description = "compare_files from src_path to dst_path"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--src_file_path", required=True, type=str, help="Source file path")
        parser.add_argument("--dst_file_path", required=True, type=str, help="Destination file path")

        parser.epilog = f"Usage: python3 {__file__} [options]"
        return parser

    @staticmethod
    def action_compare_files(arguments):
        arguments_dict = vars(arguments)
        SystemFunctionCommon.compare_files(**arguments_dict)

    @staticmethod
    def compare_files(src_file_path=None, dst_file_path=None):
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
        description = "perform_comment_line_replacement from src_path in dst_path above comment line"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--src_file_path", required=True, type=str, help="Source file path")
        parser.add_argument("--dst_file_path", required=True, type=str, help="Destination file path")
        parser.add_argument("--comment_line", required=True, type=str, help="Destination file path")

        parser.epilog = f"Usage: python3 {__file__} [options]"
        return parser

    @staticmethod
    def action_perform_comment_line_replacement(arguments):
        arguments_dict = vars(arguments)
        SystemFunctionCommon.perform_comment_line_replacement(**arguments_dict)

    @staticmethod
    def perform_comment_line_replacement(src_file_path=None, dst_file_path=None, comment_line=None):
        replacement_engine = ReplacementEngine()
        with open(src_file_path) as file_handler:
            replacement_string = file_handler.read()

        replacement_engine.perform_comment_line_replacement(dst_file_path, comment_line, replacement_string, keep_comment=True)
# endregion

# region check_systemd_service_status
    @staticmethod
    def action_check_systemd_service_status_parser():
        description = "check_systemd_service_status for specific duration"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--service_name", required=True, type=str, help="Service name to check")
        parser.add_argument("--min_uptime", required=True, type=str, help="Check running duration in seconds")

        parser.epilog = f"Usage: python3 {__file__} [options]"
        return parser

    @staticmethod
    def action_check_systemd_service_status(arguments):
        arguments_dict = vars(arguments)
        SystemFunctionCommon.check_systemd_service_status(**arguments_dict)

    @staticmethod
    def check_systemd_service_status(service_name=None, min_uptime=None):
        pdb.set_trace()
        status_name = "active"
        status_change_seconds_limit = 120
        # 'Active: active (running) since Tue 2022-04-12 18:32:04 GMT; 2h 33min ago'
        service_status_raw = SystemFunctionCommon.get_systemd_service_status(service_name)
        service_status = SystemFunctionCommon.extract_service_status_value(service_status_raw)
        server_time, seconds_duration = SystemFunctionCommon.extract_service_status_times(service_status_raw)

        time_limit = datetime.datetime.now() + datetime.timedelta(seconds=status_change_seconds_limit)
        while service_status != status_name and datetime.datetime.now() < time_limit:
            time.sleep(5)
            service_status_raw = SystemFunctionCommon.get_systemd_service_status(service_name)
            service_status = SystemFunctionCommon.extract_service_status_value(service_status_raw)
            server_time, seconds_duration = SystemFunctionCommon.extract_service_status_times(service_status_raw)

        if service_status != status_name:
            raise TimeoutError(f"service {service_name} did not reach {status_name} in {status_change_seconds_limit} seconds")

        if min_uptime < seconds_duration:
            return True

        time.sleep(min_uptime-seconds_duration)
        service_status_raw = SystemFunctionCommon.get_systemd_service_status(service_name)
        service_status = SystemFunctionCommon.extract_service_status_value(service_status_raw)
        server_time, seconds_duration = SystemFunctionCommon.extract_service_status_times(service_status_raw)
        if service_status != status_name:
            raise TimeoutError(f"service {service_name} seams to be in restart loop")

        if min_uptime < seconds_duration:
            return True

        raise TimeoutError(f"service {service_name} seams to be in restart loop after cause it can not keep {status_name} "
                           f"status for {min_uptime} seconds ")
# endregion

    @staticmethod
    def get_systemd_service_status(service_name):
        command = f"systemctl status {service_name}"
        ret = subprocess.run([command], capture_output=True, shell=True)
        decoded_ret = ret.stdout.decode().strip("\n")
        return decoded_ret

    @staticmethod
    def extract_service_status_value(service_status_raw):
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
        start_date = datetime.datetime.strptime(start_date_str, "%a %Y-%m-%d %H:%M:%S GMT")
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
        duration_lst = duration_string.lower().split(" ")
        hours = 0
        minutes = 0
        seconds = 0

        try:
            index = duration_lst.index("days")
            days = int(duration_lst[index-1])
            duration_lst = duration_lst[:index-1] + duration_lst[index+1:]
        except ValueError:
            days = 0

        try:
            index = duration_lst.index("months")
            months = int(duration_lst[index-1])
            duration_lst = duration_lst[:index-1] + duration_lst[index+1:]
        except ValueError:
            months = 0

        try:
            index = duration_lst.index("years")
            years = int(duration_lst[index-1])
            duration_lst = duration_lst[:index-1] + duration_lst[index+1:]
        except ValueError:
            years = 0

        if duration_lst[-1] != "ago":
            raise RuntimeError(f"{duration_lst} has no 'ago'")

        for duration_part in duration_lst[:-1]:
            if duration_part.endswith("s"):
                seconds = int(duration_part[:-1])
            elif duration_part.endswith("h"):
                hours = int(duration_part[:-1])
            elif duration_part.endswith("min"):
                minutes = int(duration_part[:-3])
            else:
                raise ValueError(f"{duration_part} in {duration_lst}")

        days = days + 365*years + months*30
        return days*24*60*60 + 60*60*hours + minutes*60 + seconds

    @staticmethod
    def extract_service_status_line_raw(service_status_raw):
        for line in service_status_raw.split("\n"):
            line = line.strip(" ")
            if line.startswith("Active:"):
                lst_line = line.split(" ")
                return lst_line

    # region check_file_contains
    @staticmethod
    def action_check_file_contains_parser():
        description = "check_file_contains from src_path in dst_path above comment line"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--src_file_path", required=True, type=str, help="Source file path")
        parser.add_argument("--dst_file_path", required=True, type=str, help="Destination file path")

        parser.epilog = f"Usage: python3 {__file__} [options]"
        return parser

    @staticmethod
    def action_check_file_contains(arguments):
        arguments_dict = vars(arguments)
        SystemFunctionCommon.check_file_contains(**arguments_dict)

    @staticmethod
    def check_file_contains(src_file_path=None, dst_file_path=None):
        replacement_engine = ReplacementEngine()
        with open(src_file_path) as file_handler:
            replacement_string = file_handler.read()

        if not replacement_engine.check_file_contains(dst_file_path, replacement_string):
            raise RuntimeError(f"{src_file_path} -> {dst_file_path}")

# endregion

    @staticmethod
    def action_add_line_to_file_parser():
        description = "add_line_to_file"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--line", required=True, type=str, help="Line to be added")
        parser.add_argument("--file_path", required=True, type=str, help="Path to the file")

        parser.epilog = f"Usage: python3 {__file__} [options]"
        return parser

    @staticmethod
    def action_add_line_to_file(arguments):
        arguments_dict = vars(arguments)
        SystemFunctionCommon.add_line_to_file(**arguments_dict)

    @staticmethod
    def add_line_to_file(line=None, file_path=None):
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
    def provision_file(src_file_path, dst_location):
        """

        @param src_file_path:
        @param dst_location:
        @return: True if copied else False
        """
        if os.path.isdir(dst_location):
            dst_location = os.path.join(dst_location, os.path.basename(src_file_path))
        if os.path.exists(dst_location):
            with open(dst_location, "r") as file_handler:
                dst_content = file_handler.read()
            with open(src_file_path, "r") as file_handler:
                src_content = file_handler.read()

            if src_content == dst_content:
                return False

        shutil.copy(src_file_path, dst_location)
        return True

    def check_local_port(self):
        pdb.set_trace()
        
    def check_remote_port(self):
        pdb.set_trace()
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

SystemFunctionCommon.ACTION_MANAGER.register_action("check_file_contains",
                                                    SystemFunctionCommon.action_check_file_contains_parser,
                                                    SystemFunctionCommon.action_check_file_contains)

SystemFunctionCommon.ACTION_MANAGER.register_action("perform_comment_line_replacement",
                                                    SystemFunctionCommon.action_perform_comment_line_replacement_parser,
                                                    SystemFunctionCommon.action_perform_comment_line_replacement)

SystemFunctionCommon.ACTION_MANAGER.register_action("check_systemd_service_status",
                                                    SystemFunctionCommon.action_check_systemd_service_status_parser,
                                                    SystemFunctionCommon.action_check_systemd_service_status)

if __name__ == "__main__":
    SystemFunctionCommon.ACTION_MANAGER.call_action()

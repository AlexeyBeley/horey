import pdb
import shutil
import subprocess
import uuid
import os
from horey.common_utils.actions_manager import ActionsManager
import argparse


class SystemFunctionCommon:
    ACTION_MANAGER = ActionsManager()

    def __init__(self):
        return

    @staticmethod
    def empty_parser():
        return argparse.ArgumentParser()

    @staticmethod
    def current_subpath(subpath=None):
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
        shutil.copyfile(src_file_path, dst_file_path)

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
            return

        raise RuntimeError(f"{src_file_path} not equals to {dst_file_path}")

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

if __name__ == "__main__":
    SystemFunctionCommon.ACTION_MANAGER.call_action()

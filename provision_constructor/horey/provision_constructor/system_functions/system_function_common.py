import pdb
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

        with open(file_path, "r") as file_handler:
            lines = file_handler.readlines()
            if line in lines:
                return

        with open(file_path, "a") as file_handler:
            file_handler.write(line)

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


if __name__ == "__main__":
    SystemFunctionCommon.ACTION_MANAGER.call_action()

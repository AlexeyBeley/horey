import pdb
import subprocess
import uuid


class SystemFunctionUnittest:
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

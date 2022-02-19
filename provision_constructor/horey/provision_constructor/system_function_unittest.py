import pdb
import subprocess


class SystemFunctionUnittest:
    def __init__(self):
        return

    def run_shell(self, command):
        ret = subprocess.run(command, capture_output=True)
        return ret.stdout.decode()

import os
import pdb
import subprocess

from horey.h_logger import get_logger

logger = get_logger()


class Package:
    def __init__(self, requirement_str):
        self.min_version = None
        self.max_version = None
        self.include_min = None
        self.include_max = None

        if "==" in requirement_str:
            self.name, version = requirement_str.split("==")
            self.min_version = version
            self.max_version = version
            self.include_min = True
            self.include_max = True
        else:
            raise ValueError(requirement_str)


class PipAPI:
    def __init__(self, venv_dir_path=None):
        self.packages = None
        self.venv_dir_path = venv_dir_path

    def init_packages(self):
        response = self.execute("pip freeze")
        lines = response.split("\n")
        objs = []
        for line in lines:
            objs.append(Package(line))
        self.packages = objs

    def execute(self, command):
        if self.venv_dir_path is not None:
            command = f"source {os.path.join(self.venv_dir_path, 'bin/activate')} && {command}"
        ret = subprocess.run([command], capture_output=True, shell=True)
        return ret.stdout.decode().strip("\n")

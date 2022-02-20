import os
import pdb
import subprocess

from horey.h_logger import get_logger

logger = get_logger()


class Requirement:
    def __init__(self, requirement_str):
        self.name = None
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
        elif ">=" in requirement_str:
            self.name, version = requirement_str.split(">=")
            self.min_version = version
            self.include_min = True
        else:
            pdb.set_trace()
            raise ValueError(requirement_str)


class Package:
    def __init__(self, str_src):
        if "==" in str_src:
            self.name, self.version = str_src.split("==")
        else:
            raise ValueError(f"'{str_src}'")


class PipAPI:
    def __init__(self, venv_dir_path=None, horey_repo_path=None):
        self.horey_repo_path = horey_repo_path
        self.packages = None
        self.venv_dir_path = venv_dir_path

    def init_packages(self):
        response = self.execute("pip freeze")
        lines = response.split("\n")
        objs = []
        for line in lines:
            if len(line) == 0:
                continue
            objs.append(Package(line))
        self.packages = objs

    def execute(self, command):
        if self.venv_dir_path is not None:
            command = f"source {os.path.join(self.venv_dir_path, 'bin/activate')} && {command}"
        ret = subprocess.run([command], capture_output=True, shell=True)
        return ret.stdout.decode().strip("\n")

    def install_requirements(self, requirements_file_path):
        requirements = self.compose_requirements_recursive(requirements_file_path)
        if not requirements:
            return

        for requirement in requirements:
            if self.requirement_satisfied(requirement):
                continue
            self.install_requirement(requirement)

    def install_requirement(self, requirement):
        if requirement.name.startswith("horey."):
            return self.install_horey_requirement(requirement)
        pdb.set_trace()
        self.execute("pip install ")

    def install_horey_requirement(self, requirement):
        _, name = requirement.name.split(".")
        ret = self.execute(f"cd {self.horey_repo_path} && make install_wheel-{name}")
        if ret.split("\n")[-1] != f"done installing {name}":
            raise RuntimeError(f"Could not install {name} from source code:\n {ret}")

    def requirement_satisfied(self, requirement):
        self.init_packages()
        for package in self.packages:
            if package.name == requirement.name:
                pdb.set_trace()
        return False

    def compose_requirements_recursive(self, requirements_file_path):
        ancestor_requirements = []
        self._compose_requirements_recursive_helper(requirements_file_path, ancestor_requirements)
        return ancestor_requirements

    def _compose_requirements_recursive_helper(self, requirements_file_path, ancestor_requirements):
        requirements = self.init_requirements(requirements_file_path)
        for requirement in requirements:
            if requirement in ancestor_requirements:
                pdb.set_trace()
                raise NotImplementedError()
            ancestor_requirements.insert(0, requirement)

            if requirement.name.startswith("horey."):
                horey_package_requirements = self.get_horey_package_requirements(requirement.name)
                if horey_package_requirements:
                    pdb.set_trace()
                    raise NotImplementedError()
            else:
                pdb.set_trace()
                raise NotImplementedError()

    def init_requirements(self, requirements_file_path):
        if not os.path.exists(requirements_file_path):
            return []

        requirements = []

        with open(requirements_file_path, "r") as file_handler:
            lines = [line.strip("\n") for line in file_handler.readlines() if line != "\n"]

        for line in lines:
            requirements.append(Requirement(line))

        return requirements

    def get_horey_package_requirements(self, package_name):
        _, package_name = package_name.split(".")
        horey_package_requirements_path = os.path.join(self.horey_repo_path, package_name, "requirements.txt")
        return self.init_requirements(horey_package_requirements_path)

import os
import pdb
import subprocess
import uuid

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

    def check_version_requirements(self, requirement: Requirement):
        self_int_version_lst = [int(sub_ver) for sub_ver in self.version.split(".")]

        return self.check_version_min_requirement(requirement, self_int_version_lst) and \
               self.check_version_max_requirement(requirement, self_int_version_lst)

    def check_version_min_requirement(self, requirement, self_int_version_lst):
        if requirement.min_version == self.version:
            if requirement.include_min:
                return True
            return False

        requirement_int_version_lst = [int(sub_ver) for sub_ver in requirement.min_version.split(".")]
        for index, package_sub_ver_value in enumerate(self_int_version_lst):
            if package_sub_ver_value > requirement_int_version_lst[index]:
                break
            if package_sub_ver_value < requirement_int_version_lst[index]:
                return False

        return True

    def check_version_max_requirement(self, requirement, self_int_version_lst):
        if requirement.max_version is None:
            return True

        if requirement.max_version == self.version:
            if requirement.include_max:
                return True
            return False

        raise NotImplementedError("todo:")

        requirement_int_version_lst = [int(sub_ver) for sub_ver in requirement.max_version.split(".")]
        for index, package_sub_ver_value in enumerate(self_int_version_lst):
            if package_sub_ver_value < requirement_int_version_lst[index]:
                break
            if package_sub_ver_value > requirement_int_version_lst[index]:
                return False

        return True


class PipAPI:
    REQUIREMENTS = dict()

    def __init__(self, venv_dir_path=None, horey_repo_path=None):
        self.horey_repo_path = horey_repo_path
        self.packages = None
        self.venv_dir_path = venv_dir_path

    def init_packages(self):
        response = self.execute("pip3.8 freeze")
        lines = response.split("\n")
        objs = []
        for line in lines:
            if len(line) == 0:
                continue
            objs.append(Package(line))
        self.packages = objs

    def execute(self, command):
        file_name = None
        if self.venv_dir_path is not None:
            file_name = f"tmp-{str(uuid.uuid4())}.sh"
            with open(file_name, "w") as file_handler:
                file_handler.write(f"source {os.path.join(self.venv_dir_path, 'bin/activate')}\n{command}")
                command = f"/bin/bash {file_name}"
        ret = subprocess.run([command], capture_output=True, shell=True)

        if file_name:
            os.remove(file_name)

        return ret.stdout.decode().strip("\n")

    def install_requirements(self, requirements_file_path):
        self.init_packages()
        self.compose_requirements_recursive(requirements_file_path)

        if not self.REQUIREMENTS:
            return
        for _, requirement in reversed(self.REQUIREMENTS.items()):
            if self.requirement_satisfied(requirement):
                continue
            self.install_requirement(requirement)

    def get_installed_packages(self):
        ret = self.execute("pip3.8 freeze")
        if not ret:
            return []
        packages_lines = ret.split("\n")
        return [Package(line) for line in packages_lines]

    def install_requirement(self, requirement: Requirement):
        if requirement.name.startswith("horey."):
            return self.install_horey_requirement(requirement)

        if requirement.min_version is None:
            raise NotImplementedError(requirement.__dict__)
        if requirement.min_version != requirement.max_version:
            raise NotImplementedError(requirement.__dict__)

        self.execute(f"pip3.8 install {requirement.name}=={requirement.min_version}")

    def install_horey_requirement(self, requirement):
        _, name = requirement.name.split(".")
        ret = self.execute(f"cd {self.horey_repo_path} && make install_wheel-{name}")
        lines = ret.split("\n")

        index = -2 if "Leaving directory" in lines[-1] else -1
        if lines[index] != f"done installing {name}":
            raise RuntimeError(f"Could not install {name} from source code:\n {ret}")

    def requirement_satisfied(self, requirement: Requirement):
        for package in self.packages:
            if package.name.replace("_", "-") != requirement.name.replace("_", "-"):
                continue
            return package.check_version_requirements(requirement)

        return False

    def compose_requirements_recursive(self, requirements_file_path):
        requirements = self.init_requirements_raw(requirements_file_path)
        for requirement in requirements:
            if requirement.name in self.REQUIREMENTS:
                self.update_existing_requirement(requirement)
                continue

            self.REQUIREMENTS[requirement.name] = requirement

            if requirement.name.startswith("horey."):
                _, package_name = requirement.name.split(".")
                horey_package_requirements_path = os.path.join(self.horey_repo_path, package_name, "requirements.txt")
                self.compose_requirements_recursive(horey_package_requirements_path)
            else:
                self.REQUIREMENTS[requirement.name] = requirement

    @staticmethod
    def init_requirements_raw(requirements_file_path):
        if not os.path.exists(requirements_file_path):
            return []

        requirements = []

        with open(requirements_file_path, "r") as file_handler:
            lines = [line.strip("\n") for line in file_handler.readlines() if line != "\n"]

        for line in lines:
            requirements.append(Requirement(line))

        return requirements

    def update_existing_requirement(self, requirement: Requirement):
        current = self.REQUIREMENTS[requirement.name]
        if current.min_version != requirement.min_version:
            pdb.set_trace()
            raise NotImplementedError()
        if current.include_min != requirement.include_min:
            pdb.set_trace()
            raise NotImplementedError()
        if current.max_version != requirement.max_version:
            pdb.set_trace()
            raise NotImplementedError()
        if current.include_max != requirement.include_max:
            pdb.set_trace()
            raise NotImplementedError()

    def get_horey_package_requirements(self, package_name):
        _, package_name = package_name.split(".")
        horey_package_requirements_path = os.path.join(self.horey_repo_path, package_name, "requirements.txt")
        return self.init_requirements_raw(horey_package_requirements_path)

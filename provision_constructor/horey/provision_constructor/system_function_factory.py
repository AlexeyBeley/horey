import pdb
import os
import shutil
import sys
import uuid

from horey.pip_api.pip_api import PipAPI
from horey.h_logger import get_logger

logger = get_logger()

class SystemFunctionFactory:
    REGISTERED_FUNCTIONS = dict()

    @staticmethod
    def register(cls):
        name = cls.__module__[len("horey.provision_constructor.system_functions."):]
        package_name = name[:name.rfind(".")]
        logger.info(f"Registering system function {package_name}")
        SystemFunctionFactory.REGISTERED_FUNCTIONS[package_name] = cls

    class SystemFunction:
        HOREY_REPO_PATH = None

        def __init__(self, root_deployment_dir, provisioner_script_name, force=False):
            self.provisioner_script_name = provisioner_script_name
            self.root_deployment_dir = root_deployment_dir
            self.submodules = self.__module__[len("horey.provision_constructor.system_functions."):self.__module__.rfind(".")]
            self.deployment_dir = os.path.join(root_deployment_dir, *self.submodules.split("."))
            self.pip_api = PipAPI(venv_dir_path=os.path.join(root_deployment_dir, "_venv"), horey_repo_path=self.HOREY_REPO_PATH)
            self.add_system_function(force=force)

        def add_system_function(self, force=False):
            self.move_system_function_to_deployment_dir()
            self.add_system_function_to_provisioner_script(force=force)

        def move_system_function_to_deployment_dir(self):
            shutil.copytree(os.path.dirname(sys.modules[self.__module__].__file__), self.deployment_dir, dirs_exist_ok=True)
            requirements_path = os.path.join(self.deployment_dir, "requirements.txt")
            self.pip_api.install_requirements(requirements_path)

        def add_system_function_to_provisioner_script(self, force=False):
            system_functions_provisioners = []
            system_functions_unittests = []
            system_functions_chmods =[]
            for file_name in os.listdir(self.deployment_dir):
                if file_name.startswith("provision_"):
                    script_path = os.path.join(self.deployment_dir, file_name)
                    relative_script_path = os.path.relpath(script_path, start=self.root_deployment_dir)
                    system_functions_chmods.append(f"sudo chmod +x {relative_script_path}\n")
                    system_functions_provisioners.append("sudo " + relative_script_path + "\n")
                elif file_name.startswith("test_"):
                    script_path = os.path.join(self.deployment_dir, file_name)
                    relative_script_path = os.path.relpath(script_path, start=self.root_deployment_dir)
                    system_functions_chmods.append(f"sudo chmod +x {relative_script_path}\n")
                    system_functions_unittests.append("sudo " + relative_script_path + "\n")

            provisioner_script_path = os.path.join(self.root_deployment_dir, self.provisioner_script_name)
            with open(provisioner_script_path, "a") as file_handler:
                file_handler.write(f"function main_{self.submodules}" + " {\n")
                file_handler.write(self.add_indentation("#---------CHANGE_MODES---------\n", 1))
                file_handler.writelines(self.add_indentation(system_functions_chmods, 1))
                if not force:
                    file_handler.write(self.add_indentation("#------UNIT_TESTS-------------\n", 1))
                    preprovision_tests_lines = self.generate_preprovisioning_tests(system_functions_unittests)
                    file_handler.writelines(self.add_indentation(preprovision_tests_lines, 2))

                file_handler.writelines(self.add_indentation(system_functions_provisioners, 1))
                file_handler.writelines(self.add_indentation(system_functions_unittests, 1))
                file_handler.write("}\n"+f"#---endof main_{self.submodules}---------\n")

        def generate_preprovisioning_tests(self, system_functions_unittests):
            function_name = f"unittests_{self.submodules}"
            ret = [f"function {function_name} ()" + "  { \n"]
            for command in system_functions_unittests:
                ret.append(command)
                ret.append("result=$?\n")
                ret.append("if [[ \"${result}\" -ne 0 ]]; then return ${result}; fi\n")

            ret.append("return 0\n")
            ret.append("}\n\n")

            ret.append(f"set +e\n")
            ret.append(f"{function_name}\n")

            ret.append("result=$?\n")
            ret.append(f"set -e\n")
            ret.append("if [[ \"${result}\" -eq 0 ]]; then exit 0; fi\n")

            return ret

        def add_indentation(self, src_obj, count):
            if isinstance(src_obj, list):
                return [self.add_indentation(line, count) for line in src_obj]
            elif not isinstance(src_obj, str):
                raise ValueError(src_obj)

            if not src_obj.startswith("\n"):
                src_obj = " "*4*count + src_obj
            src_obj = src_obj.replace("\n", "    \n")
            return src_obj

        def add_system_function_common(self):
            """
            Add system unit test base class with it's requirements
            @return:
            """
            system_functions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system_functions")
            shutil.copy(os.path.join(system_functions_dir, "system_function_common.py"), self.deployment_dir)
            self.pip_api.install_requirements(os.path.join(system_functions_dir, "requirements.txt"))

        def add_system_function_common(self):
            """
            Add system unit test base class with it's requirements
            @return:
            """
            system_functions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system_functions")
            shutil.copy(os.path.join(system_functions_dir, "system_function_common.py"), self.deployment_dir)
            self.pip_api.install_requirements(os.path.join(system_functions_dir, "requirements.txt"))

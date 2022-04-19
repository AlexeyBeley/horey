import pdb
import os
import shutil
import sys

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

        def __init__(self, root_deployment_dir, provisioner_script_name, force=False, trigger_on_any_provisioned=None, explicitly_add_system_function=True):
            """

            @param root_deployment_dir:
            @param provisioner_script_name:
            @param force:
            @param trigger_on_any_provisioned:
            @param explicitly_add_system_function: for example template_provisioner.py won't be added if added before replacement_engine finished its work.
            """
            self.provisioner_script_name = provisioner_script_name
            self.root_deployment_dir = root_deployment_dir
            self.submodules = self.__module__[len("horey.provision_constructor.system_functions."):self.__module__.rfind(".")]
            self.deployment_dir = os.path.join(root_deployment_dir, *self.submodules.split("."))
            os.makedirs(self.deployment_dir, exist_ok=True)
            self.pip_api = PipAPI(venv_dir_path=os.path.join(root_deployment_dir, "_venv"), horey_repo_path=self.HOREY_REPO_PATH)
            self.move_system_function_to_deployment_dir()
            if explicitly_add_system_function:
                self.add_system_function(force=force, trigger_on_any_provisioned=trigger_on_any_provisioned)

        def add_system_function(self, force=False, trigger_on_any_provisioned=None):
            self.install_system_function_requirements()
            self.add_system_function_to_provisioner_script(force=force, trigger_on_any_provisioned=trigger_on_any_provisioned)

        def move_system_function_to_deployment_dir(self):
            shutil.copytree(os.path.dirname(sys.modules[self.__module__].__file__), self.deployment_dir, dirs_exist_ok=True)

        def install_system_function_requirements(self):
            requirements_path = os.path.join(self.deployment_dir, "requirements.txt")
            self.pip_api.install_requirements(requirements_path)

        def add_system_function_to_provisioner_script(self, force=False, trigger_on_any_provisioned=None):
            system_functions_provisioners = []
            system_functions_unittests = []
            system_functions_chmods = []
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
                    system_functions_unittests.append(relative_script_path + "\n")

            provisioner_script_path = os.path.join(self.root_deployment_dir, self.provisioner_script_name)
            main_function_name = f"main_{self.submodules}"
            with open(provisioner_script_path, "a") as file_handler:
                file_handler.write(f"function {main_function_name}()" + " {\n")
                file_handler.write(self.add_indentation("#---------CHANGE_MODES---------\n", 1))
                file_handler.writelines(self.add_indentation(system_functions_chmods, 1))
                if not force:
                    file_handler.write(self.add_indentation("#------UNIT_TESTS-------------\n", 1))
                    preprovision_tests_lines = self.generate_preprovisioning_tests(system_functions_unittests)
                    file_handler.writelines(self.add_indentation(preprovision_tests_lines, 2))

                file_handler.write(self.add_indentation("#---------RUN----------\n", 1))
                file_handler.writelines(self.add_indentation(system_functions_provisioners, 1))
                file_handler.write(self.add_indentation(f"ProvisionedSystemFunctions+=(\"{self.submodules}\")\n", 1))

                file_handler.writelines(self.add_indentation(system_functions_unittests, 1))
                file_handler.write("}\n"+f"#---endof main_{self.submodules}---------\n")
                if trigger_on_any_provisioned:
                    file_handler.write(self.generate_trigger_on_any_provisioned(trigger_on_any_provisioned, main_function_name))
                else:
                    file_handler.write(f"{main_function_name}\n\n")
            logger.info(f"Finished generating '{provisioner_script_path}'")

        def generate_trigger_on_any_provisioned(self, trigger_on_any_provisioned, main_function_name):
            lst_ret = []
            check_function_name = f"run_{main_function_name}_check_if_any"
            lst_ret.append(f"function {check_function_name}()"+"{")
            lst_ret.append(self.add_indentation(f"set +e", 1))
            for check_provisioned in trigger_on_any_provisioned:
                lst_ret.append(self.add_indentation("contains \"${ProvisionedSystemFunctions[@]}\"" + f" \"{check_provisioned}\"", 1))
                lst_ret.append(self.add_indentation("result=$?", 1))
                lst_ret.append(self.add_indentation("if [[ \"${result}\" -eq 0 ]]; then return 0; fi\n", 1))

            lst_ret.append(self.add_indentation("return 1", 1))
            lst_ret.append("}")
            lst_ret.append("set +e")
            lst_ret.append(check_function_name)
            lst_ret.append("result=$?")
            lst_ret.append("set -e")
            lst_ret.append("if [[ \"${result}\" -eq 0 ]]; then " + f"{main_function_name}; fi")
            return "\n".join(lst_ret)

        def generate_preprovisioning_tests(self, system_functions_unittests):
            function_name = f"unittests_{self.submodules}"
            ret = [f"function {function_name}()" + "  { \n"]
            for command in system_functions_unittests:
                ret.append(self.add_indentation(command, 1))
                ret.append(self.add_indentation("result=$?\n", 1))
                ret.append(self.add_indentation("if [[ \"${result}\" -ne 0 ]]; then return ${result}; fi\n", 1))

            ret.append(self.add_indentation("return 0\n", 1))
            ret.append("}\n\n")

            ret.append(f"set +e\n")
            ret.append(f"{function_name}\n")

            ret.append("result=$?\n")
            ret.append(f"set -e\n")
            ret.append("if [[ \"${result}\" -eq 0 ]]; then return 0; fi\n")

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
            shutil.copy(os.path.join(system_functions_dir, "system_function_common.py"), os.path.join(self.deployment_dir, "system_function_common.py"))
            self.pip_api.install_requirements(os.path.join(system_functions_dir, "requirements.txt"))

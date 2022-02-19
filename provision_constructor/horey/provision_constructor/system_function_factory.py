import pdb
import os
import shutil
import sys
import uuid

from horey.pip_api.pip_api import PipAPI

class SystemFunctionFactory:
    REGISTERED_FUNCTIONS = dict()

    @staticmethod
    def register(cls):
        name = cls.__module__
        package_name = name[:name.rfind(".")]
        SystemFunctionFactory.REGISTERED_FUNCTIONS[package_name] = cls

    class SystemFunction:
        def __init__(self, root_deployment_dir, provisioner_script_name):
            self.provisioner_script_name = provisioner_script_name
            self.root_deployment_dir = root_deployment_dir
            self.deployment_dir = os.path.join(root_deployment_dir, self.__module__[self.__module__.rfind(".")+1:])
            self.pip_api = PipAPI(venv_dir_path=os.path.join(root_deployment_dir, "venv"))

        def move_system_function_to_deployment_dir(self):
            shutil.copytree(os.path.dirname(sys.modules[self.__module__].__file__), self.deployment_dir)
            requirements_path = os.path.join(self.deployment_dir, "requirements.txt")
            horey_requirements_path = os.path.join(self.deployment_dir, "horey_requirements.txt")
            self.pip_api.install_requirements(requirements_path)
            pdb.set_trace()

        def add_system_function_to_provisioner_script(self, force=False):
            system_functions_provisioners = []
            system_functions_unittests = []
            system_functions_chmods =[]

            for file_name in os.listdir(self.deployment_dir):
                if file_name.startswith("provision_"):
                    script_path = os.path.join(self.deployment_dir, file_name)
                    relative_script_path = os.path.relpath(script_path, start=self.root_deployment_dir)
                    system_functions_chmods.append(f"chmod +x {relative_script_path}\n")
                    system_functions_provisioners.append(relative_script_path+"\n")
                elif file_name.startswith("test_"):
                    script_path = os.path.join(self.deployment_dir, file_name)
                    relative_script_path = os.path.relpath(script_path, start=self.root_deployment_dir)
                    system_functions_chmods.append(f"chmod +x {relative_script_path}\n")
                    system_functions_unittests.append(relative_script_path+"\n")

            provisioner_script_path = os.path.join(self.root_deployment_dir, self.provisioner_script_name)
            with open(provisioner_script_path, "a") as file_handler:
                file_handler.writelines(system_functions_chmods)
                file_handler.write("------------------------------\n")
                if not force:
                    preprovision_tests_lines = self.generate_preprovisioning_tests(system_functions_unittests)
                    file_handler.writelines(preprovision_tests_lines)
                file_handler.writelines(system_functions_provisioners)
                file_handler.writelines(system_functions_unittests)
                file_handler.write("------------------------------\n")

        def generate_preprovisioning_tests(self, system_functions_unittests):
            function_name = f"tests_{uuid.uuid4()}"
            ret = [f"function {function_name} ()" + "  { \n    set +e\n"]
            for command in system_functions_unittests:
                ret.append("    " + command)
                ret.append("    result=$?\n"
                           "    if [ \"${result}\" -ne 0 ]\n"
                           "    then\n"
                           "        set -e\n"
                           "        return ${result}\n"
                           "    fi\n\n")

            ret.append("    return 0\n}\n\n")

            ret.append(f"{function_name}\n")

            ret.append("result=$?\n"
                       "if [ \"${result}\" -eq 0 ]\n"
                       "then\n"
                       "    exit 0\n"
                       "fi\n\n")

            return ret

        def add_system_function_unittest(self):
            """
            Add system unit test base class with it's requirements
            @return:
            """
            move("/Users/alexey.beley/private/horey/provision_constructor/horey/provision_constructor/system_functions/system_function_unittest.py",
                 self.deployment_dir
                 )
            self.pip_api.install_requirements("/Users/alexey.beley/private/horey/provision_constructor/horey/provision_constructor/system_functions/requirements.txt")
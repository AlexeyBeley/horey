import pdb
import os
import shutil
import sys


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

        def move_system_function_to_deployment_dir(self):
            shutil.copytree(os.path.dirname(sys.modules[self.__module__].__file__), self.deployment_dir)

        def add_system_function_to_provisioner_script(self):
            system_function_provisioners = []
            system_functions_unittests = []

            for file_name in os.listdir(self.deployment_dir):
                if file_name.startswith("provision_"):
                    script_path = os.path.join(self.deployment_dir, file_name)
                    relative_script_path = os.path.relpath(script_path, start=self.root_deployment_dir)
                    system_function_provisioners.append(f"chmod +x {relative_script_path}\n")
                    system_function_provisioners.append(relative_script_path+"\n")
                elif file_name.startswith("test_"):
                    script_path = os.path.join(self.deployment_dir, file_name)
                    relative_script_path = os.path.relpath(script_path, start=self.root_deployment_dir)
                    system_functions_unittests.append(f"chmod +x {relative_script_path}\n")
                    system_functions_unittests.append(relative_script_path+"\n")

            provisioner_script_path = os.path.join(self.root_deployment_dir, self.provisioner_script_name)
            with open(provisioner_script_path, "a") as file_handler:
                file_handler.writelines(system_function_provisioners)
                file_handler.writelines(system_functions_unittests)
                file_handler.write("------------------------------\n")






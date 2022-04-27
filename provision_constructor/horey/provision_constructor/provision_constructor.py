#!/usr/bin/python
import pdb

from horey.provision_constructor.system_functions import *
import os
import shutil
import subprocess


class ProvisionConstructor:
    PROVISIONER_SCRIPT_NAME = "main.sh"
    PROVISIONER_CONSTRUCTOR_SUB_DIR = "provision_constructor_deployment_dir"

    def __init__(self, base_dir_path, horey_repo_path=None):
        self.provisioned_system_functions = []
        self.horey_repo_path = horey_repo_path
        SystemFunctionFactory.SystemFunction.HOREY_REPO_PATH = self.horey_repo_path

        self.deployment_dir = os.path.join(base_dir_path, ProvisionConstructor.PROVISIONER_CONSTRUCTOR_SUB_DIR)
        if os.path.exists(self.deployment_dir):
            shutil.rmtree(self.deployment_dir)

        os.makedirs(self.deployment_dir, exist_ok=True)
        shutil.copyfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bash_tools", "list_contains.sh"),
                        os.path.join(self.deployment_dir, "list_contains.sh"))
        with open(os.path.join(self.deployment_dir, ProvisionConstructor.PROVISIONER_SCRIPT_NAME), "w") as file_handler:
            file_handler.writelines(["#!/bin/bash\n",
                                     "set -xe\n\n",
                                     'SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"\n',
                                     'cd "${SCRIPT_DIR}"\n\n',
                                     'source list_contains.sh\n',
                                     "ProvisionedSystemFunctions=()\n",
                                     "#------------------------------\n"])

        venv_path = os.path.join(self.deployment_dir, "_venv")
        os.makedirs(venv_path, exist_ok=True)
        subprocess.run([f"python3.8 -m venv {venv_path}"], shell=True)

    def add_system_function(self, system_function_name, **kwargs):
        self.check_provisioned_ancestor(system_function_name)
        SystemFunctionFactory.REGISTERED_FUNCTIONS[system_function_name](self.deployment_dir,
                                                                    ProvisionConstructor.PROVISIONER_SCRIPT_NAME,
                                                                    **kwargs)
        self.provisioned_system_functions.append(system_function_name)

    def check_provisioned_ancestor(self, system_function_name):
        if "." in system_function_name:
            ancestor_name = system_function_name[:system_function_name.rfind(".")]
            if ancestor_name not in self.provisioned_system_functions:
                raise RuntimeError(f"'{system_function_name}' ancestor '{ancestor_name}' was not found")

    def generate_provision_constructor_bootstrap_script(self, remote_deployment_dir_path, script_path):
        pdb.set_trace()
        # cp -r  _venv_tmp/lib/python3.8/site-packages/* _venv/lib/python3.8/site-packages/
        # install python3.8
        # install git
        # install pip3.8
        # install make
        # make install
        # apt-get install python3-venv -y

        #download_horey

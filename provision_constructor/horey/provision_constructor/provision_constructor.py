#!/usr/bin/python
import pdb

from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.provision_constructor.system_functions import *
import os
import shutil
import subprocess


class ProvisionConstructor:
    PROVISIONER_SCRIPT_NAME = "main.sh"
    PROVISIONER_CONSTRUCTOR_SUB_DIR = "provision_constructor_deployment_dir"

    def __init__(self, base_dir_path, horey_repo_path=None):
        self.horey_repo_path = horey_repo_path
        SystemFunctionFactory.SystemFunction.HOREY_REPO_PATH = self.horey_repo_path

        self.deployment_dir = os.path.join(base_dir_path, ProvisionConstructor.PROVISIONER_CONSTRUCTOR_SUB_DIR)
        if os.path.exists(self.deployment_dir):
            shutil.rmtree(self.deployment_dir)

        os.makedirs(self.deployment_dir, exist_ok=True)
        with open(os.path.join(self.deployment_dir, ProvisionConstructor.PROVISIONER_SCRIPT_NAME), "w") as file_handler:
            file_handler.writelines(["#!/bin/bash\n",
                                     "set -xe\n\n",
                                     'SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"\n',
                                     'cd "${SCRIPT_DIR}"\n\n',
                                     "------------------------------\n"])

        venv_path = os.path.join(self.deployment_dir, "_venv")
        os.makedirs(venv_path, exist_ok=True)
        subprocess.run([f"python3.8 -m venv {venv_path}"], shell=True)

    def add_system_function(self, module, **kwargs):
        SystemFunctionFactory.REGISTERED_FUNCTIONS[module.__name__](self.deployment_dir,
                                                                    ProvisionConstructor.PROVISIONER_SCRIPT_NAME,
                                                                    **kwargs)

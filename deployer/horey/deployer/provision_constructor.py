#!/usr/bin/python
import pdb

from horey.deployer.system_function_factory import SystemFunctionFactory
from horey.deployer.system_functions import *
import os
import shutil


class ProvisionConstructor:
    def __init__(self, base_dir_path):
        self.deployment_dir = os.path.join(base_dir_path, "provision_constructor_deployment_dir")
        if os.path.exists(self.deployment_dir):
            shutil.rmtree(self.deployment_dir)

        os.makedirs(self.deployment_dir, exist_ok=True)

    def add_system_function(self, module, **kwargs):
        SystemFunctionFactory.REGISTERED_FUNCTIONS[module.__name__](self.deployment_dir, **kwargs)

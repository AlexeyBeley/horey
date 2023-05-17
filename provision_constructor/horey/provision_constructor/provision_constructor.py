#!/usr/bin/python
"""
Provision constructor.
"""
import os

# pylint: disable= wildcard-import, unused-wildcard-import
from horey.provision_constructor.system_functions import *
from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.h_logger import get_logger

logger = get_logger()


class ProvisionConstructor:
    """
    Main class.

    """

    PROVISIONER_CONSTRUCTOR_SUB_DIR = "provision_constructor_deployment_dir"
    PROVISION_CONSTRUCTOR_BOOTSTRAP_SCRIPT_NAME = (
        "provision_constructor_bootstrap_script.sh"
    )

    def __init__(self):
        self.provisioned_system_functions = []
        self.horey_repo_path = None
        self.deployment_dir = None

    def provision_system_function(self, system_function_name, **kwargs):
        """
        Init and run system_function provision method.

        @param system_function_name:
        @param kwargs:
        @return:
        """

        force = False
        if "force" in kwargs:
            force = kwargs.get("force")
            del kwargs["force"]

        upgrade = False
        if "upgrade" in kwargs:
            force = kwargs.get("upgrade")
            del kwargs["upgrade"]

        logger.info(f"Initializing system_function '{system_function_name}' with args: {kwargs}")
        system_function = SystemFunctionFactory.REGISTERED_FUNCTIONS[
            system_function_name
        ](self.deployment_dir, force, upgrade, **kwargs)
        if system_function.validate_provisioned_ancestor:
            self.check_provisioned_ancestor(system_function_name)

        system_function.provision()
        self.provisioned_system_functions.append(system_function_name)

    def check_provisioned_ancestor(self, system_function_name):
        """
        Check if the system_function's ancestor was provisioned.

        @param system_function_name:
        @return:
        """

        if "." in system_function_name:
            ancestor_name = system_function_name[: system_function_name.rfind(".")]
            if ancestor_name not in self.provisioned_system_functions:
                raise RuntimeError(
                    f"'{system_function_name}' ancestor '{ancestor_name}' was not found"
                )

    @staticmethod
    def generate_provision_constructor_bootstrap_script(
        remote_deployment_dir_path, script_path
    ):
        """
        Provision constructor remote machine bootstrap script.

        @param remote_deployment_dir_path:
        @param script_path:
        @return:
        """

        with open(
            os.path.join(remote_deployment_dir_path, script_path), "w", encoding="utf-8"
        ) as file_handler:
            file_handler.write(
                "#!/bin/bash\n"
                "set -ex\n"
                "sudo apt update\n"
                "sudo apt install python3.10-dev -yqq\n"
                "sudo apt install python3-venv -yqq\n"
                "wget https://bootstrap.pypa.io/get-pip.py\n"
                "sudo python3.10 get-pip.py\n"
                "set +e\n"
                "sudo ln /usr/bin/pip3.10 /home/ubuntu/.local/bin/pip3\n"
                "sudo ln /usr/bin/pip3.10 /usr/local/bin/pip3\n"
                "sudo ln /usr/bin/python3.10 /home/ubuntu/.local/bin/python\n"
                "sudo ln /usr/bin/python3.10 /usr/local/bin/python\n"
                "python -m pip install setuptools>=54.1.2\n"
                "set -e\n"
                "sudo apt install git -yqq\n"
                "sudo apt install make -yqq\n"
                "sudo rm -rf horey\n"
                "git clone https://github.com/AlexeyBeley/horey.git\n"
                "cd horey\n"
                "make recursive_install_from_source-provision_constructor\n"
                "cd .."
            )

        # download_horey

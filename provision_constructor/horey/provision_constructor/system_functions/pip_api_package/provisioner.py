"""
Provision pip_api packages - regular packages or multi-package repos

"""

import os.path
from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.h_logger import get_logger
from horey.pip_api.pip_api import PipAPI
from horey.pip_api.pip_api_configuration_policy import PipAPIConfigurationPolicy

logger = get_logger()


# pylint: disable= abstract-method
@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """
    Provisioner class.

    """

    # pylint: disable= too-many-arguments
    def __init__(
        self,
        deployment_dir,
        force, upgrade,
        requirements_file_path=None,
        pip_api_configuration_file=None,
    ):
        super().__init__(os.path.dirname(os.path.abspath(__file__)), force, upgrade)
        self.deployment_dir = deployment_dir
        self.requirements_file_path = requirements_file_path

        configuration = PipAPIConfigurationPolicy()
        configuration.configuration_file_full_path = pip_api_configuration_file
        configuration.init_from_file()
        self.pip_api = PipAPI(configuration=configuration)

    def _provision(self):
        """
        Provision all packages.

        @return:
        """

        self.pip_api.install_requirements_from_file(self.requirements_file_path, force_reinstall=self.force)

    def test_provisioned(self):
        """
        Test the system_function was provisioned.

        :return:
        """
        requirements = self.pip_api.init_requirements_raw(self.requirements_file_path)

        str_ret = ""
        for requirement in requirements:
            if not self.pip_api.requirement_satisfied(requirement):
                str_ret += requirement.str_src + "\n"
        if str_ret:
            raise RuntimeError(f"Following requirements were not met: {str_ret}")

        return True

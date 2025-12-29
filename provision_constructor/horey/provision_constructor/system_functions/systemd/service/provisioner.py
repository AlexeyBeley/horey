"""
Provision systemd service

"""

import os.path
from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.h_logger import get_logger

logger = get_logger()


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """
    Provisioner class.

    """

    # pylint: disable=too-many-arguments
    def __init__(self, deployment_dir, force, upgrade, name=None, unit_file_location=None, **kwargs):
        super().__init__(force, upgrade, **kwargs)
        self.validate_provisioned_ancestor = False
        self.deployment_dir = deployment_dir

        self.name = name
        self.unit_file_name = f"{name}.service"

        self.unit_file_location = None

        if unit_file_location is not None:
            if os.path.isfile(unit_file_location):
                if not unit_file_location.endswith(self.unit_file_name):
                    raise ValueError(
                        f"{unit_file_location} is not of form: {self.unit_file_name}"
                    )
                self.unit_file_location = os.path.dirname(unit_file_location)
            else:
                if not os.path.exists(
                    os.path.join(unit_file_location, self.unit_file_name)
                ):
                    raise RuntimeError(
                        f"Unit file does not exist: {os.path.join(unit_file_location, self.unit_file_name)}"
                    )
                self.unit_file_location = unit_file_location

    def test_provisioned(self):
        """
        Test service is provisioned.

        @return:
        """

        if not self.check_file_provisioned(
            os.path.join(self.unit_file_location, self.unit_file_name),
            os.path.join("/etc/systemd/system/", self.unit_file_name),
        ):
            return False

        return self.check_systemd_service_status(service_name=self.name, min_uptime=60)

    def _provision(self):
        """
        Provision service.

        @return:
        """

        self.provision_file(
            os.path.join(self.unit_file_location, self.unit_file_name),
            os.path.join("/etc/systemd/system/", self.unit_file_name),
            sudo=True,
        )
        self.run_bash("sudo systemctl daemon-reload")
        self.run_bash(f"sudo systemctl restart {self.name}")
        self.run_bash(f"sudo systemctl enable {self.name}")

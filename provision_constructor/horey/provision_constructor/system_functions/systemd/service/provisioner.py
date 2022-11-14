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

    def __init__(self, deployment_dir, name=None, unit_file_location=None):
        super().__init__(os.path.dirname(os.path.abspath(__file__)))
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

    def provision(self, force=False):
        """
        Provision the service.

        @param force:
        @return: True if provisioning ran, False if skipped.
        """

        if not force and self.test_provisioned():
            logger.info(f"Skipping service provisioning: {self.name}")
            return False

        self._provision()

        if not self.test_provisioned():
            raise RuntimeError(f"Failed to provision systemd service: {self.name}")

        logger.info(f"Successfully provisioned systemd service: {self.name}")
        return True

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

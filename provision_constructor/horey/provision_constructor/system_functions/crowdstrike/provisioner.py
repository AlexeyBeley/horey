"""
Provision ntp service.

"""

from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.common_utils.bash_executor import BashExecutor
from horey.h_logger import get_logger

logger = get_logger()
BashExecutor.set_logger(logger, override=False)


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """

    """

    def __init__(self, deployment_dir, force, upgrade, **kwargs):
        super().__init__(force, upgrade, **kwargs)
        self.deployment_dir = deployment_dir

    def test_provisioned(self):
        self.init_apt_packages()
        return (
            (not self.apt_check_installed("sntp*"))
            and (not self.apt_check_installed("chrony*"))
            and self.check_file_provisioned(
                "./timesyncd.conf", "/etc/systemd/timesyncd.conf"
            )
            and self.check_systemd_service_status(
                service_name="systemd-timesyncd", min_uptime=20
            )
        )

    def _provision(self):
        """
        Provision ntp.

        @return:
        """

        breakpoint()



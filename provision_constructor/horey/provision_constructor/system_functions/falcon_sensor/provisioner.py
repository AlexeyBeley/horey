"""
Provision ntp service.

"""

import os.path
import platform
import json

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
    Provision ntp service.
    Remove all others.

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

        self.apt_purge("ntp*")
        self.apt_purge("sntp*")
        self.apt_purge("chrony*")
        release = platform.release()
        float_release = float(release[:release.find(".", release.find(".")+1)])

        if float_release < 5.15:
            self.apt_install("systemd-timesyncd")

        try:
            ret = self.run_bash("sudo timedatectl set-ntp false")
            logger.info(ret)
        except BashExecutor.BashError as error_inst:
            dict_inst = json.loads(str(error_inst))
            if "NTP not supported" in dict_inst["stderr"]:
                SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, self.force,
                                                                   self.upgrade, package_names=["systemd-timesyncd"]).provision()
                self.run_bash("sudo systemctl restart systemd-timedated")
                ret = self.run_bash("sudo timedatectl set-ntp false")
                logger.info(ret)

        self.provision_file(
            "./timesyncd.conf", "/etc/systemd/timesyncd.conf", sudo=True
        )

        ret = self.run_bash("sudo timedatectl set-ntp true")
        logger.info(ret)

        ret = self.run_bash("sudo systemctl restart systemd-timedated")
        logger.info(ret)

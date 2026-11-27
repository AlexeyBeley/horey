import os.path

from horey.common_utils.remoter import Remoter
from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.h_logger import get_logger

logger = get_logger()


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    def __init__(self, deployment_dir, force, upgrade, **kwargs):
        super().__init__(deployment_dir, force, upgrade, **kwargs)

    def test_provisioned(self):
        """
        jre:
        openjdk-11-jre-headless/jammy-updates,jammy-security,now 11.0.18+10-0ubuntu1~22.04 amd64 [installed,automatic]
        openjdk-11-jre/jammy-updates,jammy-security,now 11.0.18+10-0ubuntu1~22.04 amd64 [installed,automatic]

        jdk:
        openjdk-11-jdk-headless/jammy-updates,jammy-security,now 11.0.18+10-0ubuntu1~22.04 amd64 [installed,automatic]
        openjdk-11-jdk/jammy-updates,jammy-security,now 11.0.18+10-0ubuntu1~22.04 amd64 [installed,automatic]
        :return:
        """
        self.init_apt_packages()
        return self.apt_check_installed("openjdk-17-jdk") and \
               self.apt_check_installed("openjdk-17-jre")

    def _provision(self):
        """
        retry_10_times_sleep_5 apt install --upgrade default-jre -y
        retry_10_times_sleep_5 apt install --upgrade default-jdk -y

        old:
        self.apt_add_repository("ppa:openjdk-r/ppa")

        :return:
        """

        self.update_packages()
        self.apt_install("openjdk-17-jdk")
        self.apt_install("openjdk-17-jdk")


    def provision_remote(self, remoter: Remoter):
        """
        retry_10_times_sleep_5 apt install --upgrade default-jre -y
        retry_10_times_sleep_5 apt install --upgrade default-jdk -y

        old:
        self.apt_add_repository("ppa:openjdk-r/ppa")

        :return:
        """

        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, self.force, self.upgrade, package_names=["openjdk-17-jdk"]).provision_remote(remoter)

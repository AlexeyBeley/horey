import os.path
from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.h_logger import get_logger

logger = get_logger()


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    def __init__(self, deployment_dir, force, upgrade):
        super().__init__(os.path.dirname(os.path.abspath(__file__)), force, upgrade)
        self.deployment_dir = deployment_dir

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
        return self.apt_check_installed("openjdk-11-jdk") and \
               self.apt_check_installed("openjdk-11-jre")

    def _provision(self):
        """
        retry_10_times_sleep_5 apt install --upgrade default-jre -y
        retry_10_times_sleep_5 apt install --upgrade default-jdk -y

        old:
        self.apt_add_repository("ppa:openjdk-r/ppa")

        :return:
        """
        breakpoint()

        self.apt_install("default-jre")
        self.apt_install("default-jdk")

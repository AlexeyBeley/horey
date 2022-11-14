import os.path
import pdb
from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.h_logger import get_logger

logger = get_logger()


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    def __init__(self, deployment_dir):
        super().__init__(os.path.dirname(os.path.abspath(__file__)))
        self.deployment_dir = deployment_dir
        self._release_codename = None

    @property
    def release_codename(self):
        if self._release_codename is None:
            response = self.run_bash("lsb_release -cs")
            self._release_codename = response["stdout"]
        return self._release_codename

    def provision(self, force=False):
        if not force:
            if self.test_provisioned():
                return

        self._provision()

        self.test_provisioned()

    def test_provisioned(self):
        self.init_apt_packages()
        return (
            os.path.isfile("/usr/share/keyrings/docker-archive-keyring.gpg")
            and self.check_file_contains(
                "/etc/apt/sources.list.d/docker.list", "download.docker.com"
            )
            and self.apt_check_installed("docker-ce")
            and self.apt_check_installed("docker-ce-cli")
            and self.apt_check_installed("docker-ce")
        )

    def _provision(self):
        if not self.apt_check_repository_exists("download.docker.com"):
            self.run_bash("sudo rm -rf /usr/share/keyrings/docker-archive-keyring.gpg")
            self.run_bash(
                "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg"
            )
            self.add_line_to_file(
                line=f"deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu {self.release_codename} stable",
                file_path="/etc/apt/sources.list.d/docker.list",
                sudo=True,
            )

            self.reinit_apt_packages()

        self.apt_install("docker-ce")
        self.apt_install("docker-ce-cli")
        self.apt_install("docker-ce")
        self.run_bash("sudo groupadd docker || true")
        self.run_bash('sudo usermod -aG docker "${USER}"')
        self.run_bash("sudo chmod 0666 /var/run/docker.sock")

"""
APT packages provisioning.

"""

from horey.common_utils.remoter import Remoter
from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.h_logger import get_logger

logger = get_logger()


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """
    Main provisioner.

    """

    # pylint: disable= too-many-arguments
    def __init__(self, deployment_dir, force, upgrade, package_name=None, package_names=None, needrestart_mode="a", **kwargs):
        super().__init__(deployment_dir, force, upgrade)
        self.deployment_dir = deployment_dir

        if package_name is not None:
            self.package_names = [package_name]
        elif package_names is not None:
            self.package_names = package_names
        else:
            raise ValueError("package_name/package_names not set")
        self.needrestart_mode = needrestart_mode

    def test_provisioned(self):
        """
        Test all packages provisioned.

        @return:
        """

        self.init_apt_packages()
        if self.package_names == ["all"]:
            ret = self.run_bash("sudo apt list --upgradeable")
            return ret["stdout"] in ["Listing... Done", "Listing..."]

        return all(self.apt_check_installed(package_name)
                   for package_name in self.package_names)

    def _provision(self):
        """
        Provision packages.

        @return:
        """
        if self.package_names == ["all"]:
            return self._provision_upgrade_full()

        return self.apt_install(None, package_names=self.package_names, needrestart_mode=self.needrestart_mode)

    def _provision_upgrade_full(self):
        """
        Upgrade all system packages system.

        :return:
        """

        return self.run_apt_bash_command(f"sudo NEEDRESTART_MODE={self.needrestart_mode} apt full-upgrade -y")

    def provision_remote(self, remoter: Remoter):
        """
        Provision remotely
        Preparing to unpack influxdb_1.12.2-1_amd64.deb ...

        :param remoter:
        :return:
        """

        self.remoter = remoter
        self.apt_install_remote(package_names=self.package_names, needrestart_mode=self.needrestart_mode)

    def apt_install_remote(self, package_names=None, needrestart_mode="a"):
        """
        Run apt install or upgrade.

        @param package_name:
        @param package_names:
        @return:
        :param needrestart_mode:
        """

        self.init_apt_packages_remote()

        logger.info(f"Installing apt packages: {package_names}")

        command = f"sudo NEEDRESTART_MODE={needrestart_mode} apt{' --upgrade ' if self.upgrade else ' '}install -y {' '.join(package_names)}"

        def raise_on_error_callback(lst_stdout, lst_stderr, status_code):
            """
            Validate apt install result.

            :param lst_stdout:
            :param lst_stderr:
            :param status_code:
            :return:
            """

            logger.info(f"Ignoring {lst_stderr=}, {status_code=}")

            stdout = "\n".join(lst_stdout)
            if (
                    "has no installation candidate" in stdout
                    or "is not available, but is referred to by another package"
                    in stdout
            ):
                raise ValueError(f"Error in {stdout}")

            return True

        self.remoter.execute(
            command, raise_on_error_callback
        )

        self.reinit_apt_packages_remote()

    def reinit_apt_packages_remote(self):
        """
        After we modify the apt packages' statuses (install, update, remove...) we need to reinit.

        @return:
        """

        self.remoter.get_state()["APT_PACKAGES"] = []
        self.remoter.get_state()["APT_PACKAGES_UPDATED"] = False
        self.init_apt_packages_remote()

    def init_apt_packages_remote(self):
        """
        Init installed packages list.

        @return:
        """

        self.update_packages_remote()
        if not self.remoter.get_state()["APT_PACKAGES"]:
            stdout, stderr, errcode = self.remoter.execute("sudo apt list --installed")
            lines = [line.strip("\n") for line in stdout]
            self.remoter.get_state()["APT_PACKAGES"] = self.init_apt_packages_from_output(lines)

    def update_packages_remote(self):
        """
        Update the information from apt repositories.
        If we update the repo list we need to run update.

        @return:
        """

        if self.remoter.get_state().get("APT_PACKAGES_UPDATED"):
            return True

        stdout, stderr, errcode = self.remoter.execute("sudo DEBIAN_FRONTEND=noninteractive apt update")

        lines = [line.strip("\n") for line in stdout]
        self.validate_apt_update_output(lines)

        self.remoter.get_state()["APT_PACKAGES_UPDATED"] = True
        self.remoter.get_state()["APT_PACKAGES"] = []
        return self.init_apt_packages_remote()

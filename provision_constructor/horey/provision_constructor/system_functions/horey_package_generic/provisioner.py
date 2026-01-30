"""
Provision horey packages from source.

"""
import shutil
from pathlib import Path

from horey.common_utils.remoter import Remoter
from horey.pip_api.pip_api import PipAPI
from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.h_logger import get_logger

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
        horey_repo_path=None,
        package_name=None,
        package_names=None,
        venv_path=None,
        **kwargs
    ):
        super().__init__(deployment_dir, force, upgrade, **kwargs)

        if package_name is not None:
            self.package_names = [package_name]
        elif package_names is not None:
            self.package_names = package_names
        else:
            raise ValueError("package_name/package_names not set")

        self.horey_repo_path = horey_repo_path
        self.venv_path = venv_path
        self.local_horey_repo_path = kwargs.get("local_horey_repo_path")

    def test_provisioned(self):
        """
        Test all packages are provisioned.

        @return:
        """
        return all(self.check_pip_installed(f"horey.{package_name.replace('_', '-')}")
                   for package_name in self.package_names)

    def _provision(self):
        """
        Provision single packages.

        @return:
        """

        for package_name in self.package_names:
            command = f"cd {self.horey_repo_path} && make recursive_install_from_source-{package_name}"

            if self.venv_path is not None:
                command = self.activate + " && " + command

            self.run_bash(command)
            self.init_pip_packages()


    def provision_remote(self, remoter: Remoter):
        """
        Provision remotely
             command = (
            "#!/bin/bash\n"
            "sudo sed -i 's/#$nrconf{kernelhints} = -1;/$nrconf{kernelhints} = 0;/' /etc/needrestart/needrestart.conf\n"
            "set -xe\n"
            "export unzip_installed=0\n"
            "unzip -v || export unzip_installed=1\n"
            f"if [[ $unzip_installed == '1' ]]; then sudo DEBIAN_FRONTEND=noninteractive apt update && sudo NEEDRESTART_MODE=a apt install -yqq unzip; fi\n"
            f"unzip {remote_zip_path} -d {remote_deployment_dir_path}\n"
            f"rm {remote_zip_path}\n"
        )
        logger.info(f"[REMOTE] {command}")
        return command

        :param remoter:
        :return:
        """


        remoter.execute("rm -rf horey")
        if self.local_horey_repo_path:
            self.deployment_dir.mkdir(exist_ok=True)
            deployment_horey_dir = self.deployment_dir / "horey"
            shutil.rmtree(deployment_horey_dir)
            for package_name in self.package_names:
                PipAPI.copy_horey_package_required_packages_to_build_dir(package_name,
                                                                         self.deployment_dir,
                                                                     self.local_horey_repo_path,
                                                                     )

            remoter.put_directory(Path(deployment_horey_dir), Path("./horey"))

        for package_name in self.package_names:
            install_command = f"python pip_api/horey/pip_api/pip_api_make.py --install horey.{package_name} --force_reinstall --pip_api_configuration ./pip_api_configuration.py"

            remoter.execute(f"cd horey && {install_command}")

        return True

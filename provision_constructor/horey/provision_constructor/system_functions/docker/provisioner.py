"""
Docker provisioner.

"""
import json
import os.path
from pathlib import Path

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
    Docker provisioner.

    """

    def __init__(self, deployment_dir, force, upgrade, **kwargs):
        super().__init__(deployment_dir, force, upgrade, **kwargs)
        self._release_codename = None

    @property
    def release_codename(self):
        """
        Get linux release code name.

        :return:
        """

        if self._release_codename is None:
            response = self.run_bash("lsb_release -cs")
            self._release_codename = response["stdout"]
        return self._release_codename

    def test_provisioned(self):
        """
        Standard.

        :return:
        """

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
        """
        Provision stable docker

        :return:
        """

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
        self.run_bash("sudo groupadd docker || true")
        self.run_bash('sudo usermod -aG docker "${USER}"')
        self.run_bash("sudo chmod 0666 /var/run/docker.sock")

    def init_release_codename_remote(self, remoter:Remoter):
        """
        Init the release

        :param remoter:
        :return:
        """

        if self._release_codename is None:
            ret = remoter.execute("lsb_release -cs")
            self._release_codename = ret[0][-1].strip("\n")
        return self._release_codename

    def provision_remote(self, remoter: Remoter):
        """
        Provision stable docker

        :return:
        """
        self.remoter = remoter
        if self.action == "prune_old_images":
            return self.provision_prune_old_images_remote()
        if self.action == "pull":
            return self.provision_pull_remote()
        if self.action == "login":
            return self.provision_login_remote()

        if not SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, self.force,
                                                                  self.upgrade,
                                                                  action="check_repository_exists",
                                                                                 repository_name="download.docker.com").provision_remote(
                                                                  remoter):

            SystemFunctionFactory.REGISTERED_FUNCTIONS["gpg_key"](self.deployment_dir, self.force,
                                                                  self.upgrade,
                                                                  src_url="https://download.docker.com/linux/ubuntu/gpg",
                                                                  dst_file_path="/usr/share/keyrings/docker-archive-keyring.gpg").provision_remote(
                                                                  remoter)
            self.init_release_codename_remote(remoter)
            self.add_line_to_file_remote(remoter,
                line=f"deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu {self.release_codename} stable",
                file_path=Path("/etc/apt/sources.list.d/docker.list"),
                sudo=True,
            )

        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, True, self.upgrade,
                                                                          action="update_packages").provision_remote(
            remoter)

        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir, self.force, self.upgrade,
                                                                          package_names=["docker-ce",
                                                                                         ]).provision_remote(
            remoter)

        remoter.execute("sudo groupadd docker || true")
        remoter.execute('sudo usermod -aG docker "${USER}"')
        remoter.execute("sudo chmod 0666 /var/run/docker.sock")
    
    def provision_prune_old_images_remote(self):
        """
        Clean old images.

        :return: 
        """

        horey_dir_path= Path(self.kwargs.get("horey_dir_path"))
        limit = self.kwargs.get("limit")
        self.remoter.execute(f"source {horey_dir_path / 'build' / '_build' / '_venv' / 'bin' / 'activate'} && "
                             f"python {horey_dir_path / 'docker_api'/ 'horey' / 'docker_api' / 'docker_actor.py'} --action prune_old_images --limit {limit}")
        return True

    def provision_pull_remote(self):
        """
        Clean old images.

        :return:
        """

        horey_dir_path= Path(self.kwargs.get("horey_dir_path"))
        image = self.kwargs.get("image")
        self.remoter.execute(f"source {horey_dir_path / 'build' / '_build' / '_venv' / 'bin' / 'activate'} && "
                             f"python {horey_dir_path / 'docker_api'/ 'horey' / 'docker_api' / 'docker_actor.py'} --action pull --image {image}")
        return True

    def provision_login_remote(self):
        """
        Clean old images.

        :return:
        """

        region = self.kwargs.get("region")
        logout = self.kwargs.get("logout")
        # True by default unless "false" explicitly set
        logout = str(logout).lower() != "false"

        self.remoter.execute("ls")
        ret = self.remoter.execute("aws sts get-caller-identity")
        response = json.loads("".join(ret[0]))
        registry = f"{response['Account']}.dkr.ecr.{region}.amazonaws.com"
        if logout:
            self.remoter.execute(f"docker logout {registry}", self.last_line_validator(f"Removing login credentials for {registry}"))

        self.remoter.execute(f"aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {registry}", self.last_line_validator("Login Succeeded"))
        ret = self.remoter.execute("cat ~/.docker/config.json && echo '\n'")
        output = "".join(ret[0])
        response= json.loads(output[output.find("{"):])
        for docker_registry in  response["auths"]:
            if docker_registry == registry:
                return True

        raise self.FailedCheckError(f"Did not find registry {registry} in ~/.docker/config.json: {output} ")

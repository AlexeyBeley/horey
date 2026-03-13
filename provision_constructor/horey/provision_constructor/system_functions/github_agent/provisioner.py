"""
Provision ntp service.

"""
from pathlib import Path

from horey.common_utils.remoter import Remoter

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
    Provision github agent.

    """

    def __init__(self, deployment_dir, force, upgrade, **kwargs):
        """

        :param deployment_dir:
        :param force:
        :param upgrade:
        :param kwargs:
                    github_token - token
                    runner_name - Name to give to the runner
                    repo_name
                    repo_owner
        """
        super().__init__(deployment_dir, force, upgrade, **kwargs)


    def provision_remote(self, remoter: Remoter):
        """
        Provision remotely
        Preparing to unpack influxdb_1.12.2-1_amd64.deb ...

        :param remoter:
        :return:
        """

        self.remoter = remoter
        if self.action == "start_container":
            return self.start_container_remote()
        self.provision_agent_remote()

    def start_container_remote(self):
        """
        Start container

        :return:
        """


        image_name = self.kwargs.get("image_name")
        github_token = self.kwargs.get("github_token")
        repo_name = self.kwargs.get("repo_name")
        repo_owner = self.kwargs.get("repo_owner")

        ret = self.remoter.execute(f"docker run -d --name {repo_name} "
                                   f"-e REPO_OWNER={self.kwargs.get('repo_owner')} "
                                   f"-e REPO_NAME={self.kwargs.get('repo_name')} "
                                   f"-e GITHUB_TOKEN={self.kwargs.get('github_token')} "
                                   f"-e RUNNER_NAME={self.kwargs.get('runner_name', repo_name)} "
                                   f"{image_name}")
        breakpoint()

    def provision_agent_remote(self):
        """
        Provision GitHub agent remotely.

        :return:
        """

        github_token = self.kwargs.get("github_token")
        if not github_token:
            raise ValueError("github_token is required in kwargs")
        runner_name = self.kwargs.get("runner_name")
        if not runner_name:
            raise ValueError("runner_name is required in kwargs")

        # Download and configure GitHub Actions runner
        remote_dir = Path("actions-runner")
        remote_targ_gz_path = remote_dir / "actions-runner-linux-x64-2.311.0.tar.gz"

        self.remoter.execute(f"mkdir -p {remote_dir}")
        self.download_file_from_web_remote("https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz", remote_targ_gz_path)
        self.remoter.execute(f"tar xzf {remote_targ_gz_path}")
        self.remoter.execute(f"./config.sh --url https://github.com/{self.kwargs.get('repo_owner')}/{self.kwargs.get('repo_name')} --token {github_token} --name {runner_name} --unattended")
        self.remoter.execute("sudo ./svc.sh install")
        self.remoter.execute("sudo ./svc.sh start")

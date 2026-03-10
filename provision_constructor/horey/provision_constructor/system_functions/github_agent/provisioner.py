"""
Provision ntp service.

"""

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

        self.remoter.execute("pwd")

    def provision_agent(self):
        """
        Provision GitHub agent remotely.

        :return:
        """
        github_token = self.kwargs.get("github_token")
        if not github_token:
            raise ValueError("github_token is required in kwargs")

        # Download and configure GitHub Actions runner
        commands = [
            "mkdir -p actions-runner && cd actions-runner",
            "curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz",
            "tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz",
            f"./config.sh --url https://github.com/{self.kwargs.get('repo_owner')}/{self.kwargs.get('repo_name')} --token {github_token} --unattended",
            "sudo ./svc.sh install",
            "sudo ./svc.sh start"
        ]

        for command in commands:
            self.remoter.execute(command)

"""
GIT API module.

"""
import os
from pathlib import Path

from horey.h_logger import get_logger
from horey.git_api.git_api_configuration_policy import GitAPIConfigurationPolicy
from horey.common_utils.bash_executor import BashExecutor

logger = get_logger()


class GitAPI:
    """
    API to pip functionality

    """

    REQUIREMENTS = {}

    def __init__(self, configuration: GitAPIConfigurationPolicy = None):
        self.configuration = configuration
        self.bash_executor = BashExecutor()

    def clone(self):
        """
        Clone from remote to local.

        :return:
        """
        breakpoint()
        base = f'GIT_SSH_COMMAND="ssh -i {self.configuration.ssh_key_file_path} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"'

        os.chdir(Path(self.configuration.directory_path).resolve().parent)
        ret = self.bash_executor.run_bash(f"{base} git clone {self.configuration.remote}")
        return ret

    def checkout_remote_branch(self, git_remote_url, branch_name):
        """
        Pull latest changes.

        :param git_remote_url:
        :param branch_name:
        :return:
        """
        if oct(os.stat(self.configuration.ssh_key_file_path).st_mode)[-3:] != "644":
            path_ssh_key_file = Path(self.configuration.ssh_key_file_path)
            path_ssh_key_file.chmod(0o400)

        base = f'GIT_SSH_COMMAND="ssh -i {self.configuration.ssh_key_file_path} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"'
        current_working_directory = os.getcwd()
        if current_working_directory != self.configuration.git_directory_path:
            os.chdir(self.configuration.git_directory_path)
        self.configuration.directory_path = str(Path(self.configuration.git_directory_path) / git_remote_url.split("/")[-1])
        if not os.path.exists(self.configuration.directory_path):
            command = f"{base} git clone -b {branch_name} --single-branch {git_remote_url}"
            self.bash_executor.run_bash(command)
            os.chdir(self.configuration.directory_path)
            return True

        os.chdir(self.configuration.directory_path)

        command = "git remote -v"
        ret = self.bash_executor.run_bash(command)
        lines = ret["stdout"].split("\n")
        for line in lines:
            line = line.replace("\t", " ")
            remote_name, address, direction = line.split(" ")

            if direction != "(fetch)":
                continue

            if address != git_remote_url:
                continue

            break
        else:
            raise RuntimeError(f"Was not able to find remote with address {git_remote_url}")

        command = f"{base} git fetch {remote_name} {branch_name}"
        ret = self.bash_executor.run_bash(command)
        stdout = ret.get("stdout")
        if stdout:
            raise RuntimeError(f"Unexpected stdout: {stdout}")
        stderr = ret.get("stderr")
        if not stderr:
            raise RuntimeError(f"Unexpected stderr: {stderr}")

        for line in stderr.split("\n"):
            line = line.strip()
            while "  " in line:
                line = line.replace("  ", " ")
            if not line.startswith("*"):
                continue
            line_static_star, line_static_branch, line_branch_name, line_arrow, line_static_fetch_head = line.split(" ")
            if line_static_star != "*":
                raise ValueError(f"Incorrect star in '{line}'")
            if line_static_branch != "branch":
                raise ValueError(f"Incorrect branch in '{line}'")
            if line_branch_name != branch_name:
                raise ValueError(f"Incorrect branch_name in '{line}'")
            if line_arrow != "->":
                raise ValueError(f"Incorrect line_arrow in '{line}'")
            if line_static_fetch_head != "FETCH_HEAD":
                raise ValueError(f"Incorrect line_static_fetch_head in '{line}'")
            break
        else:
            raise RuntimeError("Was not able to find line corresponding to fetched branch")

        command = f"git reset --hard {remote_name}/{branch_name}"
        ret = self.bash_executor.run_bash(command)
        stdout = ret["stdout"]
        if "HEAD is now at" not in stdout:
            raise RuntimeError(stdout)

        command = f"git checkout {branch_name}"
        ret = self.bash_executor.run_bash(command)
        if ret["stdout"] not in [f"Your branch is up to date with '{remote_name}/{branch_name}'.", f"branch '{branch_name}' set up to track '{remote_name}/{branch_name}'."]:
            raise RuntimeError(ret)
        return True

    def get_commit_id(self):
        command = "git rev-parse --short HEAD"
        ret = self.bash_executor.run_bash(command)
        stdout = ret["stdout"]

        if not stdout:
            raise RuntimeError(stdout)

        if " " in stdout:
            raise RuntimeError(stdout)

        return stdout

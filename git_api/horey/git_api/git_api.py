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
        self.bash_executor.set_logger(logger, override=False)

    def clone(self):
        """
        Clone from remote to local.

        :return:
        """
        raise NotImplementedError(
            """
            
        base = f'GIT_SSH_COMMAND="ssh -i {self.configuration.ssh_key_file_path} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"'

        os.chdir(Path(self.configuration.directory_path).resolve().parent)
        ret = self.bash_executor.run_bash(f"{base} git clone {self.configuration.remote}")
        return ret
            """
        )

    def checkout_remote_branch(self, git_remote_url, branch_name):
        """
        Pull latest changes.

        :param git_remote_url:
        :param branch_name:
        :return:
        """

        if oct(os.stat(self.configuration.ssh_key_file_path).st_mode)[-3:] != "400":
            path_ssh_key_file = Path(self.configuration.ssh_key_file_path)
            path_ssh_key_file.chmod(0o400)

        # old: ssh_base_command = f'GIT_SSH_COMMAND="ssh -i {self.configuration.ssh_key_file_path} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"'
        ssh_base_command = 'GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"'
        int_agent_pid = None
        if os.environ.get("SSH_AUTH_SOCK") is None:
            ssh_base_command = f"ssh-add {self.configuration.ssh_key_file_path}; " + ssh_base_command
            command = "ssh-agent -s"
            ret = self.bash_executor.run_bash(command)
            lines = ret["stdout"].split("\n")
            for line in lines:
                if "SSH_AGENT_PID" in line:
                    lst_line = line.split("=")
                    int_agent_pid = int((lst_line[lst_line.index("SSH_AGENT_PID") + 1]).split(";")[0])
                if "SSH_AUTH_SOCK" in line:
                    ssh_base_command = f"{line} {ssh_base_command}"
        try:
            self.checkout_remote_branch_helper(git_remote_url, branch_name, ssh_base_command)
        finally:
            if int_agent_pid:
                command = f"kill {int_agent_pid}"
                ret = self.bash_executor.run_bash(command)
                if ret.get("stdout") or ret.get("stdout"):
                    raise NotImplementedError(ret)
        return True

    def checkout_remote_branch_helper(self, git_remote_url, branch_name, ssh_base_command):
        """
        Run the git logic.

        :param git_remote_url:
        :param branch_name:
        :param ssh_base_command:
        :return:
        """

        current_working_directory = os.getcwd()
        if current_working_directory != self.configuration.git_directory_path:
            os.chdir(self.configuration.git_directory_path)
        self.configuration.directory_path = str(
            Path(self.configuration.git_directory_path) / git_remote_url.split("/")[-1])

        if not os.path.exists(self.configuration.directory_path):
            command = f"{ssh_base_command} git clone -b {branch_name} --single-branch {git_remote_url}"
            self.bash_executor.run_bash(command)
            os.chdir(self.configuration.directory_path)
            return True

        logger.info(f"Changing directory to source code directory: {self.configuration.directory_path}")
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

        command = f"{ssh_base_command} git fetch {remote_name} {branch_name}"
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

        command = f"git rev-parse --verify {branch_name}"
        ret = self.bash_executor.run_bash(command,
                                          ignore_on_error_callback=lambda dict_response: "Needed a single revision" in dict_response.get("stderr"))
        if ret["code"] == 0:
            command = f"git reset --hard {branch_name}"
            ret = self.bash_executor.run_bash(command)
            stdout = ret["stdout"]
            if "HEAD is now at" not in stdout:
                raise RuntimeError(stdout)

            command = f"git checkout {branch_name}"
            ret = self.bash_executor.run_bash(command)
            if ret["stdout"] not in [f"Your branch is up to date with '{remote_name}/{branch_name}'.",
                                     f"branch '{branch_name}' set up to track '{remote_name}/{branch_name}'."]:
                if ret["stderr"] != f"Already on '{branch_name}'":
                    raise RuntimeError(ret)
        else:
            command = f"git checkout -b {branch_name}"
            ret = self.bash_executor.run_bash(command)
            if ret["stdout"] not in [f"Your branch is up to date with '{remote_name}/{branch_name}'.",
                                     f"branch '{branch_name}' set up to track '{remote_name}/{branch_name}'."]:
                if ret["stderr"] != f"Already on '{branch_name}'":
                    raise RuntimeError(ret)

        command = "git merge FETCH_HEAD"
        ret = self.bash_executor.run_bash(command)
        if ret["stderr"]:
            raise RuntimeError(ret)
        return True

    def get_commit_id(self):
        """
        Fetch current commit short id

        :return:
        """

        command = "git rev-parse --short HEAD"
        ret = self.bash_executor.run_bash(command)
        stdout = ret["stdout"]

        if not stdout:
            raise RuntimeError(stdout)

        if " " in stdout:
            raise RuntimeError(stdout)

        return stdout

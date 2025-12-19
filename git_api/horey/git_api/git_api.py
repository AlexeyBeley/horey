"""
GIT API module.

"""
import os
import shutil
from pathlib import Path
from time import perf_counter

from horey.h_logger import get_logger
from horey.git_api.git_api_configuration_policy import GitAPIConfigurationPolicy
from horey.common_utils.bash_executor import BashExecutor
from horey.common_utils.common_utils import CommonUtils

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

        options = "-o User=git " if "github" in self.configuration.remote else ""
        self.ssh_base_command = f'GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o IdentitiesOnly=yes {options}-i {self.configuration.ssh_key_file_path}"'

    def clone(self):
        """
        Clone from remote to local.

        :return:
        """

        logger.info(f"Cloning from {self.configuration.remote} into {self.configuration.directory_path.parent}")
        with CommonUtils.temporary_directory(self.configuration.directory_path.parent):
            ret = self.bash_executor.run_bash(f"{self.ssh_base_command} git clone {self.configuration.remote}")
            expected_output = f"Cloning into '{os.path.basename(self.configuration.directory_path)}'"
            if expected_output not in ret["stdout"] and expected_output not in ret["stderr"]:
                try:
                    logger.info(
                        f"Failed to clone. Removing directory: {self.configuration.directory_path}")
                    shutil.rmtree(self.configuration.directory_path)
                except Exception:
                    pass
                raise ValueError(f"Expected to find '{expected_output}' either in stdout or stderr. Received: {ret}")
            return ret

    def update_local_source_code(self, dst_obj_identifier):
        """
        Pull if needed

        :param dst_obj_identifier:
        :return:
        """

        # Destination folder is empty or branch was specified
        if not self.configuration.directory_path.exists() or dst_obj_identifier is not None:
            return self.checkout_remote(dst_obj=dst_obj_identifier)
        return True

    def checkout_remote(self, dst_obj=None):
        """
        Pull latest changes.

        :param dst_obj:
        :return:
        """

        dst_obj = dst_obj or self.configuration.main_branch_name

        start_time = perf_counter()

        # todo: remove
        logger.print("start git api config print")
        self.configuration.print()

        if oct(os.stat(self.configuration.ssh_key_file_path).st_mode)[-3:] != "400":
            path_ssh_key_file = Path(self.configuration.ssh_key_file_path)
            path_ssh_key_file.chmod(0o400)

        int_agent_pid = None
        if os.environ.get("SSH_AUTH_SOCK") is None:
            command = "ssh-agent -s"
            ret = self.bash_executor.run_bash(command)
            lines = ret["stdout"].split("\n")
            for line in lines:
                if "SSH_AGENT_PID" in line:
                    lst_line = line.split("=")
                    int_agent_pid = int((lst_line[lst_line.index("SSH_AGENT_PID") + 1]).split(";")[0])
                if "SSH_AUTH_SOCK" in line:
                    self.ssh_base_command = f"{line} {self.ssh_base_command}"

            logger.info(f"Time to start SSH Agent: {perf_counter() - start_time}")
        try:
            self.checkout_remote_helper(dst_obj)
        except self.bash_executor.BashError as inst_err:
            if "The following untracked working tree files would be overwritten by" not in repr(inst_err):
                raise
            shutil.rmtree(self.configuration.directory_path)
            self.checkout_remote_helper(dst_obj)
        finally:
            if int_agent_pid:
                command = f"kill {int_agent_pid}"
                ret = self.bash_executor.run_bash(command)
                if ret.get("stdout") or ret.get("stdout"):
                    raise NotImplementedError(ret)

        logger.info(f"Time to git checkout remote branch: {perf_counter() - start_time}")

        return True

    # pylint: disable = too-many-locals, too-many-branches, too-many-statements
    def checkout_remote_helper(self, remote_object: str):
        """
        Run the git logic.

        :param remote_object:
        :return:
        """

        if not self.configuration.directory_path.exists():
            logger.info(f"git repo directory {self.configuration.directory_path} does not exist. Calling 'clone'")
            self.clone()
        with CommonUtils.temporary_directory(self.configuration.directory_path):

            remote_name = self.get_remote_name()
            if remote_object.startswith("refs/pull"):
                return self.checkout_remote_pr_helper(remote_name, remote_object)

            command = f"{self.ssh_base_command} git fetch {remote_name} {remote_object}"
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
                if line_branch_name != remote_object:
                    raise ValueError(f"Incorrect branch_name in '{line}'")
                if line_arrow != "->":
                    raise ValueError(f"Incorrect line_arrow in '{line}'")
                if line_static_fetch_head != "FETCH_HEAD":
                    raise ValueError(f"Incorrect line_static_fetch_head in '{line}'")
                break
            else:
                raise RuntimeError("Was not able to find line corresponding to fetched branch")

            self.checkout_fetched_remote_branch(remote_object, remote_name)
            self.update_submodules()
            return True

    def get_remote_name(self):
        """
        Fetch remote name from the local git.

        :return:
        """

        command = "git remote -v"
        ret = self.bash_executor.run_bash(command)
        lines = ret["stdout"].split("\n")
        for line in lines:
            line = line.replace("\t", " ")
            remote_name, address, direction = line.split(" ")
            logger.info(f"Checking triplet: {remote_name=}, {address=}, {direction=}")

            if direction != "(fetch)":
                logger.info(f"Checking direction: '{direction=}'")
                continue

            if address.lower() != self.configuration.remote.lower():
                logger.info(f"Checking address: '{address.lower()}', '{self.configuration.remote.lower()}'")
                continue
            break
        else:
            raise RuntimeError(f"Was not able to find remote with address {self.configuration.remote} and direction=(fetch)")
        return remote_name

    def checkout_fetched_remote_branch(self, branch_name, remote_name):
        """
        Checkout new or existing
        :param remote_name:
        :param branch_name:
        :return:
        """

        command = f"git rev-parse --verify {branch_name}"
        ret = self.bash_executor.run_bash(command,
                                          ignore_on_error_callback=lambda dict_response: "Needed a single revision" in dict_response.get("stderr"))
        if ret["code"] == 0:
            command = f"git reset --hard {branch_name}"
            ret = self.bash_executor.run_bash(command)
            stdout = ret["stdout"]
            if "HEAD is now at" not in stdout:
                raise RuntimeError(stdout)

            self.checkout_local(branch_name, remote_name=remote_name)

            command = f"git reset --hard {remote_name}/{branch_name}"
            ret = self.bash_executor.run_bash(command)
            stdout = ret["stdout"]
            if "HEAD is now at" not in stdout:
                raise RuntimeError(stdout)
        else:
            command = f"git checkout --track {remote_name}/{branch_name}"
            ret = self.bash_executor.run_bash(command)
            if ret["stderr"] not in [f"Switched to a new branch '{branch_name}'"]:
                raise RuntimeError(ret)

    def checkout_local(self, branch_name, remote_name=None):
        """
        Checkout to existing local branch

        :param remote_name:
        :param branch_name:
        :return:
        """

        remote_name = remote_name or self.get_remote_name()
        command = f"git checkout {branch_name}"
        ret = self.bash_executor.run_bash(command)
        if ret["stdout"] not in [f"Your branch is up to date with '{remote_name}/{branch_name}'.",
                                 f"branch '{branch_name}' set up to track '{remote_name}/{branch_name}'."]:

            if ret["stderr"] not in [f"Already on '{branch_name}'",
                                     f"Switched to branch '{branch_name}'"]:

                raise RuntimeError(ret)

        return True

    def checkout_remote_pr_helper(self, remote_name: str, remote_object: str):
        """
        Fetch and checkout remote PR

        :return:
        """

        branch_name = f"pr/{remote_object.split('/')[2]}"
        self.delete_local_branch(branch_name)

        command = f"{self.ssh_base_command} git fetch {remote_name} {remote_object}:{branch_name}"
        ret = self.bash_executor.run_bash(command)
        stdout = ret.get("stdout")
        if stdout:
            raise RuntimeError(f"Unexpected stdout: {stdout}")
        stderr = ret.get("stderr")
        if not stderr:
            raise RuntimeError(f"Unexpected stderr: {stderr}")
        last_line = stderr.split("\n")[-1].strip()
        # '* [new ref] refs/pull/1111/merge -> pr/1111'

        while "  " in last_line:
            last_line = last_line.replace("  ", " ")

        if last_line != f"* [new ref] {remote_object} -> {branch_name}":
            raise ValueError(f"Was not able to fetch {remote_name}:{remote_object}")
        self.checkout_local(branch_name, remote_name=remote_name)
        return True

    def delete_local_branch(self, branch_name):
        """
        Delete if exists.

        :param branch_name:
        :return:
        """

        if not self.check_local_branch_exists(branch_name):
            return True
        self.checkout_local(self.configuration.main_branch)

        ret = self.bash_executor.run_bash(f"git branch -D {branch_name}")
        if not ret["stdout"].startswith(f"Deleted branch {branch_name} (was"):
            raise RuntimeError(f"Was not able to delete branch {branch_name}")

        return ret["code"] == 0

    def check_local_branch_exists(self, branch_name: str):
        """
        Check branch exists locally

        :return:
        """

        command = f"git rev-parse --verify {branch_name}"
        ret = self.bash_executor.run_bash(command,
                                          ignore_on_error_callback=lambda dict_response: "Needed a single revision" in dict_response.get("stderr"))
        return ret["code"] == 0

    def update_submodules(self):
        """
        Init and update.

        :return:
        """

        if not os.path.exists(os.path.join(self.configuration.directory_path, ".gitmodules")):
            return True

        with CommonUtils.temporary_directory(self.configuration.directory_path):
            command = "git submodule init"
            ret = self.bash_executor.run_bash(command)
            if ret["stdout"]:
                raise ValueError(ret)
            if ret["stderr"] and "registered for path" not in ret["stderr"]:
                raise ValueError(ret)

            command = f"{self.ssh_base_command} git submodule update"
            ret = self.bash_executor.run_bash(command)
            if ret["stdout"] or ret["stderr"]:
                if "checked out" not in ret["stdout"] and "Cloning into" not in ret["stderr"]:
                    raise ValueError(ret)
        return True

    def get_commit_id(self):
        """
        Fetch current commit short id

        :return:
        """

        with CommonUtils.temporary_directory(self.configuration.directory_path):
            command = "git rev-parse --short HEAD"
            ret = self.bash_executor.run_bash(command)
            stdout = ret["stdout"]

            if not stdout:
                raise RuntimeError(stdout)

            if " " in stdout:
                raise RuntimeError(stdout)
            commit_id = stdout.strip()
            if len(commit_id) > 8 or len(commit_id) < 6:
                # pylint: disable= raise-missing-from
                raise ValueError(f"Unexpected commit id '{commit_id}'")
        return commit_id

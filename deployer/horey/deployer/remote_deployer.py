# pylint: disable= too-many-lines
"""
Remote targets deployer.

"""

import re
import os
import datetime
import time
import threading
import stat
import traceback

from contextlib import contextmanager
from typing import List
import paramiko
from sshtunnel import open_tunnel

from horey.deployer.deployment_target import DeploymentTarget
from horey.deployer.deployment_step import DeploymentStep
from horey.deployer.replacement_engine import ReplacementEngine
from horey.common_utils.zip_utils import ZipUtils

from horey.h_logger import get_logger

logger = get_logger()


class HoreySFTPClient(paramiko.SFTPClient):
    """
    Stolen from here:
    https://stackoverflow.com/questions/4409502/directory-transfers-with-paramiko

    """

    def put_dir(self, source, target):
        """
        Uploads the contents of the source directory to the target path. The
        target directory needs to exists. All subdirectories in source are
        created under target.
        """
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                self.put(
                    os.path.join(source, item), os.path.join(target, item), confirm=True
                )
            else:
                self.mkdir(os.path.join(target, item), ignore_existing=True)
                self.put_dir(os.path.join(source, item), os.path.join(target, item))

    def mkdir(self, path, mode=511, ignore_existing=False):
        """
        Augments mkdir by adding an option to not fail if the folder exists

        old code:
        super(HoreySFTPClient, self).mkdir(path, mode)
        """

        try:
            super().mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise

    def get_dir(self, remote_path, local_path):
        """
        Get remote dir

        :param remote_path:
        :param local_path:
        :return:
        """

        if os.path.isfile(local_path):
            raise RuntimeError(f"local_path must be a dir but {local_path} is a file")
        remote_path_basename = os.path.basename(remote_path)
        if not local_path.endswith(remote_path_basename):
            local_path = os.path.join(local_path, remote_path_basename)

        logger.info(f"Copying remote directory '{remote_path}' to local {local_path}")

        os.makedirs(local_path, exist_ok=True)

        remote_files_and_dirs = self.listdir_attr(path=remote_path)
        for attribute in remote_files_and_dirs:
            if stat.S_ISDIR(attribute.st_mode):
                self.get_dir(os.path.join(remote_path, attribute.filename), local_path)
                continue
            self.get(
                os.path.join(remote_path, attribute.filename),
                os.path.join(local_path, attribute.filename),
            )


class RemoteDeployer:
    """
    Remote target deployer.

    """
    REGEX_CLEANER = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')

    def __init__(self, configuration=None):
        self.configuration = configuration
        self.replacement_engine = ReplacementEngine()

    def provision_target_remote_deployer_infrastructure(
        self, deployment_target, asynchronous=False
    ):
        """
        Provision the deployment dir and deployer remote executor.

        :param deployment_target:
        :param asynchronous:
        :return:
        """

        if asynchronous:
            thread = threading.Thread(
                target=self.provision_target_remote_deployer_infrastructure_thread,
                args=(deployment_target,),
            )
            thread.start()
        else:
            self.provision_target_remote_deployer_infrastructure_thread(
                deployment_target
            )

    def provision_target_remote_deployer_infrastructure_thread(self, deployment_target):
        """
        Thread - can run async.

        :param deployment_target:
        :return:
        """

        retries = 5
        try:
            for i in range(retries):
                try:
                    self.provision_target_remote_deployer_infrastructure_raw(
                        deployment_target
                    )
                    break
                except Exception as exception_instance:
                    traceback_str = "".join(
                        traceback.format_tb(exception_instance.__traceback__)
                    )
                    repr_exception_instance = repr(exception_instance)

                    if i == retries - 1:
                        logger.error(f"Reached maximum number of retries when provisioning remote deployer infrastructure: "
                                     f"{retries}: {repr_exception_instance}: tb: {traceback_str}")
                        raise

                    logger.warning(
                        f"Exception received {repr_exception_instance} "
                    )

                    if (
                        "Unable to connect to port 22" in repr_exception_instance
                        or "No such file" in repr_exception_instance
                        or "Could not establish session to SSH gateway"
                        in repr_exception_instance
                        or "Error reading SSH protocol banner"
                        in repr_exception_instance
                    ):
                        logger.info("Valid exception going to sleep before retrying provision_target_remote_deployer_infrastructure_raw")
                        time.sleep(10)
                        continue

                    logger.error(
                        f"Raised unknown exception {repr_exception_instance}: tb: {traceback_str} "
                    )
                    raise

        except Exception as exception_instance:
            deployment_target.remote_deployer_infrastructure_provisioning_succeeded = (
                False
            )
            raise RuntimeError(
                f"{deployment_target.deployment_target_address}"
            ) from exception_instance
        finally:
            deployment_target.remote_deployer_infrastructure_provisioning_finished = (
                True
            )

    @staticmethod
    def generate_unzip_script_file_contents(remote_zip_path, deployment_target):
        """
        Generate the script to unzip remotely copied zipped deployment dir.

        :param remote_zip_path:
        :param deployment_target:
        :return:
        """
        command = (
            "#!/bin/bash\n"
            "sudo sed -i 's/#$nrconf{kernelhints} = -1;/$nrconf{kernelhints} = 0;/' /etc/needrestart/needrestart.conf\n"
            "set -xe\n"
            "export unzip_installed=0\n"
            "unzip -v || export unzip_installed=1\n"
            f"if [[ $unzip_installed == '1' ]]; then sudo DEBIAN_FRONTEND=noninteractive apt update && sudo NEEDRESTART_MODE=a apt install -yqq unzip; fi\n"
            f"unzip {remote_zip_path} -d {deployment_target.remote_deployment_dir_path}\n"
            f"rm {remote_zip_path}\n"
        )
        logger.info(f"[REMOTE] {command}")
        return command

    # pylint: disable = too-many-statements
    def provision_target_remote_deployer_infrastructure_raw(self, deployment_target):
        """
        Single attempt to provision. Should be enclosed in retries.

        :param deployment_target:
        :return:
        """
        # pylint: disable= too-many-locals

        zip_file_name = (
            os.path.basename(deployment_target.local_deployment_dir_path) + ".zip"
        )
        local_zip_file_path = os.path.join(
            deployment_target.local_deployment_dir_path, "..", zip_file_name
        )
        ZipUtils.make_archive(
            local_zip_file_path, deployment_target.local_deployment_dir_path
        )

        # Verify ZIP file was created
        for _ in range(10):
            if os.path.exists(local_zip_file_path):
                time.sleep(5)
                break
            logger.info(f"Waiting for '{local_zip_file_path}'")
            time.sleep(5)
        else:
            raise RemoteDeployer.DeployerError(f"Was not able to create '{local_zip_file_path}'")

        with self.get_deployment_target_client_context(deployment_target) as client:
            try:
                command = f"sudo rm -rf {deployment_target.remote_deployment_dir_path}"
                channel = client.invoke_shell()

                stdin = channel.makefile('wb')
                stdout = channel.makefile('r')
                self.execute_remote_shell(stdin, stdout, command, deployment_target.deployment_target_address)

                transport = client.get_transport()
                sftp_client = HoreySFTPClient.from_transport(transport)
                logger.info(
                    f"sftp: mkdir {deployment_target.remote_deployment_dir_path}"
                )
                sftp_client.mkdir(
                    deployment_target.remote_deployment_dir_path, ignore_existing=True
                )

                remote_zip_path = os.path.join(
                    deployment_target.remote_deployment_dir_path, zip_file_name
                )

                logger.info(
                    f"sftp: copying zip file from local {local_zip_file_path} to "
                    f"{deployment_target.deployment_target_address}:{remote_zip_path}"
                )

                sftp_client.put(local_zip_file_path, remote_zip_path)
                local_unziper_file_path = os.path.join(
                    deployment_target.local_deployment_dir_path, "unzip_script.sh"
                )
                with open(local_unziper_file_path, "w", encoding="utf-8") as file_handler:
                    file_handler.write(
                        self.generate_unzip_script_file_contents(
                            remote_zip_path, deployment_target
                        )
                    )

                remote_unzip_file_path = os.path.join(
                    deployment_target.remote_deployment_dir_path, "unzip_script.sh"
                )
                sftp_client.put(local_unziper_file_path, remote_unzip_file_path)
                os.remove(local_unziper_file_path)
                command = f"/bin/bash {remote_unzip_file_path}"

                try:
                    _, shout, _, exit_status = self.execute_remote_shell(stdin, stdout, command, deployment_target.deployment_target_address)
                    logger.info(f"{deployment_target.deployment_target_address} Unzip result: shell_output: {str(shout)}, exit_status: {exit_status}")
                except RemoteDeployer.DeployerError as error_instance:
                    if "apt does not have a stable CLI interface" not in repr(error_instance):
                        raise

                sftp_client.put(
                    os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        "data",
                        "remote_step_executor.sh",
                    ),
                    os.path.join(
                        deployment_target.remote_deployment_dir_path,
                        "remote_step_executor.sh",
                    ),
                )

                logger.info(
                    f"sftp: Uploading '{os.path.join(deployment_target.remote_deployment_dir_path, 'remote_step_executor.sh')}'"
                )
                sftp_client.put(
                    os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        "data",
                        "remote_step_executor.sh",
                    ),
                    os.path.join(
                        deployment_target.remote_deployment_dir_path,
                        "remote_step_executor.sh",
                    ),
                )

                command = f"sudo chmod +x {os.path.join(deployment_target.remote_deployment_dir_path, 'remote_step_executor.sh')}"
                self.execute_remote_shell(stdin, stdout, command, deployment_target.deployment_target_address)

                if deployment_target.linux_distro == "redhat":
                    command = "sudo yum install screen -y"
                    self.execute_remote_shell(stdin, stdout, command, deployment_target.deployment_target_address)
                deployment_target.remote_deployer_infrastructure_provisioning_succeeded = (
                    True
                )
                logger.info(
                    f"Finished provisioning deployer infrastructure at target {deployment_target.deployment_target_address}"
                )
            except Exception as error_instance:
                traceback_str = "".join(
                    traceback.format_tb(error_instance.__traceback__)
                )
                logger.error(
                    f"Failed provisioning deployer infrastructure at target {deployment_target.deployment_target_address}: {repr(error_instance)}: tb {traceback_str}"
                )

                deployment_target.remote_deployer_infrastructure_provisioning_succeeded = (
                    False
                )
                raise RemoteDeployer.DeployerError from error_instance

    @staticmethod
    def execute_remote_shell(stdin, stdout, cmd, remote_address, timeout=60):
        """

        :param remote_address:
        :param timeout: in minutes
        :param cmd: the command to be executed on the remote computer
        :examples:  execute('ls')
                    execute('finger')
                    execute('cd folder_name')
        """

        logger.info(f"[{remote_address} REMOTE->] {cmd}")
        end_time = datetime.datetime.now() + datetime.timedelta(minutes=timeout)

        cmd = cmd.strip('\n')
        finish = 'end of stdOUT buffer. finished with exit status'
        echo_cmd = f"echo {finish} $?"
        stdin.write(f"{cmd} ; {echo_cmd}\n")
        shin = stdin
        stdin.flush()

        shout = []
        sherr = []
        exit_status = 0
        for line in stdout:
            # get rid of 'coloring and formatting' special characters
            line = RemoteDeployer.REGEX_CLEANER.sub('', line).replace('\b', '').replace('\r', '')

            logger.info(f"[{remote_address} REMOTE<-] {line}")
            if str(line).startswith(cmd) or str(line).startswith(echo_cmd):
                # up for now filled with shell junk from stdin
                shout = []
            elif str(line).startswith(finish):
                # our finish command ends with the exit status
                exit_status = int(str(line).rsplit(maxsplit=1)[1])
                if exit_status:
                    raise RemoteDeployer.DeployerError(f"{shout}: exit status: {exit_status}")
                break
            else:
                shout.append(line)
            if datetime.datetime.now() > end_time:
                raise RemoteDeployer.DeployerError(f"{remote_address} Reached timeout waiting: {timeout} minutes")

        # first and last lines of shout/sherr contain a prompt
        if shout and echo_cmd in shout[-1]:
            shout.pop()
        if shout and cmd in shout[0]:
            shout.pop(0)
        if sherr and echo_cmd in sherr[-1]:
            sherr.pop()
        if sherr and cmd in sherr[0]:
            sherr.pop(0)

        return shin, shout, sherr, exit_status

    def execute_remote_windows(self, deployment_target, command):
        """
        This works:
        powershell -Command "ls; echo \"1 2 $?\""
        :param deployment_target:
        :param command:
        :return:
        """
        with self.get_deployment_target_client_context(deployment_target) as client:
            _, stdout, stderr = client.exec_command(command, timeout=600)
            stdout_string = stdout.read().decode("utf-8")
            stderr_string = stderr.read().decode("utf-8")
            return stdout_string, stderr_string

    def put_file_windows(self, deployment_target, local_file_path, remote_file_path):
        """
        Copy file from local to remote.

        :param deployment_target:
        :param local_file_path:
        :param remote_file_path:
        :return:
        """

        with self.get_deployment_target_client_context(deployment_target) as client:
            transport = client.get_transport()
            sftp_client = HoreySFTPClient.from_transport(transport)
            sftp_client.put(local_file_path, remote_file_path)
        return True

    def get_file_windows(self, deployment_target, local_file_path, remote_file_path):
        """
        Copy file from local to remote.

        :param deployment_target:
        :param local_file_path:
        :param remote_file_path:
        :return:
        """
        sleep_time = 1
        end_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
        while datetime.datetime.now() < end_time:
            with self.get_deployment_target_client_context(deployment_target) as client:
                transport = client.get_transport()
                try:
                    sftp_client = HoreySFTPClient.from_transport(transport)
                    sftp_client.get(remote_file_path, local_file_path)
                    return True
                except Exception as inst_error:
                    if "No such file" not in repr(inst_error):
                        break
                    logger.error(
                        f"Was not able to fetch remote path '{remote_file_path}' to local path '{local_file_path}'")
            logger.info(f"Going to sleep for {sleep_time}")
            time.sleep(sleep_time)
        logger.error(f"Was not able to fetch remote path '{remote_file_path}' to local path '{local_file_path}'")
        return False

    @staticmethod
    def execute_remote(client, command):
        """
        Execute command with SSH using connected client.

        :param client:
        :param command:
        :return:

        shell = client.invoke_shell(term='vt100', width=80, height=24, width_pixels=0, height_pixels=0, environment=None)
        """

        _, stdout, stderr = client.exec_command(command, timeout=120)
        stdout_string = stdout.read().decode("utf-8")
        stderr_string = stderr.read().decode("utf-8")
        if stdout_string:
            logger.info(stdout_string)
        if stderr_string:
            raise RemoteDeployer.DeployerError(stderr_string)

    def deploy_target_step(self, deployment_target, step, asynchronous=False):
        """
        Deploy single step.

        :param deployment_target:
        :param step:
        :param asynchronous:
        :return:
        """

        if asynchronous:
            thread = threading.Thread(
                target=self.deploy_target_step_thread, args=(deployment_target, step)
            )
            thread.start()
        else:
            self.deploy_target_step_thread(deployment_target, step)

    def deploy_target_step_thread(self, deployment_target, step):
        """
        Deploying thread, can be run async.

        :param deployment_target:
        :param step:
        :return:
        """

        logger.info(
            f"Starting deployment for target {deployment_target.deployment_target_address} step: {step.configuration.name}"
        )
        try:
            self.deploy_target_step_thread_helper(deployment_target, step)
        except Exception as exception_instance:
            logger.error(
                f"Unhandled exception in deploy_target_step_thread {repr(exception_instance)})"
            )
            step.status_code = step.StatusCode.ERROR
            step.output = repr(exception_instance)

    def deploy_target_step_thread_helper(self, deployment_target, step:DeploymentStep):
        """
        Unprotected code, should be enclosed in try except.

        :param deployment_target:
        :param step:
        :return:
        """

        with self.get_deployment_target_client_context(deployment_target) as client:
            try:
                self.execute_step(client, step, deployment_target.deployment_target_address)
                transport = client.get_transport()
                sftp_client = HoreySFTPClient.from_transport(transport)

                retry_attempts = step.configuration.retry_attempts
                sleep_time = step.configuration.sleep_time
                for retry_counter in range(retry_attempts):
                    try:
                        sftp_client.get(
                            step.configuration.finish_status_file_path,
                            os.path.join(
                                deployment_target.local_deployment_data_dir_path,
                                step.configuration.finish_status_file_name,
                            ),
                        )

                        sftp_client.get(
                            step.configuration.output_file_path,
                            os.path.join(
                                deployment_target.local_deployment_data_dir_path,
                                step.configuration.output_file_name,
                            ),
                        )
                        break
                    except IOError as error_received:
                        repr_error_received = repr(error_received)
                        if "No such file" not in repr_error_received:
                            raise
                        logger.info(
                            f"[LOCAL->{deployment_target.deployment_target_address}] Retrying to fetch remote script's status in {sleep_time} seconds ({retry_counter}/{retry_attempts})"
                        )
                    except Exception as error_received:
                        logger.error(
                            f"[LOCAL->{deployment_target.deployment_target_address}] Unhandled exception in helper thread {repr(error_received)})"
                        )

                    time.sleep(sleep_time)
                else:
                    step.status_code = step.StatusCode.ERROR
                    deployment_target.status_code = deployment_target.StatusCode.FAILURE
                    deployment_target.status = f"Failed to fetch step's status and output files: {step.configuration.name}"
                    raise TimeoutError(
                        f"[LOCAL->{deployment_target.deployment_target_address}] Failed to fetch remote script's status target: {deployment_target.deployment_target_address}"
                    )

                step.update_finish_status(
                    deployment_target.local_deployment_data_dir_path
                )
                step.update_output(deployment_target.local_deployment_data_dir_path)

                if step.status_code != step.StatusCode.SUCCESS:
                    last_lines = "\n".join(step.output.split("\n")[-50:])
                    deployment_target.status_code = deployment_target.StatusCode.FAILURE
                    deployment_target.status = f"Step returned status different from success: {step.configuration.name}"
                    raise RuntimeError(
                        f"[REMOTE<-{deployment_target.deployment_target_address}] Step finished with status: {step.status}, error: \n{last_lines}"
                    )

                logger.info(
                    f"[REMOTE<-{deployment_target.deployment_target_address}] Step finished successfully output in: '{step.configuration.output_file_name}'"
                )
            except Exception as error_instance:
                step.status_code = step.StatusCode.ERROR
                deployment_target.status_code = deployment_target.StatusCode.FAILURE
                deployment_target.status = f"Unknown exception happened when deploying the step {step.configuration.name}. " \
                                           f"Error: {repr(error_instance)}"
                raise RemoteDeployer.DeployerError(
                    repr(error_instance)
                ) from error_instance

    def perform_recursive_replacements(
        self, replacements_base_dir_path, string_replacements
    ):
        """
        Old style replacement.

        :param replacements_base_dir_path:
        :param string_replacements:
        :return:
        """
        self.replacement_engine.perform_recursive_replacements(
            replacements_base_dir_path, string_replacements
        )

    def perform_file_string_replacements(self, root, filename, string_replacements):
        """
        Old style replacement.

        :param root:
        :param filename:
        :param string_replacements:
        :return:
        """
        self.replacement_engine.perform_file_string_replacements(
            root, filename, string_replacements
        )

    def begin_provisioning_deployment_code(
        self, deployment_targets: List[DeploymentTarget]
    ):
        """
        Old code. Should be deprecated

        for deployment_target in deployment_targets:
            with self.get_deployment_target_client_context(deployment_target) as client:
                try:
                    transport = client.get_transport()
                    sftp_client = HoreySFTPClient.from_transport(transport)
                    self.execute_step(client, deployment_target.application_infrastructure_provision_step)
                    self.wait_for_step_to_finish(deployment_target.application_infrastructure_provision_step,
                                                 deployment_target.local_deployment_data_dir_path, sftp_client)
                except Exception as error_instance:
                    raise RemoteDeployer.DeployerError(repr(error_instance)) from error_instance

            deployment_target.deployment_code_provisioning_ended = True

        :param deployment_targets:
        :return:
        """

        raise DeprecationWarning("old code")

    def wait_for_step_to_finish(
        self, step, local_deployment_data_dir_path, sftp_client, deployment_target_address
    ):
        """
        Wait for status file creation.

        :param step:
        :param local_deployment_data_dir_path:
        :param sftp_client:
        :return:
        """

        retry_attempts = 10
        sleep_time = 60
        for retry_counter in range(retry_attempts):
            try:
                sftp_client.get(
                    step.configuration.finish_status_file_path,
                    os.path.join(
                        local_deployment_data_dir_path,
                        step.configuration.finish_status_file_name,
                    ),
                )

                sftp_client.get(
                    step.configuration.output_file_path,
                    os.path.join(
                        local_deployment_data_dir_path,
                        step.configuration.output_file_name,
                    ),
                )
                break
            except IOError as error_received:
                if "No such file" not in repr(error_received):
                    raise
                logger.info(
                    f"[LOCAL->{deployment_target_address}] Retrying to fetch remote script's status in {sleep_time} seconds ({retry_counter}/{retry_attempts})"
                )
            time.sleep(sleep_time)
        else:
            raise TimeoutError(f"[LOCAL->{deployment_target_address}] Failed to fetch remote script's status")

        step.update_finish_status(local_deployment_data_dir_path)
        step.update_output(local_deployment_data_dir_path)

        if step.status_code != step.StatusCode.SUCCESS:
            last_lines = "\n".join(step.output.split("\n")[-50:])
            raise RuntimeError(
                f"[REMOTE<-{deployment_target_address}] Step finished with status: {step.status}, error: \n{last_lines}"
            )

        logger.info(
            f"[REMOTE<-{deployment_target_address}] Step finished successfully output in: '{step.configuration.output_file_name}'"
        )

    @staticmethod
    def wait_for_deployment_code_provisioning_to_end(
        blocks_to_deploy: List[DeploymentTarget],
    ):
        """
        The build_dir and remote executor script provisioning.

        :param blocks_to_deploy:
        :return:
        """

        for block_to_deploy in blocks_to_deploy:
            for _ in range(60):
                if block_to_deploy.deployment_code_provisioning_ended:
                    break
                time.sleep(1)
            else:
                raise RuntimeError(
                    "Deployment failed at wait_for_deployment_code_provisioning_to_end"
                )
        logger.info("Deployment provisioning finished successfully")

    def begin_deployment(self, deployment_targets: List[DeploymentTarget]):
        """
        Old code
        for deployment_target in deployment_targets:
            with self.get_deployment_target_client_context(deployment_target) as client:
                try:
                    transport = client.get_transport()
                    sftp_client = HoreySFTPClient.from_transport(transport)
                    self.execute_step(client, deployment_target.application_deploy_step)
                    self.wait_for_step_to_finish(deployment_target.application_deploy_step,
                                             deployment_target.local_deployment_data_dir_path, sftp_client)
                except Exception as error_instance:
                    raise RemoteDeployer.DeployerError(repr(error_instance)) from error_instance

            deployment_target.deployment_code_provisioning_ended = True
        :param deployment_targets:
        :return:
        """
        raise DeprecationWarning()

    @staticmethod
    @contextmanager
    def get_deployment_target_client_context(block_to_deploy: DeploymentTarget):
        """
        SSH client context. With or without bastion tunnel

        :param block_to_deploy:
        :return:
        """

        logger.info(f"Loading target SSH Key of type '{block_to_deploy.deployment_target_ssh_key_type}' from '{block_to_deploy.deployment_target_ssh_key_path}'")
        deployment_target_key = RemoteDeployer.load_ssh_key_from_file(block_to_deploy.deployment_target_ssh_key_path, block_to_deploy.deployment_target_ssh_key_type)

        if block_to_deploy.bastion_address is None:
            with paramiko.SSHClient() as client:
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                logger.info(
                    f"Connecting directly to {block_to_deploy.deployment_target_address}, "
                    f"using key at {block_to_deploy.deployment_target_ssh_key_path}"
                )
                client.connect(
                    block_to_deploy.deployment_target_address,
                    port=22,
                    username=block_to_deploy.deployment_target_user_name,
                    pkey=deployment_target_key,
                    compress=True,
                    banner_timeout=60,
                )
                yield client
            return
        logger.info(f"Loading bastion SSH Key of type '{block_to_deploy.bastion_ssh_key_type}' from '{block_to_deploy.bastion_ssh_key_path}'")
        bastion_key = RemoteDeployer.load_ssh_key_from_file(block_to_deploy.bastion_ssh_key_path, block_to_deploy.bastion_ssh_key_type)
        with RemoteDeployer.get_client_context_with_bastion(
            block_to_deploy.bastion_address,
            block_to_deploy.bastion_user_name,
            bastion_key,
            block_to_deploy.deployment_target_address,
            block_to_deploy.deployment_target_user_name,
            deployment_target_key,
        ) as client:
            yield client

    @staticmethod
    def load_ssh_key_from_file(file_path, key_type):
        """
        Load key from file to object.

        :param file_path:
        :param key_type:
        :return:
        """

        key_type_lower = str(key_type).lower()
        if key_type_lower not in DeploymentTarget.SupportedSSHKeys:
            raise ValueError(f"Only {DeploymentTarget.SupportedSSHKeys} are supported, received: {key_type_lower}")

        if key_type_lower == "ed25519key":
            return paramiko.Ed25519Key.from_private_key_file(file_path)

        return paramiko.RSAKey.from_private_key_file(file_path)

    @staticmethod
    @contextmanager
    # pylint: disable= too-many-arguments
    def get_client_context_with_bastion(
        bastion_address,
        bastion_user_name,
        bastion_key,
        deployment_target_address,
        deployment_target_user_name,
        deployment_target_key,
    ):
        """
        SSH client context via bastion tunnel

        :param bastion_address:
        :param bastion_user_name:
        :param bastion_key:
        :param deployment_target_address:
        :param deployment_target_user_name:
        :param deployment_target_key:
        :return:
        """

        for i in range(10):
            try:
                with open_tunnel(
                    ssh_address_or_host=(bastion_address, 22),
                    remote_bind_address=(deployment_target_address, 22),
                    ssh_username=bastion_user_name,
                    ssh_pkey=bastion_key,
                ) as tunnel:
                    logger.info(
                        f"Opened SSH tunnel to {deployment_target_user_name}@{deployment_target_address} via {bastion_user_name}@{bastion_address}"
                    )

                    with paramiko.SSHClient() as client:
                        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        client.connect(
                            "localhost",
                            port=tunnel.local_bind_port,
                            username=deployment_target_user_name,
                            pkey=deployment_target_key,
                            compress=True,
                            banner_timeout=60,
                        )

                        yield client
                        return
            except RemoteDeployer.DeployerError:
                raise
            except Exception as error_received:
                logger.error(
                    f"Low level ssh connection to {deployment_target_user_name}@{deployment_target_address} via {bastion_user_name}@{bastion_address} error: {repr(error_received)}. Retry {i}/10"
                )

            logger.info(
                f"Going to sleep before retrying connecting to {deployment_target_user_name}@{deployment_target_address} via {bastion_user_name}@{bastion_address}"
            )
            time.sleep(1)

        raise RemoteDeployer.DeployerError(
            f"Timeout: Failed to open ssh tunnel to {deployment_target_user_name}@{deployment_target_address} via {bastion_user_name}@{bastion_address}"
        )

    @staticmethod
    def get_deployment_target_client(target: DeploymentTarget):
        """
        old code.

        with open(target.bastion_ssh_key_path, 'r') as bastion_key_file_handler:
            bastion_key = paramiko.RSAKey.from_private_key(StringIO(bastion_key_file_handler.read()))
        with open(target.deployment_target_ssh_key_path, 'r') as bastion_key_file_handler:
            deployment_target_key = paramiko.RSAKey.from_private_key(StringIO(bastion_key_file_handler.read()))

        with open_tunnel(
                ssh_address_or_host=(target.bastion_address, 22),
                remote_bind_address=(target.deployment_target_address, 22),
                ssh_username=target.bastion_user_name,
                ssh_pkey=bastion_key) as tunnel:
            logger.info(f"Opened SSH tunnel to {target.deployment_target_address} via {target.bastion_address} ")

            with paramiko.SSHClient() as client:
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(
                    'localhost',
                    port=tunnel.local_bind_port,
                    username=target.deployment_target_user_name,
                    pkey=deployment_target_key,
                    compress=True,
                    banner_timeout=60)

                yield client

        :param target:
        :return:
        """

        raise DeprecationWarning()

    def execute_step(self, client: paramiko.SSHClient, step, deployment_target_address):
        """
        Trigger one step execution.

        :param deployment_target_address:
        :param client:
        :param step:
        :return:
        """

        command = (
            f"screen -S deployer -dm {step.configuration.deployment_dir_path}/remote_step_executor.sh "
            f"{step.configuration.remote_script_file_path} {step.configuration.script_configuration_file_path} "
            f"{step.configuration.finish_status_file_path} {step.configuration.output_file_path}"
        )

        logger.info(f"[REMOTE->{deployment_target_address}] {command}")

        _, stdout_transport, stderr_transport = client.exec_command(command)
        stderr = stderr_transport.read()
        if stderr:
            raise RemoteDeployer.DeployerError(f"[REMOTE<-{deployment_target_address}]  {stderr}")
        stdout = stdout_transport.read()
        logger.info(f"[REMOTE<-{deployment_target_address}] {stdout}")

    def wait_for_deployment_to_end(self, blocks_to_deploy):
        """
        old code
        lst_errors = []
        for block in blocks_to_deploy:
            if block.application_deploy_step.status_code != DeploymentStep.StatusCode.SUCCESS:
                lst_errors.append(block.application_infrastructure_provision_step.configuration.output_file_path)

        if lst_errors:
            raise RuntimeError(str(lst_errors))
        logger.info("Deployment finished successfully output in")

        :param blocks_to_deploy:
        :return:
        """
        raise DeprecationWarning()

    @staticmethod
    def wait_to_finish(
        targets,
        check_finished_callback,
        check_success_callback,
        sleep_time=10,
        total_time=2400,
    ):
        """
        Check for an object to finish- callbacks based.

        :param targets:
        :param check_finished_callback:
        :param check_success_callback:
        :param sleep_time:
        :param total_time:
        :return:
        """

        total_time = max(total_time, max(step.configuration.sleep_time*step.configuration.retry_attempts for target in targets for step in target.steps))
        logger.info(f"New time to finish calculated from steps and default: {total_time} seconds")

        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(seconds=total_time)
        error_type = RuntimeError
        while datetime.datetime.now() < end_time:
            if all(check_finished_callback(target) for target in targets):
                logger.info(
                    f"All Finished: {[target.deployment_target_address for target in targets if check_finished_callback(target)]}"
                )
                break

            finished_targets = [
                target.deployment_target_address
                for target in targets
                if check_finished_callback(target)
            ]
            unfinished_targets = [
                target.deployment_target_address
                for target in targets
                if not check_finished_callback(target)
            ]
            logger.info(
                f"Finished {len(finished_targets)}: {finished_targets}"
                f", not finished {len(unfinished_targets)}: {unfinished_targets}"
            )
            logger.info(
                f"Deployer is going to sleep for {sleep_time} seconds"
            )

            time.sleep(sleep_time)
        else:
            error_type = TimeoutError

        failed = False
        errors = [f"Result: {[check_success_callback(target) for target in targets]}"]
        for target in targets:
            if not check_success_callback(target):
                failed = True
                error_line = f"[REMOTE<-{target.deployment_target_address}] Deployment failed"
                try:
                    error_line += f" Status: {target.status}"
                except Exception as inst:
                    logger.warning(f"[LOCAL->{target.deployment_target_address}] Couldn't fetch failure status."
                                   f"Due to exception: {repr(inst)}")
                errors.append(error_line)

        if failed:
            raise error_type("\n".join(errors))

    @staticmethod
    def wait_to_finish_step(
        target: DeploymentTarget, step: DeploymentStep, sleep_time=10, total_time=2400
    ):
        """
        Wait for a single step to finish

        :param target:
        :param step:
        :param sleep_time:
        :param total_time:
        :return:
        """

        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(seconds=total_time)

        while datetime.datetime.now() < end_time:
            if step.status_code is not None:
                logger.info(f"[REMOTE<-{target.deployment_target_address}] Finished step {step.configuration.name}")
                break

            logger.info(
                f"[LOCAL->{target.deployment_target_address}] Waiting for step: {step.configuration.name} going to sleep for {sleep_time} seconds"
            )

            time.sleep(sleep_time)
        else:
            step.status_code = step.StatusCode.ERROR
            if target.status_code is None:
                target.status_code = target.StatusCode.ERROR
                target.status = f"Step failed. Name: {step.configuration.name}"
            raise TimeoutError(
                f"[REMOTE<-{target.deployment_target_address}] Step: {step.configuration.name}"
            )

        if step.status_code != step.StatusCode.SUCCESS:
            raise RuntimeError(
                f"[REMOTE<-{target.deployment_target_address}] Step failed. Name: {step.configuration.name}, Status code:{step.status_code}, Status: {step.status}, Output: {step.output}"
            )

        logger.info(
            f"[REMOTE<-{target.deployment_target_address}] Finished step: {step.configuration.name}"
        )

    def deploy_targets_steps(self, targets, step_callback, asynchronous=True, async_wait_interval=10):
        """
        Deploy multiple targets' steps returned by a callback.

        :param async_wait_interval: Wait interval between the deployments. In seconds.
        :param targets:
        :param step_callback:
        :param asynchronous:
        :return:
        """

        steps = []
        for target in targets:
            step = step_callback(target)
            steps.append(step)
            self.deploy_target_step(target, step, asynchronous=asynchronous)
            time.sleep(async_wait_interval)
        self.wait_to_finish(
            targets,
            lambda _target: step_callback(_target).status_code is not None,
            lambda _target: step_callback(_target).status_code
            == step.StatusCode.SUCCESS,
        )

    def deploy_target(self, target: DeploymentTarget, asynchronous=False):
        """
        Deploy single target's all steps

        :param target:
        :param asynchronous:
        :return:
        """

        if asynchronous:
            thread = threading.Thread(target=self.deploy_target_thread, args=(target,))
            thread.start()
        else:
            self.deploy_target_thread(target)

    def deploy_target_thread(self, target):
        """
        Thread triggered async

        :param target:
        :return:
        """

        logger.info(f"Starting target deployment {target.deployment_target_address}")
        try:
            self.provision_target_remote_deployer_infrastructure_thread(target)
            if not target.remote_deployer_infrastructure_provisioning_succeeded:
                raise RuntimeError("Could not provision deployer infra")

            for step in target.steps:
                self.deploy_target_step(target, step, asynchronous=False)
                self.wait_to_finish_step(target, step)

            target.status_code = target.StatusCode.SUCCESS

        except Exception as inst_error:
            if target.status_code is None:
                target.status_code = target.StatusCode.ERROR
            if target.status is None:
                target.status = repr(inst_error)

        logger.info(f"Finished target deployment: {target.deployment_target_address}")

    def deploy_targets(self, targets, asynchronous=True):
        """
        Deploy multiple targets.

        :param asynchronous:
        :param targets:
        :return:
        """

        errors = []
        for target in targets:
            if target.bastion_ssh_key_path is not None and not os.path.exists(target.bastion_ssh_key_path):
                errors.append(f"Target {target.hostname} bastion SSH key file is missing at {target.bastion_ssh_key_path}")
            if not os.path.exists(target.deployment_target_ssh_key_path):
                errors.append(f"Target {target.hostname} SSH key file is missing at {target.deployment_target_ssh_key_path}")
        if errors:
            raise ValueError("\n".join(errors))

        for target in targets:
            self.deploy_target(target, asynchronous=asynchronous)
            time.sleep(10)

        self.wait_to_finish(
            targets,
            lambda _target: _target.status_code is not None,
            lambda _target: _target.status_code == _target.StatusCode.SUCCESS,
        )

    class DeployerError(RuntimeError):
        """
        Error occurred while deploying.
        """

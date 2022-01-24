import datetime
import json
import pdb
import time
import threading
import stat

import paramiko
from sshtunnel import open_tunnel
import os
from horey.deployer.machine_deployment_block import MachineDeploymentBlock
from horey.deployer.machine_deployment_step import MachineDeploymentStep
from typing import List
from contextlib import contextmanager
from io import StringIO

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
                self.put(os.path.join(source, item), os.path.join(target, item), confirm=True)
            else:
                self.mkdir(os.path.join(target, item), ignore_existing=True)
                self.put_dir(os.path.join(source, item), os.path.join(target, item))

    def mkdir(self, path, mode=511, ignore_existing=False):
        """
        Augments mkdir by adding an option to not fail if the folder exists
        """

        try:
            super(HoreySFTPClient, self).mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise

    def get_dir(self, remote_path, local_path):
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
            self.get(os.path.join(remote_path, attribute.filename), os.path.join(local_path, attribute.filename))


class RemoteDeployer:
    def __init__(self, configuration=None):
        self.configuration = configuration

    def deploy_blocks(self, blocks_to_deploy: List[MachineDeploymentBlock]):
        self.provision_remote_deployer_infrastructure(blocks_to_deploy)

        self.begin_provisioning_deployment_code(blocks_to_deploy)

        self.wait_for_deployment_code_provisioning_to_end(blocks_to_deploy)

        self.begin_deployment(blocks_to_deploy)

        self.wait_for_deployment_to_end(blocks_to_deploy)

    def provision_remote_deployer_infrastructure(self, deployment_targets):
        """
        """
        for deployment_target in deployment_targets:
            with self.get_deployment_target_client_context(deployment_target) as client:
                command = f"rm -rf {deployment_target.remote_target_deployment_directory_path}"
                logger.info(f"[REMOTE] {command}")
                client.exec_command(command)

                transport = client.get_transport()
                sftp_client = HoreySFTPClient.from_transport(transport)

                logger.info(f"sftp: mkdir {deployment_target.remote_target_deployment_directory_path}")
                sftp_client.mkdir(deployment_target.remote_target_deployment_directory_path, ignore_existing=True)

                logger.info(f"sftp: put_dir {deployment_target.remote_target_deployment_directory_path}")
                sftp_client.put_dir(deployment_target.local_deployment_dir_path,
                                    deployment_target.remote_target_deployment_directory_path)

                remote_output_dir = os.path.join(deployment_target.remote_target_deployment_directory_path, "output")
                logger.info(f"sftp: mkdir {remote_output_dir}")
                sftp_client.mkdir(remote_output_dir, ignore_existing=True)

                logger.info(f"sftp: Uploading '{os.path.join(deployment_target.remote_target_deployment_directory_path, 'remote_step_executor.sh')}'")
                sftp_client.put(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "remote_step_executor.sh"),
                                    os.path.join(deployment_target.remote_target_deployment_directory_path, "remote_step_executor.sh"))

                command = f"sudo chmod +x {os.path.join(deployment_target.remote_target_deployment_directory_path, 'remote_step_executor.sh')}"
                logger.info(f"[REMOTE] {command}")
                client.exec_command(command)

    def provision_target_remote_deployer_infrastructure(self, deployment_target, asynchronous=False):
        if asynchronous:
            thread = threading.Thread(target=self.provision_target_remote_deployer_infrastructure_thread, args=(deployment_target,))
            thread.start()
        else:
            self.provision_target_remote_deployer_infrastructure_thread(deployment_target)

    def provision_target_remote_deployer_infrastructure_thread(self, deployment_target):
        try:
            with self.get_deployment_target_client_context(deployment_target) as client:
                command = f"rm -rf {deployment_target.remote_target_deployment_directory_path}"
                logger.info(f"[REMOTE] {command}")
                client.exec_command(command)

                transport = client.get_transport()
                sftp_client = HoreySFTPClient.from_transport(transport)
                try:
                    logger.info(f"sftp: mkdir {deployment_target.remote_target_deployment_directory_path}")
                    sftp_client.mkdir(deployment_target.remote_target_deployment_directory_path, ignore_existing=True)

                    remote_output_dir = os.path.join(deployment_target.remote_target_deployment_directory_path,
                                                     "output")
                    logger.info(f"sftp: mkdir {remote_output_dir}")
                    sftp_client.mkdir(remote_output_dir, ignore_existing=True)
                except Exception as exception_instance:
                    raise RuntimeError(f"{deployment_target.deployment_target_address}") from exception_instance

                logger.info(f"sftp: put_dir from local {deployment_target.local_deployment_dir_path} to "
                            f"{deployment_target.deployment_target_address}:{deployment_target.remote_target_deployment_directory_path}")

                try:
                    sftp_client.put_dir(deployment_target.local_deployment_dir_path,
                                    deployment_target.remote_target_deployment_directory_path)
                except Exception as exception_instance:
                    raise RuntimeError(f"SFTP copping dir {deployment_target.local_deployment_dir_path} to "
                                       f"{deployment_target.remote_target_deployment_directory_path} to"
                                       f" {deployment_target.deployment_target_address}") from exception_instance

                logger.info(
                    f"sftp: Uploading '{os.path.join(deployment_target.remote_target_deployment_directory_path, 'remote_step_executor.sh')}'")
                sftp_client.put(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "remote_step_executor.sh"),
                                os.path.join(deployment_target.remote_target_deployment_directory_path,
                                             "remote_step_executor.sh"))

                command = f"sudo chmod +x {os.path.join(deployment_target.remote_target_deployment_directory_path, 'remote_step_executor.sh')}"
                logger.info(f"[REMOTE] {command}")
                client.exec_command(command)
                deployment_target.remote_deployer_infrastructure_provisioning_succeeded = True
        except Exception:
            deployment_target.remote_deployer_infrastructure_provisioning_succeeded = False
            raise
        finally:
            deployment_target.remote_deployer_infrastructure_provisioning_finished = True

    def deploy_target_step(self, deployment_target, step, asynchronous=False):
        if asynchronous:
            thread = threading.Thread(target=self.deploy_target_step_thread, args=(deployment_target, step))
            thread.start()
        else:
            self.deploy_target_step_thread(deployment_target, step)

    def deploy_target_step_thread(self, deployment_target, step):
        try:
            self.deploy_target_step_thread_helper(deployment_target, step)
        except Exception as exception_instance:
            step.status_code = step.StatusCode.ERROR
            step.output = repr(exception_instance)

    def deploy_target_step_thread_helper(self, deployment_target, step):
        with self.get_deployment_target_client_context(deployment_target) as client:
            self.execute_step(client, step)
            transport = client.get_transport()
            sftp_client = HoreySFTPClient.from_transport(transport)

            retry_attempts = 10
            sleep_time = 60
            for retry_counter in range(retry_attempts):
                try:
                    sftp_client.get(step.configuration.finish_status_file_path,
                                    os.path.join(deployment_target.local_deployment_data_dir_path,
                                                 step.configuration.finish_status_file_name))

                    sftp_client.get(step.configuration.output_file_path,
                                    os.path.join(deployment_target.local_deployment_data_dir_path, step.configuration.output_file_name))

                    sftp_client.get_dir(os.path.join(step.configuration.step_scripts_dir_path, "output"),
                                    deployment_target.local_deployment_dir_path)
                    break
                except IOError as error_received:
                    if "No such file" not in repr(error_received):
                        raise
                    logger.info(
                        f"Retrying to fetch remote script's status in {sleep_time} seconds ({retry_counter}/{retry_attempts})")
                time.sleep(sleep_time)
            else:
                raise TimeoutError(f"Failed to fetch remote script's status target: {deployment_target.deployment_target_address}")

            step.update_finish_status(deployment_target.local_deployment_data_dir_path)
            step.update_output(deployment_target.local_deployment_data_dir_path)

            if step.status_code != step.StatusCode.SUCCESS:
                last_lines = '\n'.join(step.output.split("\n")[-50:])
                raise RuntimeError(f"Step finished with status: {step.status}, error: \n{last_lines}")

            logger.info(f"Step finished successfully output in: '{step.configuration.output_file_name}'")

    def perform_recursive_replacements(self, replacements_base_dir_path, string_replacements):
        if not os.path.exists(replacements_base_dir_path):
            raise RuntimeError(f"No such directory '{replacements_base_dir_path}'")

        for root, _, filenames in os.walk(replacements_base_dir_path):
            for filename in filenames:
                if filename.startswith("template_"):
                    self.perform_file_string_replacements(root, filename, string_replacements)

    def perform_file_string_replacements(self, root, filename, string_replacements):
        logger.info(f"Performing replacements on template dir: '{root}' name: '{filename}'")
        with open(os.path.join(root, filename)) as file_handler:
            str_file = file_handler.read()

        for key in sorted(string_replacements.keys(), key=lambda key_string: len(key_string), reverse=True):
            if not key.startswith("STRING_REPLACEMENT_"):
                raise ValueError("Key must start with STRING_REPLACEMENT_")
            logger.info(f"Performing replacement in template: {filename}, key: {key}")
            value = string_replacements[key]
            str_file = str_file.replace(key, value)

        new_filename = filename[len("template_"):]

        with open(os.path.join(root, new_filename), "w+") as file_handler:
            file_handler.write(str_file)

        if "STRING_REPLACEMENT_" in str_file:
            raise ValueError(f"Not all STRING_REPLACEMENT_ were replaced in {os.path.join(root, new_filename)}")

    def begin_provisioning_deployment_code(self, deployment_targets: List[MachineDeploymentBlock]):
        for deployment_target in deployment_targets:
            with self.get_deployment_target_client_context(deployment_target) as client:
                transport = client.get_transport()
                sftp_client = HoreySFTPClient.from_transport(transport)
                self.execute_step(client, deployment_target.application_infrastructure_provision_step)
                self.wait_for_step_to_finish(deployment_target.application_infrastructure_provision_step, deployment_target.local_deployment_data_dir_path, sftp_client)

            deployment_target.deployment_code_provisioning_ended = True

    def wait_for_step_to_finish(self, step, local_deployment_data_dir_path, sftp_client):
        retry_attempts = 10
        sleep_time = 60
        for retry_counter in range(retry_attempts):
            try:
                sftp_client.get(step.configuration.finish_status_file_path,
                        os.path.join(local_deployment_data_dir_path, step.configuration.finish_status_file_name))

                sftp_client.get(step.configuration.output_file_path,
                                os.path.join(local_deployment_data_dir_path, step.configuration.output_file_name))
                break
            except IOError as error_received:
                if "No such file" not in repr(error_received):
                    raise
                logger.info(f"Retrying to fetch remote script's status in {sleep_time} seconds ({retry_counter}/{retry_attempts})")
            time.sleep(sleep_time)
        else:
            raise TimeoutError("Failed to fetch remote script's status")

        step.update_finish_status(local_deployment_data_dir_path)
        step.update_output(local_deployment_data_dir_path)

        if step.status_code != step.StatusCode.SUCCESS:
            last_lines = '\n'.join(step.output.split("\n")[-50:])
            raise RuntimeError(f"Step finished with status: {step.status}, error: \n{last_lines}")

        logger.info(f"Step finished successfully output in: '{step.configuration.output_file_name}'")

    def wait_for_deployment_code_provisioning_to_end(self, blocks_to_deploy: List[MachineDeploymentBlock]):
        for block_to_deploy in blocks_to_deploy:
            for i in range(60):
                if block_to_deploy.deployment_code_provisioning_ended:
                    break
                time.sleep(1)
            else:
                raise RuntimeError("Deployment failed at wait_for_deployment_code_provisioning_to_end")
        logger.info("Deployment provisioning finished successfully")

    def begin_deployment(self, deployment_targets: List[MachineDeploymentBlock]):
        for deployment_target in deployment_targets:
            with self.get_deployment_target_client_context(deployment_target) as client:
                transport = client.get_transport()
                sftp_client = HoreySFTPClient.from_transport(transport)

                self.execute_step(client, deployment_target.application_deploy_step)
                self.wait_for_step_to_finish(deployment_target.application_deploy_step, deployment_target.local_deployment_data_dir_path, sftp_client)

            deployment_target.deployment_code_provisioning_ended = True

    @staticmethod
    @contextmanager
    def get_deployment_target_client_context(block_to_deploy: MachineDeploymentBlock):
        with open(block_to_deploy.deployment_target_ssh_key_path, 'r') as ssh_key_file_handler:
            deployment_target_key = paramiko.RSAKey.from_private_key(StringIO(ssh_key_file_handler.read()))

        if block_to_deploy.bastion_address is None:
            with paramiko.SSHClient() as client:
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(
                    block_to_deploy.deployment_target_address,
                    port=22,
                    username=block_to_deploy.deployment_target_user_name,
                    pkey=deployment_target_key,
                    compress=True,
                    banner_timeout=60
                )
                yield client
            return

        with open(block_to_deploy.bastion_ssh_key_path, 'r') as bastion_key_file_handler:
            bastion_key = paramiko.RSAKey.from_private_key(StringIO(bastion_key_file_handler.read()))

        with open_tunnel(
                ssh_address_or_host=(block_to_deploy.bastion_address, 22),
                remote_bind_address=(block_to_deploy.deployment_target_address, 22),
                ssh_username=block_to_deploy.bastion_user_name,
                ssh_pkey=bastion_key) as tunnel:
            logger.info(f"Opened SSH tunnel to {block_to_deploy.deployment_target_address} via {block_to_deploy.bastion_address} ")

            with paramiko.SSHClient() as client:
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(
                    'localhost',
                    port=tunnel.local_bind_port,
                    username=block_to_deploy.deployment_target_user_name,
                    pkey=deployment_target_key,
                    compress=True,
                    banner_timeout=60
                )

                yield client
    
    @staticmethod
    def get_deployment_target_client(target: MachineDeploymentBlock):
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
                
    def execute_step(self, client: paramiko.SSHClient, step):
        command = f"screen -S deployer -dm {step.configuration.step_scripts_dir_path}/remote_step_executor.sh {step.configuration.remote_script_file_path} {step.configuration.script_configuration_file_path} {step.configuration.finish_status_file_path} {step.configuration.output_file_path}"
        logger.info(f"[REMOTE] {command}")

        client.exec_command(command)

    def get_status_path_from_script_path(self, script_path):
        pdb.set_trace()

    def get_output_path_from_script_path(self, script_path):
        pdb.set_trace()

    def wait_for_deployment_to_end(self, blocks_to_deploy):
        lst_errors = []
        for block in blocks_to_deploy:
            if block.application_deploy_step.status_code != MachineDeploymentStep.StatusCode.SUCCESS:
                lst_errors.append(block.application_infrastructure_provision_step.configuration.output_file_path)

        if lst_errors:
            raise RuntimeError(str(lst_errors))
        logger.info("Deployment finished successfully output in")

    def wait_to_finish(self, targets, check_callback, sleep_time=10, total_time=600):
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(seconds=total_time)

        while datetime.datetime.now() < end_time:
            if all([check_callback(target) for target in targets]):
                break

            logger.info(f"remote_deployer wait_to_finish going to sleep for {sleep_time} seconds")
            time.sleep(sleep_time)
        else:
            raise TimeoutError(f"Result: {[check_callback(target) for target in targets]}")

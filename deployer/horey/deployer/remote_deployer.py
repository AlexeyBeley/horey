import json
import pdb
import time

import paramiko
from sshtunnel import open_tunnel
import os
from datetime import time
from horey.deployer.machine_deployment_block import MachineDeploymentBlock
from horey.deployer.deployment_step_configuration_policy import DeploymentStepConfigurationPolicy
from typing import List
from contextlib import contextmanager
from io import StringIO


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


class RemoteDeployer:
    def __init__(self, configuration=None):
        self.configuration = configuration

    def deploy_blocks(self, blocks_to_deploy: List[MachineDeploymentBlock]):
        self.begin_provisioning_deployment_code(blocks_to_deploy)

        self.wait_for_deployment_code_provisioning_to_end(blocks_to_deploy)

        self.begin_deployment(blocks_to_deploy)

        self.wait_for_deployment_to_end(blocks_to_deploy)

    def begin_provisioning_deployment_code(self, blocks_to_deploy: List[MachineDeploymentBlock]):
        for block_to_deploy in blocks_to_deploy:
            with self.get_deployment_target_client(block_to_deploy) as client:
                transport = client.get_transport()
                sftp_client = HoreySFTPClient.from_transport(transport)
                sftp_client.put_dir(os.path.join(block_to_deploy.local_deployment_dir_path, block_to_deploy.remote_scripts_dir_name),
                                    block_to_deploy.remote_deployment_dir_path)

            self.execute_step(client, self.)

            block_to_deploy.deployment_code_provisioning_ended = True

    def wait_for_deployment_code_provisioning_to_end(self, blocks_to_deploy: List[MachineDeploymentBlock]):
        for block_to_deploy in blocks_to_deploy:
            for i in range(60):
                if block_to_deploy.deployment_code_provisioning_ended:
                    break
                time.sleep(1)
            else:
                raise RuntimeError("Deployment failed at wait_for_deployment_code_provisioning_to_end")

    def begin_deployment(self, blocks_to_deploy: List[MachineDeploymentBlock]):
        for block_to_deploy in blocks_to_deploy:
            with self.get_deployment_target_client(block_to_deploy) as client:
                self.execute_step(client, os.path.join(block_to_deploy.local_deployment_dir_path, block_to_deploy.remote_scripts_dir_name, block_to_deploy.deployment_step_configuration_file_name))

    @staticmethod
    @contextmanager
    def get_deployment_target_client(block_to_deploy: MachineDeploymentBlock):
        with open(block_to_deploy.bastion_ssh_key_path, 'r') as bastion_key_file_handler:
            bastion_key = paramiko.RSAKey.from_private_key(StringIO(bastion_key_file_handler.read()))
        with open(block_to_deploy.deployment_target_ssh_key_path, 'r') as bastion_key_file_handler:
            deployment_target_key = paramiko.RSAKey.from_private_key(StringIO(bastion_key_file_handler.read()))

        with open_tunnel(
                ssh_address_or_host=(block_to_deploy.bastion_address, 22),
                remote_bind_address=(block_to_deploy.deployment_target_address, 22),
                ssh_username=block_to_deploy.bastion_user_name,
                ssh_pkey=bastion_key) as tunnel:
            with paramiko.SSHClient() as client:
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(
                    'localhost',
                    port=tunnel.local_bind_port,
                    username=block_to_deploy.deployment_target_user_name,
                    pkey=deployment_target_key,
                    compress=True)

                yield client

    def execute_step(self, client: paramiko.SSHClient, step_configuration_file_path):
        configs = DeploymentStepConfigurationPolicy()
        configs.configuration_file_full_path = step_configuration_file_path
        configs.init_from_file()
        command = f"./configuration.remote_step_executor.sh {configs.scripts_dir_path}, {step_configuration_file_path}, {configs.finish_status_file_path}, {configs.output_file_path}"
        pdb.set_trace()
        client.exec_command(command)
        transport = client.get_transport()
        sftp_client = HoreySFTPClient.from_transport(transport)
        sftp_client.get(step_configuration_file_path.configuration_file_full_path,
                            step_configuration_file_path.configuration_file_full_path)

    def get_status_path_from_script_path(self, script_path):
        pdb.set_trace()

    def get_output_path_from_script_path(self, script_path):
        pdb.set_trace()

    def wait_for_deployment_to_end(self, blocks_to_deploy):
        pdb.set_trace()

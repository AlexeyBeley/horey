"""
Shamelessly stolen from:
https://github.com/lukecyca/pyslack
"""
import os
import json
import shutil

import requests
from horey.h_logger import get_logger
from horey.gitlab_api.gitlab_api_configuration_policy import GitlabAPIConfigurationPolicy
from horey.deployer.remote_deployer import RemoteDeployer
from horey.deployer.deployment_target import DeploymentTarget
from horey.deployer.deployment_step_configuration_policy import DeploymentStepConfigurationPolicy
from horey.deployer.deployment_step import DeploymentStep
# pylint: disable=no-name-in-module
from horey.provision_constructor.provision_constructor import ProvisionConstructor

logger = get_logger()


class GitlabAPI:
    """
    Main Class.
    """

    def __init__(self, configuration: GitlabAPIConfigurationPolicy = None):
        self.projects = []
        self.token = configuration.token
        self.group_id = configuration.group_id
        self.base_address = "https://gitlab.com"
        self._deployer = None

    @property
    def deployer(self):
        """
        Remote deployer, initialized if needed.

        @return:
        """

        if self._deployer is None:
            self._deployer = RemoteDeployer()
        return self._deployer

    def get(self, request_path):
        """
        Compose and send GET request.

        @param request_path:
        @return:
        """

        request = self.create_request(request_path)
        return self.get_raw(request)

    def get_raw(self, request):
        """
        Send raw get request

        @param request:
        @return:
        """

        headers = {}

        if self.token is not None:
            headers["PRIVATE-TOKEN"] = self.token

        response = requests.get(
            request,
            headers=headers
        )
        if response.status_code != 200:
            raise RuntimeError(
                f'Request to gitlab api returned an error {response.status_code}, the response is:\n{response.text}'
            )
        return response.json()

    def post(self, request_path, data):
        """
        Compose and send POST request

        @param request_path:
        @param data:
        @return:
        """

        request = self.create_request(request_path)
        return self.post_raw(request, data)

    def post_raw(self, request, data):
        """
        Send POST request.

        @param request:
        @param data:
        @return:
        """

        headers = {"Content-Type": "application/json"}

        if self.token is not None:
            headers["PRIVATE-TOKEN"] = self.token

        response = requests.post(
            request, data=json.dumps(data),
            headers=headers)

        if response.status_code not in [200, 201]:
            raise RuntimeError(
                f'Request to gitlab api returned an error {response.status_code}, the response is:\n{response.text}'
            )
        return response.json()

    def delete(self, request_path):
        """
        Compose and send DELETE request.

        @param request_path:
        @return:
        """

        request = self.create_request(request_path)
        headers = {"Content-Type": "application/json"}

        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"

        response = requests.delete(
            request,
            headers=headers
        )
        if response.status_code not in [200, 201]:
            raise RuntimeError(
                f'Request to gitlab api returned an error {response.status_code}, the response is:\n{response.text}'
            )
        return response.json()

    def create_request(self, request: str):
        """
        Construct request.

        #request = "https://gitlab.com/api/v4/groups/{group_id}/projects"
        @param request:
        @return:
        """

        if request.startswith("/"):
            request = request[1:]

        return f"{self.base_address}/api/v4/{request}"

    def init_projects(self):
        """
        Init projects

        @return:
        """

        for dict_src in self.get(f"groups/{self.group_id}/projects"):
            self.projects.append(dict_src)

    def add_user_to_projects(self, projects, user_id):
        """
        Add user as member to projects.

        @param projects:
        @param user_id:
        @return:
        """
        for dict_src in projects:
            ret = self.get_raw(dict_src["_links"]["members"])
            if user_id in str(ret):
                continue
            data = {"user_id": user_id, "access_level": 40}
            try:
                self.post(f"projects/{dict_src['id']}/members", data)
                logger.info(f"Added to {dict_src['name']}")
            except Exception as inst:
                logger.error(f"{dict_src['name']} : {repr(inst)}")
                if "An error 403" not in repr(inst):
                    raise

    def provision_gitlab_runner_with_jenkins_authenticator(self, public_ip_address, ssh_key_file_path, gitlab_registration_token):
        """
        Provision all jenkins-agent services and system functionality.
        Boostrap the provision_constructor script.
        Using provision constructor provision the system.

        :return:
        """
        target = DeploymentTarget()

        target.deployment_target_address = public_ip_address
        target.deployment_target_user_name = "ubuntu"
        target.deployment_target_ssh_key_path = ssh_key_file_path

        self.generate_deployment_dir_bootstrap_files(target.local_deployment_dir_path, target.deployment_data_dir_name, gitlab_registration_token)

        target.add_step(self.generate_provision_constructor_bootstrap_step())
        target.add_step(self.generate_application_software_provisioning_step())

        self.deployer.deploy_target(target)

        if target.status_code != target.StatusCode.SUCCESS:
            raise RuntimeError(target.status_code)

    def generate_deployment_dir_bootstrap_files(self, local_deployment_dir_path, deployment_data_dir_name,
                                                gitlab_registration_token):
        """
        Generate deployment files and prepare the local dir.

        @param gitlab_registration_token:
        @param deployment_data_dir_name:
        @param local_deployment_dir_path:
        @return:
        """
        shutil.rmtree(local_deployment_dir_path)
        os.makedirs(os.path.join(local_deployment_dir_path, deployment_data_dir_name), exist_ok=True)

        source_scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gitlab_runner", "remote_scripts")

        for filename in os.listdir(source_scripts_dir):
            shutil.copyfile(os.path.join(source_scripts_dir, filename), os.path.join(local_deployment_dir_path, filename))

        string_replacements = {
            "STRING_REPLACEMENT_GITLAB_REGISTRATION_TOKEN": gitlab_registration_token
        }

        self.deployer.perform_recursive_replacements(local_deployment_dir_path, string_replacements)

        ProvisionConstructor.generate_provision_constructor_bootstrap_script(local_deployment_dir_path,
                                                                             ProvisionConstructor.PROVISION_CONSTRUCTOR_BOOTSTRAP_SCRIPT_NAME)

    @staticmethod
    def generate_provision_constructor_bootstrap_step():
        """
        Generate the deployment step used to bootstrap provision_constructor.

        :return:
        """

        step_configuration = DeploymentStepConfigurationPolicy("ProvisionConstructorBootstrap")
        step_configuration.script_name = ProvisionConstructor.PROVISION_CONSTRUCTOR_BOOTSTRAP_SCRIPT_NAME

        step = DeploymentStep(step_configuration)
        step_configuration.generate_configuration_file(step_configuration.script_configuration_file_path)
        return step

    @staticmethod
    def generate_application_software_provisioning_step():
        """
        Generate the deployment step used to provision all the needed services.

        :return:
        """

        step_configuration = DeploymentStepConfigurationPolicy("AgentApplicationDeployment")
        step_configuration.script_name = "provision_gitlab_runner.sh"

        step = DeploymentStep(step_configuration)
        step_configuration.generate_configuration_file(step_configuration.script_configuration_file_path)
        return step

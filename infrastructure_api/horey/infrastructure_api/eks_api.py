"""
Standard ECS maintainer.

"""
import json
import os
import pathlib
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from horey.h_logger import get_logger

from horey.aws_api.aws_services_entities.ecr_image import ECRImage
from horey.aws_api.aws_services_entities.ecr_repository import ECRRepository
from horey.aws_api.base_entities.region import Region
from horey.infrastructure_api.cloudwatch_api_configuration_policy import CloudwatchAPIConfigurationPolicy
from horey.infrastructure_api.eks_api_configuration_policy import EKSAPIConfigurationPolicy
from horey.infrastructure_api.environment_api import EnvironmentAPI
from horey.infrastructure_api.build_api import BuildAPI, BuildAPIConfigurationPolicy

logger = get_logger()


class KSAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration: EKSAPIConfigurationPolicy, environment_api: EnvironmentAPI):
        self.configuration = configuration
        self.environment_api = environment_api
        self._build_api = None

    @property
    def ecr_repo_uri(self):
        """
        Generate repo URI.

        :return:
        """

        return f"{self.environment_api.aws_api.ecs_client.account_id}.dkr.ecr.{self.configuration.ecr_repository_region}.amazonaws.com/{self.configuration.ecr_repository_name}"


    @property
    def build_api(self):
        """
        Standard

        :return:
        """

        if self._build_api is None:
            config = BuildAPIConfigurationPolicy()
            config.docker_repository_uri = self.ecr_repo_uri
            build_api = BuildAPI(configuration=config, environment_api=self.environment_api)
            build_api.git_api = build_api.horey_git_api
            self._build_api = build_api
        return self._build_api

    @build_api.setter
    def build_api(self, value):
        if not isinstance(value,BuildAPI):
            raise ValueError("Must be BuildAPI")
        self._build_api = value

    def provision_service(self):
        """
        Provision service.

        :return:
        """

        self.build_api = BuildAPI(self.configuration.build_api_configuration_policy)



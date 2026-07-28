"""
Standard ECS maintainer.

"""

from horey.h_logger import get_logger

from horey.aws_api.aws_services_entities.ecr_image import ECRImage
from horey.aws_api.aws_services_entities.ecr_repository import ECRRepository
from horey.aws_api.base_entities.region import Region
from horey.infrastructure_api.cloudwatch_api_configuration_policy import CloudwatchAPIConfigurationPolicy
from horey.infrastructure_api.eks_api_configuration_policy import EKSAPIConfigurationPolicy
from horey.infrastructure_api.environment_api import EnvironmentAPI
from horey.infrastructure_api.build_api import BuildAPI, BuildAPIConfigurationPolicy
from horey.infrastructure_api.ecs_api import ECSAPI, ECSAPIConfigurationPolicy

logger = get_logger()


class EKSAPI:
    """
    Manage EKS.

    """

    def __init__(self, configuration: EKSAPIConfigurationPolicy, environment_api: EnvironmentAPI):
        self.configuration = configuration
        self.environment_api = environment_api
        self._build_api = None
        self._ecs_api = None

    @property
    def build_api(self):
        """
        Standard

        :return:
        """

        if self._build_api is None:
            config = BuildAPIConfigurationPolicy()
            config.docker_repository_uri = self.ecs_api.ecr_repo_uri
            build_api = BuildAPI(configuration=config, environment_api=self.environment_api)
            build_api.git_api = build_api.horey_git_api
            self._build_api = build_api
        return self._build_api

    @build_api.setter
    def build_api(self, value):
        if not isinstance(value,BuildAPI):
            raise ValueError("Must be BuildAPI")
        self._build_api = value

    @property
    def ecs_api(self):
        """
        Standard

        :return:
        """

        if self._ecs_api is None:
            config = ECSAPIConfigurationPolicy()
            _ecs_api = ECSAPI(configuration=config, environment_api=self.environment_api)
            self._ecs_api = _ecs_api
        return self._ecs_api

    @build_api.setter
    def build_api(self, value):
        if not isinstance(value,BuildAPI):
            raise ValueError("Must be BuildAPI")
        self._build_api = value

    def provision_service(self, branch_name):
        """
        Provision service.

        :return:
        """

        build_numer = self.ecs_api.get_next_build_number()
        image = self.build_api.run_build_and_upload_image_routine(branch_name, build_numer)

        for image_reference in image.tags:
            if self.ecs_api.configuration.ecr_repository_name in image_reference:
                break
        else:
            raise ValueError(f"Was not able to find image with repo {self.configuration.ecr_repository_name}")

        self.provision_deployment(image_reference)

    def provision_deployment(self, image_reference):
        """
        Provision deployment.

        :return:
        """
        breakpoint()




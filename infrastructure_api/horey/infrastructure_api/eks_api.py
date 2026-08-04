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
        self.build_api.init_commit_id()

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
         

        str_yaml = self.deployment_yaml()
        str_yaml = str_yaml.replace("IMAGE_REFERENCE", image_reference)
        deployment_file_path = self.environment_api.configuration.data_directory_path / "deployment.yaml"
        with open(deployment_file_path, "w", encoding="utf-8") as fh:
            fh.write(str_yaml)
        command = f"kubectl apply -f {deployment_file_path}"
        print(command)
        logger.info(f"Run command: {command}")
        breakpoint()


    @staticmethod
    def deployment_yaml():
        return """
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: test-frs
  name: test-frs
  namespace: default
spec:
  progressDeadlineSeconds: 600
  replicas: 1
  revisionHistoryLimit: 10
  selector:
    matchLabels:
      app: test-frs
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: test-frs
    spec:
      containers:
      - image: IMAGE_REFERENCE 
        imagePullPolicy: Always 
        name: frs
        resources: {}
        terminationMessagePath: /dev/termination-log
        terminationMessagePolicy: File
        resources:
          requests:
            memory: "2Gi"   # Guaranteed 2GB RAM allocated for the container
          limits:
            memory: "3Gi"   # Hard cap at 2GB RAM to prevent OOM spiking
      dnsPolicy: ClusterFirst
      restartPolicy: Always
      schedulerName: default-scheduler
      securityContext: {}
      terminationGracePeriodSeconds: 30
      """





"""
Build API.

"""
import json
import shutil
import time
import uuid
from pathlib import Path

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.h_logger import get_logger

from horey.aws_api.base_entities.region import Region
from horey.infrastructure_api.build_api_configuration_policy import BuildAPIConfigurationPolicy
from horey.git_api.git_api import GitAPIConfigurationPolicy, GitAPI

logger = get_logger()


class BuildAPI:
    """
    Manage builds.

    """

    def __init__(self, configuration: BuildAPIConfigurationPolicy, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api
        self.commit_id = None
        self._horey_git_api = None
        self._git_api = None
        self._build_directory = None
        self._docker_registries_credentials = {}

    @property
    def horey_git_api(self):
        """
        Standard.

        :return:
        """
        if self._horey_git_api is None:
            self.init_horey_git_api()
        return self._horey_git_api

    @property
    def git_api(self):
        """
        Standard.

        :return:
        """

        return self._git_api

    @git_api.setter
    def git_api(self, value):
        """
        Standard.

        :return:
        """

        self._git_api = value

    def init_horey_git_api(self):
        """
        Init default.

        :return:
        """

        configuration = GitAPIConfigurationPolicy()
        configuration.git_directory_path = "/tmp/git"
        configuration.remote = "https://github.com/AlexeyBeley/horey.git"
        self._horey_git_api = GitAPI(configuration=configuration)

    def run_build_image_routine(self, branch_name, build_number, nocache=False, dockerfile="Dockerfile"):
        """
        Run the build and upload routine

        :return:
        """

        source_code_directory_path = self.prepare_source_code_directory(branch_name)
        build_directory = self.prepare_docker_image_build_directory(source_code_directory_path, build_number)
        tags = self.generate_docker_image_tags(build_number)
        image = self.build_docker_image(build_directory, tags, nocache=nocache, dockerfile=dockerfile)
        # todo: self.validate_docker_image()
        self.upload_docker_image_to_artifactory(tags)
        return image

    def prepare_source_code_directory(self, branch_name):
        """

        :return:
        """


        logger.info(f"Preparing source code directory, {branch_name=}")
        perf_counter_start = time.perf_counter()

        self.git_api.update_local_source_code(branch_name)
        self.commit_id = self.git_api.get_commit_id()

        logger.info(f"Prepared source code directory commit: {self.commit_id}. Took {time.perf_counter() - perf_counter_start}")
        return self.git_api.configuration.directory_path

    @property
    def docker_build_directory(self):
        """
        Build dir

        :return:
        """

        if self._build_directory is None:
            build_dir_path = Path("/tmp/ecs_api_build_temp_dirs") / str(uuid.uuid4())
            build_dir_path.parent.mkdir(exist_ok=True)
            self._build_directory = build_dir_path
        return self._build_directory

    def prepare_docker_image_build_directory(self, source_code_directory_path, build_number):
        """
        Copy source code to tmp dir.

        :param build_number:
        :param source_code_directory_path:
        :return:
        """

        logger.info(f"Preparing docker build directory' {source_code_directory_path}' to '{self.docker_build_directory}'")
        perf_counter_start = time.perf_counter()

        def ignore_git(_, file_names):
            return ["_build"] + [".git", ".gitmodules", ".idea"] if ".git" in file_names else []

        shutil.copytree(str(source_code_directory_path), str(self.docker_build_directory), ignore=ignore_git)

        build_dir_path = self.prepare_docker_image_build_directory_callback(self.docker_build_directory)

        self.add_build_metadata_file(build_dir_path, build_number)

        logger.info(f"Prepared docker build directory. Took {time.perf_counter() - perf_counter_start}")

        return build_dir_path

    def add_build_metadata_file(self, build_dir_path, build_number):
        """
        Standard

        :return:
        """

        with open(build_dir_path / "build_metadata.json", "w", encoding="utf-8") as file_handler:
            json.dump({"commit": self.commit_id, "build": str(build_number)}, file_handler)

    def prepare_docker_image_build_directory_callback(self, build_dir_path: Path):
        """
        Echo.

        :param build_dir_path:
        :return:
        """

        return build_dir_path

    def generate_docker_image_tags(self, build_number):
        """
        Generate tags.

        :param build_number:
        :return:
        """

        tag = f"{self.configuration.docker_repository_uri}:build_{build_number + 1}"
        if self.commit_id:
            tag += f"-commit_{self.commit_id}"
        return [tag]

    def build_docker_image(self, dir_path: Path, tags, nocache=False, dockerfile="Dockerfile"):
        """
        Image building fails for different reasons, this function aggregates the reasons and handles them.

        :param dir_path:
        :param tags:
        :return:
        """

        for _ in range(120):
            try:
                logger.info(f"Building docker image with arguments: {self.configuration.docker_build_arguments}")
                return self.environment_api.docker_api.build(str(dir_path), tags, nocache=nocache, **self.configuration.docker_build_arguments)
            except Exception as error_inst:
                repr_error_inst = repr(error_inst).lower()
                if "authorization token has expired" in repr_error_inst:
                    logout = True
                elif "authentication is required" in repr_error_inst:
                    logout = False
                else:
                    raise

                for registry, username, password in self.extract_registries_credentials_from_dockerfile(dir_path / dockerfile):
                    if logout:
                        self.environment_api.docker_api.logout(registry)
                    self.environment_api.docker_api.login(registry, username, password)

                return self.environment_api.docker_api.build(str(dir_path), tags, **self.configuration.docker_build_arguments)

        raise TimeoutError("Was not able to build and image")

    def extract_registries_credentials_from_dockerfile(self, dockerfile_path: Path):
        """
        Extract credentials.

        :param dockerfile_path:
        :return:
        """

        lst_ret = []

        with open(dockerfile_path, encoding="utf-8") as file_handler:
            for line in file_handler.readlines():
                line = line.strip("\n").lower()
                if line.startswith("from"):
                    registry = line.split(" ")[1].split("/")[0]
                    lst_ret.append((registry, *self._docker_registries_credentials[registry]))
        return lst_ret

    def login_to_ecr_registry(self, region, logout=False):
        """
        Login or re-login

        :param logout:
        :param region:
        :return:
        """

        logger.info(f"Login to AWS Docker Repo (ECR) in region: {region.region_mark}")
        credentials = self.environment_api.aws_api.get_ecr_authorization_info(region=region)

        if len(credentials) != 1:
            raise ValueError("len(credentials) != 1")
        credentials = credentials[0]

        registry, username, password = credentials["proxy_host"], credentials["user_name"], credentials["decoded_token"]
        if logout:
            self.environment_api.docker_api.logout(registry)
        self.environment_api.docker_api.login(registry, username, password)
        return registry, username, password

    def upload_docker_image_to_artifactory(self, tags):
        """
        Standard.
        "ecr:CompleteLayerUpload",
        "ecr:GetAuthorizationToken",
        "ecr:UploadLayerPart",
        "ecr:InitiateLayerUpload",
        "ecr:BatchCheckLayerAvailability",
        "ecr:PutImage"

        :param tags:
        :return:
        """

        try:
            self.environment_api.docker_api.upload_images(tags)
        except Exception as inst_error:
            repr_inst_err = repr(inst_error)
            if "no basic auth credentials" in repr_inst_err or \
                    "Your authorization token has expired. Reauthenticate and try again" in repr_inst_err:
                ecr_repository_region = tags[0].split(".")[3]
                registry, _, _ = self.login_to_ecr_registry(Region.get_region(ecr_repository_region))
                self.environment_api.docker_api.logout(registry)
                self.login_to_ecr_registry(Region.get_region(ecr_repository_region))
                self.environment_api.docker_api.upload_images(tags)
            else:
                raise

    def add_docker_registry_credentials(self, registry_url, user, password):
        """
        Add custom registry

        :param registry_url:
        :param user:
        :param password:
        :return:
        """

        self._docker_registries_credentials[registry_url] = (user, password)

    def add_ecr_registry_credentials(self):
        """
        '<aws_account>.dkr.ecr.us-west-2.amazonaws.com/<repo>:<tag>'
        :return:
        """

        self.add_docker_registry_credentials(*self.get_ecr_registry_credentials())

    def get_ecr_registry_credentials(self):
        """
        Get credentials to a region.

        :param region:
        :return:
        """

        logger.info(f"Login to AWS Docker Repo (ECR) in region: {self.environment_api.configuration.region}")
        credentials = self.environment_api.aws_api.get_ecr_authorization_info(region=self.environment_api.region)

        if len(credentials) != 1:
            raise ValueError("len(credentials) != 1")
        credentials = credentials[0]

        registry, username, password = credentials["proxy_host"], credentials["user_name"], credentials["decoded_token"]
        self.environment_api.docker_api.login(registry, username, password)
        return registry, username, password

    def copy_docker_image(self, src_ecs_api=None, dst_ecs_api=None):
        """
        Copy from source to dst.

        :param src_ecs_api:
        :param dst_ecs_api:
        :return:
        """

        if src_ecs_api is None:
            raise NotImplementedError("src_ecs_api is None")
        if dst_ecs_api is None:
            raise NotImplementedError("dst_ecs_api is None")

        latest_source_build = src_ecs_api.fetch_latest_artifact_metadata()

        # todo: there is a problem with global AWS account, once set to src - it is not reset to DST and fails on permissions.
        # it is exposed when calling to this function, src_ecs_api argument sets the AWs account
        latest_dst_build = dst_ecs_api.fetch_latest_artifact_metadata()

        if latest_dst_build and latest_dst_build.image_tags == latest_source_build.image_tags:
            return True

        image_registry_reference = src_ecs_api.generate_image_registry_reference(latest_source_build.image_tags[0])

        for _ in range(3):
            try:
                return self.environment_api.docker_api.copy_image(image_registry_reference, dst_ecs_api.ecr_repository.repository_uri, copy_all_tags=True)
            except Exception as inst_error:
                # Different ECR regions generate errors differently - part goes to repr part to str.
                if "no basic auth credentials" not in repr(inst_error) + str(inst_error):
                    raise

                if src_ecs_api.ecr_repository.repository_uri in repr(inst_error).replace("%2F", "/"):
                    region_mark = src_ecs_api.ecr_repository.repository_uri.split(".")[3]
                elif dst_ecs_api.ecr_repository.repository_uri in repr(inst_error).replace("%2F", "/"):
                    region_mark = dst_ecs_api.ecr_repository.repository_uri.split(".")[3]
                else:
                    raise
                self.login_to_ecr_registry(Region.get_region(region_mark))
        raise RuntimeError("Was not able to copy image after 3 retries - 1 retry per each ECR region and final after both did relogin")


    def init_temporary_source_code_directory(self):
        """
        Create temporary source code directory.

        :return:
        """

        tmp_dir = Path("/tmp") / str(uuid.uuid4())
        tmp_dir.mkdir(parents=True)
        self.configuration.tmp_source_code_dir_path = tmp_dir
        return tmp_dir
    
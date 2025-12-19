"""
Build API.

"""
import json
import shutil
import uuid
from pathlib import Path

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

    def run_build_image_routine(self, branch_name, build_number, nocache=False):
        """
        Run the build and upload routine

        :return:
        """

        source_code_directory_path = self.prepare_source_code_directory(branch_name)
        build_directory = self.prepare_docker_image_build_directory(source_code_directory_path, build_number)
        tags = self.generate_docker_image_tags(build_number)
        image = self.build_docker_image(build_directory, tags, nocache=nocache)
        # todo: self.validate_docker_image()
        self.upload_docker_image_to_artifactory(tags)
        return image

    def prepare_source_code_directory(self, branch_name):
        """

        :return:
        """

        self.git_api.update_local_source_code(branch_name)
        self.commit_id = self.git_api.get_commit_id()
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

        logger.info(f"Start copying source code from '{source_code_directory_path}' to '{self.docker_build_directory}'")

        def ignore_git(x, file_names):
            return ["_build"] + [".git", ".gitmodules", ".idea"] if ".git" in file_names else []

        shutil.copytree(str(source_code_directory_path), str(self.docker_build_directory), ignore=ignore_git)

        build_dir_path = self.prepare_docker_image_build_directory_callback(self.docker_build_directory)

        self.add_build_metadata_file(build_dir_path, build_number)

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

    def build_docker_image(self, dir_path, tags, nocache=False):
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
                repr_error_inst = repr(error_inst)
                if "authorization token has expired" not in repr_error_inst:
                    raise

                ecr_repository_region = tags[0].split(".")[3]
                _, _, _ = self.login_to_ecr_registry(region=Region.get_region(ecr_repository_region), logout=True)
                return self.environment_api.docker_api.build(str(dir_path), tags, **self.configuration.docker_build_arguments)

        raise TimeoutError("Was not able to build and image")

    def login_to_ecr_registry(self, region, logout=False):
        """
        Login or relogin

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

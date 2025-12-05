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

logger = get_logger()


class BuildAPI:
    """
    Manage builds.

    """

    def __init__(self, configuration: BuildAPIConfigurationPolicy, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api
        self.commit_id = None

    def run_build_image_routine(self, branch_name, build_number):
        """
        Run the build and upload routine

        :return:
        """

        source_code_directory_path = self.prepare_source_code_directory(branch_name)
        build_directory = self.prepare_docker_image_build_directory(source_code_directory_path, build_number)
        tags = self.generate_docker_image_tags(build_number)
        image = self.build_docker_image(build_directory, tags)
        # todo: self.validate_docker_image()
        self.upload_docker_image_to_artifactory(tags)
        return image

    def prepare_source_code_directory(self, branch_name):
        """

        :return:
        """

        self.environment_api.git_api.checkout_remote(branch_name)
        self.commit_id = self.environment_api.git_api.get_commit_id()
        return self.environment_api.git_api.configuration.directory_path

    def prepare_docker_image_build_directory(self, source_code_directory_path, build_number):
        """
        Copy source code to tmp dir.

        :param build_number:
        :param source_code_directory_path:
        :return:
        """

        build_dir_path = Path("/tmp/ecs_api_build_temp_dirs") / str(uuid.uuid4())
        build_dir_path.parent.mkdir(exist_ok=True)

        def ignore_git(_, file_names):
            return [".git", ".gitmodules", ".idea"] if ".git" in file_names else []

        shutil.copytree(str(source_code_directory_path), str(build_dir_path), ignore=ignore_git)

        build_dir_path = self.prepare_docker_image_build_directory_callback(build_dir_path)

        with open(build_dir_path / "build_metadata.json", "w", encoding="utf-8") as file_handler:
            json.dump({"commit": self.commit_id, "build": str(build_number)}, file_handler)

        return build_dir_path

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

    def build_docker_image(self, dir_path, tags):
        """
        Image building fails for different reasons, this function aggregates the reasons and handles them.

        :param dir_path:
        :param tags:
        :return:
        """

        for _ in range(120):
            try:
                return self.environment_api.docker_api.build(str(dir_path), tags, **self.configuration.docker_build_arguments)
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

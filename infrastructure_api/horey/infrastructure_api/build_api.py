"""
Build API.

"""
from horey.h_logger import get_logger

from horey.infrastructure_api.build_api_configuration_policy import BuildAPIConfigurationPolicy

logger = get_logger()


class BuildAPI:
    """
    Manage builds.

    """

    def __init__(self, configuration: BuildAPIConfigurationPolicy, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

    def run_build_image_routine(self):
        """
        Run the build and upload routine

        :return:
        """

        source_code_directory_path = self.prepair_source_code_directory()
        self.validate_source_code()
        build_directory = self.prepair_docker_image_build_directory(source_code_directory_path)
        image = self.build_docker_image(build_directory)
        self.validate_docker_image()
        self.upload_docker_image_to_artifactory(image)

    def prepair_source_code_directory(self):
        """

        :return:
        """
        breakpoint()
        self.environment_api.git_api.checkout_remote()


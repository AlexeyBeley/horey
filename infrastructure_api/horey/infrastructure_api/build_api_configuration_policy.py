"""
AWS Lambda config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class BuildAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._build_image = None
        self._docker_build_arguments = None
        self._docker_repository_uri = None

    @property
    def build_image(self):
        if self._build_image is None:
            return True

        return self._build_image

    @build_image.setter
    def build_image(self, value):
        self._build_image = value

    @property
    def docker_build_arguments(self):
        if self._docker_build_arguments is None:
            return {"nocache": False, "platform": "linux/amd64"}

        return self._docker_build_arguments

    @docker_build_arguments.setter
    def docker_build_arguments(self, value):
        self._docker_build_arguments = value
    
    @property
    def docker_repository_uri(self):
        self.check_defined()
        return self._docker_repository_uri

    @docker_repository_uri.setter
    def docker_repository_uri(self, value):
        self._docker_repository_uri = value

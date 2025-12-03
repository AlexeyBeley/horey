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

    @property
    def build_image(self):
        if self._build_image is None:
            return True

        return self._build_image

    @build_image.setter
    def build_image(self, value):
        self._build_image = value

"""
AWS IAM config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy


# pylint: disable= missing-function-docstring, too-many-instance-attributes


class AWSIAMAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._role_name = None
        self._assume_role_policy_document = None

    @property
    def assume_role_policy_document(self):
        if self._assume_role_policy_document is None:
            raise self.UndefinedValueError("assume_role_policy_document")
        return self._assume_role_policy_document

    @assume_role_policy_document.setter
    def assume_role_policy_document(self, value):
        self._assume_role_policy_document = value

    @property
    def role_name(self):
        if self._role_name is None:
            raise self.UndefinedValueError("role_name")
        return self._role_name

    @role_name.setter
    def role_name(self, value):
        self._role_name = value

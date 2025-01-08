"""
AWS Lambda config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class AWSLambdaAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._lambda_name = None
        self._lambda_role_name = None
        self._ecr_repository_region = None
        self._git_remote_url = None
        self._environment_variables = None
        self._security_groups = None
        self._schedule_expression = None

    @property
    def schedule_expression(self):
        return self._schedule_expression

    @schedule_expression.setter
    def schedule_expression(self, value):
        self._schedule_expression = value

    @property
    def security_groups(self):
        if self._security_groups is None:
            raise self.UndefinedValueError("security_groups")
        return self._security_groups

    @security_groups.setter
    def security_groups(self, value):
        self._security_groups = value

    @property
    def environment_variables(self):
        if self._environment_variables is None:
            raise self.UndefinedValueError("environment_variables")
        return self._environment_variables

    @environment_variables.setter
    def environment_variables(self, value):
        self._environment_variables = value

    @property
    def git_remote_url(self):
        if self._git_remote_url is None:
            raise self.UndefinedValueError("git_remote_url")
        return self._git_remote_url

    @git_remote_url.setter
    def git_remote_url(self, value):
        self._git_remote_url = value

    @property
    def ecr_repository_region(self):
        if self._ecr_repository_region is None:
            raise self.UndefinedValueError("ecr_repository_region")
        return self._ecr_repository_region

    @ecr_repository_region.setter
    def ecr_repository_region(self, value):
        self._ecr_repository_region = value

    @property
    def lambda_role_name(self):
        if self._lambda_role_name is None:
            raise self.UndefinedValueError("lambda_role_name")
        return self._lambda_role_name

    @lambda_role_name.setter
    def lambda_role_name(self, value):
        self._lambda_role_name = value

    @property
    def lambda_name(self):
        if self._lambda_name is None:
            raise self.UndefinedValueError("lambda_name")
        return self._lambda_name

    @lambda_name.setter
    def lambda_name(self, value):
        self._lambda_name = value

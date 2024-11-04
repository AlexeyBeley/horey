"""
Horey infra knowledge as a code.

"""


class InfrastructureAPI:
    """
    Manage Knowledge.

    """
    def __init__(self):
        pass

    def get_environment_api(self, configuration, aws_api=None):
        """
        Get EnvironmentAPI

        :param configuration:
        :param aws_api:
        :return:
        """

        from horey.infrastructure_api.environment_api import EnvironmentAPI
        return EnvironmentAPI(configuration, aws_api=aws_api)

    def get_frontend_api(self, configuration, environment_api):
        """
        Get frontend API

        :param configuration:
        :param environment_api:
        :return:
        """

        from horey.infrastructure_api.frontend_api import FrontendAPI
        from horey.infrastructure_api.environment_api import EnvironmentAPI
        if not isinstance(environment_api, EnvironmentAPI):
            raise ValueError(f"{environment_api} not instance of EnvironmentAPI")

        return FrontendAPI(configuration, environment_api)

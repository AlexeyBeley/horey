"""
Horey infra knowledge as a code.

"""

# pylint: disable= import-outside-toplevel, no-name-in-module


class InfrastructureAPI:
    """
    Manage Knowledge.

    """

    def get_environment_api(self, configuration, aws_api):
        """
        Get EnvironmentAPI

        :param configuration:
        :param aws_api:
        :return:
        """

        from horey.infrastructure_api.environment_api import EnvironmentAPI
        return EnvironmentAPI(configuration, aws_api)

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

    def get_ecs_api(self, configuration, environment_api):
        """
        Get frontend API

        :param configuration:
        :param environment_api:
        :return:
        """

        from horey.infrastructure_api.ecs_api import ECSAPI
        from horey.infrastructure_api.environment_api import EnvironmentAPI
        if not isinstance(environment_api, EnvironmentAPI):
            raise ValueError(f"{environment_api} not instance of EnvironmentAPI")

        return ECSAPI(configuration, environment_api)

    def get_alerts_api(self, configuration, environment_api):
        """
        Get alerts API

        :param configuration:
        :param environment_api:
        :return:
        """

        from horey.infrastructure_api.alerts_api import AlertsAPI
        from horey.infrastructure_api.environment_api import EnvironmentAPI
        if not isinstance(environment_api, EnvironmentAPI):
            raise ValueError(f"{environment_api} not instance of EnvironmentAPI")

        return AlertsAPI(configuration, environment_api)

    def get_email_api(self, configuration, environment_api):
        """
        Get email API

        :param configuration:
        :param environment_api:
        :return:
        """

        from horey.infrastructure_api.email_api import EmailAPI
        from horey.infrastructure_api.environment_api import EnvironmentAPI
        if not isinstance(environment_api, EnvironmentAPI):
            raise ValueError(f"{environment_api} not instance of EnvironmentAPI")

        return EmailAPI(configuration, environment_api)

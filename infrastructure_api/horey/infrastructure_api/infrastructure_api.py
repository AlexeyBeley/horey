"""
Horey infra knowledge as a code.

"""

# pylint: disable= import-outside-toplevel, no-name-in-module


class InfrastructureAPI:
    """
    Manage Knowledge.

    """

    @staticmethod
    def get_environment_api(configuration, aws_api, git_api=None):
        """
        Get EnvironmentAPI

        :param git_api:
        :param configuration:
        :param aws_api:
        :return:
        """

        from horey.infrastructure_api.environment_api import EnvironmentAPI
        return EnvironmentAPI(configuration, aws_api, git_api=git_api)

    @staticmethod
    def get_frontend_api(configuration, environment_api):
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

    @staticmethod
    def get_ecs_api(configuration, environment_api):
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

    @staticmethod
    def get_alerts_api(configuration, environment_api):
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

    @staticmethod
    def get_email_api(configuration, environment_api):
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

    @staticmethod
    def get_aws_lambda_api(configuration, environment_api):
        """
        Get AWS Lambda API

        :param configuration:
        :param environment_api:
        :return:
        """

        from horey.infrastructure_api.aws_lambda_api import AWSLambdaAPI
        from horey.infrastructure_api.environment_api import EnvironmentAPI
        if not isinstance(environment_api, EnvironmentAPI):
            raise ValueError(f"{environment_api} not instance of EnvironmentAPI")

        return AWSLambdaAPI(configuration, environment_api)

    @staticmethod
    def get_cloudwatch_api(configuration, environment_api):
        """
        Get Cloudwatch API

        :param configuration:
        :param environment_api:
        :return:
        """

        from horey.infrastructure_api.cloudwatch_api import CloudwatchAPI
        from horey.infrastructure_api.environment_api import EnvironmentAPI
        if not isinstance(environment_api, EnvironmentAPI):
            raise ValueError(f"{environment_api} not instance of EnvironmentAPI")

        return CloudwatchAPI(configuration, environment_api)

    @staticmethod
    def get_aws_iam_api(configuration, environment_api):
        """
        Get AWS iam API

        :param configuration:
        :param environment_api:
        :return:
        """

        from horey.infrastructure_api.aws_iam_api import AWSIAMAPI
        from horey.infrastructure_api.environment_api import EnvironmentAPI
        if not isinstance(environment_api, EnvironmentAPI):
            raise ValueError(f"{environment_api} not instance of EnvironmentAPI")

        return AWSIAMAPI(configuration, environment_api)

    @staticmethod
    def get_loadbalancer_api(configuration, environment_api):
        """
        Get Cloudwatch API

        :param configuration:
        :param environment_api:
        :return:
        """

        from horey.infrastructure_api.loadbalancer_api import LoadbalancerAPI
        from horey.infrastructure_api.environment_api import EnvironmentAPI
        if not isinstance(environment_api, EnvironmentAPI):
            raise ValueError(f"{environment_api} not instance of EnvironmentAPI")

        return LoadbalancerAPI(configuration, environment_api)

    @staticmethod
    def get_dns_api(configuration, environment_api):
        """
        Get Cloudwatch API

        :param configuration:
        :param environment_api:
        :return:
        """

        from horey.infrastructure_api.dns_api import DNSAPI
        from horey.infrastructure_api.environment_api import EnvironmentAPI
        if not isinstance(environment_api, EnvironmentAPI):
            raise ValueError(f"{environment_api} not instance of EnvironmentAPI")

        return DNSAPI(configuration, environment_api)

    @staticmethod
    def get_db_api(configuration, environment_api):
        """
        Get Cloudwatch API

        :param configuration:
        :param environment_api:
        :return:
        """

        from horey.infrastructure_api.db_api import DBAPI
        from horey.infrastructure_api.environment_api import EnvironmentAPI
        if not isinstance(environment_api, EnvironmentAPI):
            raise ValueError(f"{environment_api} not instance of EnvironmentAPI")

        return DBAPI(configuration, environment_api)

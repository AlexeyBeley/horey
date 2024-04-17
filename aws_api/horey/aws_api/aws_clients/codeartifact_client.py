"""
AWS lambda client to handle lambda service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.h_logger import get_logger

logger = get_logger()


class CodeartifactClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "codeartifact"
        super().__init__(client_name)

    def create_domain(self, region, name, encryption_key):
        """
        Standard

        :param region:
        :param name:
        :param encryption_key:
        :return:
        """

        filters_req = {"domain": name, "encryptionKey": encryption_key}

        try:
            for _ in self.execute(
                    self.get_session_client(region=region).create_domain, "domain", filters_req=filters_req
            ):
                logger.info(f"Created codeartifact domain name: {name}")
        except Exception as exception_received:
            if "already exists" not in repr(exception_received):
                raise
            logger.info(
                f"Exception while creating domain name: {name}. Domain already exists"
            )

    def create_repository(self, region, domain_name, repository_name):
        """
        Standard.

        :param region:
        :param domain_name:
        :param repository_name:
        :return:
        """
        filters_req = {"domain": domain_name, "repository": repository_name}

        try:
            for _ in self.execute(
                    self.get_session_client(region=region).create_repository, "repository", filters_req=filters_req
            ):
                logger.info(f"Created codeartifact repository name: {repository_name}")
        except Exception as exception_received:
            if "already exists" not in repr(exception_received):
                raise
            logger.info(
                f"Exception while creating domain name: {repository_name}. Repository already exists"
            )

    def get_repository_endpoint(self, region, domain_name, repository_name, _format):
        """
        Standard.

        :param region:
        :param domain_name:
        :param repository_name:
        :param _format:
        :return:
        """
        filters_req = {"domain": domain_name, "repository": repository_name, "format": _format}

        for endpoint in self.execute(
                self.get_session_client(region=region).get_repository_endpoint,
                "repositoryEndpoint",
                filters_req=filters_req,
        ):
            return endpoint

"""
AWS lambda client to handle lambda service API requests.
"""
import pdb
from boto3_client import Boto3Client
from h_logger import get_logger

logger = get_logger()


class CodeartifactClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "codeartifact"
        super().__init__(client_name)

    def create_domain(self, name, encryption_key):
        filters_req = dict()
        filters_req["domain"] = name
        filters_req["encryptionKey"] = encryption_key

        try:
            for _ in self.execute(self.client.create_domain, "domain", filters_req=filters_req):
                logger.info(f"Created codeartifact domain name: {name}")
        except Exception as exception_received:
            if "already exists" not in repr(exception_received):
                raise
            logger.info(f"Exception while creating domain name: {name}. Domain already exists")

    def create_repository(self, domain_name, repository_name):
        filters_req = dict()
        filters_req["domain"] = domain_name
        filters_req["repository"] = repository_name

        try:
            for _ in self.execute(self.client.create_repository, "repository", filters_req=filters_req):
                logger.info(f"Created codeartifact repository name: {repository_name}")
        except Exception as exception_received:
            if "already exists" not in repr(exception_received):
                raise
            logger.info(f"Exception while creating domain name: {repository_name}. Repository already exists")

    def get_repository_endpoint(self, domain_name, repository_name, format):
        filters_req = dict()
        filters_req["domain"] = domain_name
        filters_req["repository"] = repository_name
        filters_req["format"] = format

        for endpoint in self.execute(self.client.get_repository_endpoint, "repositoryEndpoint", filters_req=filters_req):
            pdb.set_trace()
            return endpoint

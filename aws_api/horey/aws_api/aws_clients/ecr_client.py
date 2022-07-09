"""
AWS lambda client to handle lambda service API requests.
"""
import pdb
from base64 import b64decode
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.ecr_repository import ECRRepository
from horey.aws_api.aws_services_entities.ecr_image import ECRImage
from horey.h_logger import get_logger

logger = get_logger()


class ECRClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    NEXT_PAGE_REQUEST_KEY = "nextToken"
    NEXT_PAGE_RESPONSE_KEY = "nextToken"

    def __init__(self):
        client_name = "ecr"
        super().__init__(client_name)

    def get_authorization_info(self, region=None):
        current_account = AWSAccount.get_aws_account()

        if region is not None:
            AWSAccount.set_aws_region(region)
        filters_req = {"registryIds": [current_account.id]} if current_account is not None else None
        lst_ret = list(self.execute(self.client.get_authorization_token, "authorizationData", filters_req=filters_req))
        for dict_src in lst_ret:
            auth_user_token = b64decode(dict_src['authorizationToken']).decode()
            user_name, decoded_token = auth_user_token.split(":")
            dict_src["user_name"] = user_name
            dict_src["decoded_token"] = decoded_token
            dict_src["proxy_host"] = dict_src["proxyEndpoint"][len("https://"):]
        return lst_ret

    def provision_repository(self, repository):
        AWSAccount.set_aws_region(repository.region)

        region_repos = self.get_region_repositories(repository.region, repository_names=[repository.name])
        if len(region_repos) == 1:
            return repository.update_from_raw_create(region_repos[0].dict_src)

        dict_ret = self.provision_repository_raw(repository.generate_create_request())
        return repository.update_from_raw_create(dict_ret)

    def provision_repository_raw(self, request_dict):
        for response in self.execute(self.client.create_repository, "repository", filters_req=request_dict):
            return response

    def get_all_images(self, repository):
        """
        Get all images in all regions.
        :return:
        """
        final_result = list()
        AWSAccount.set_aws_region(repository.region)
        filters_req = {"repositoryName": repository.name, "filter": {"tagStatus": "ANY"}}
        for dict_src in self.execute(self.client.describe_images, "imageDetails", filters_req=filters_req):
            obj = ECRImage(dict_src)
            final_result.append(obj)

        return final_result
    
    def get_all_repositories(self, region=None):
        """
        Get all repositories in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_repositories(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_repositories(region)

        return final_result

    def get_region_repositories(self, region, repository_names=None):
        logger.info(f"Getting all repositories in region {str(region)}")
        filters_req = dict()
        if repository_names is not None:
            filters_req["repositoryNames"] = repository_names

        final_result = list()
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.describe_repositories, "repositories", filters_req=filters_req,
                                     exception_ignore_callback=lambda error: "RepositoryNotFoundException" in repr(error)):
            obj = ECRRepository(dict_src)
            final_result.append(obj)

        return final_result

    def dispose_repository(self, repository: ECRRepository):
        AWSAccount.set_aws_region(repository.region)

        dict_ret = self.dispose_repository_raw(repository.generate_dispose_request())
        return repository.update_from_raw_create(dict_ret)

    def dispose_repository_raw(self, request_dict):
        for response in self.execute(self.client.delete_repository, "repository", filters_req=request_dict):
            return response

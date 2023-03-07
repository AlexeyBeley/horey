"""
AWS lambda client to handle lambda service API requests.
"""

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
        """
        Get authorization info to be used by docker client to connect the repo.

        @param region:
        @return:
        """

        if region is not None:
            AWSAccount.set_aws_region(region)

        filters_req = {"registryIds": [self.account_id]}
        lst_ret = list(
            self.execute(
                self.client.get_authorization_token,
                "authorizationData",
                filters_req=filters_req,
            )
        )
        for dict_src in lst_ret:
            auth_user_token = b64decode(dict_src["authorizationToken"]).decode()
            user_name, decoded_token = auth_user_token.split(":")
            dict_src["user_name"] = user_name
            dict_src["decoded_token"] = decoded_token
            dict_src["proxy_host"] = dict_src["proxyEndpoint"][len("https://") :]
        return lst_ret

    def provision_repository(self, repository):
        """
        Provision ECR repo.

        @param repository:
        @return:
        """

        AWSAccount.set_aws_region(repository.region)

        region_repos = self.get_region_repositories(
            repository.region, repository_names=[repository.name], get_tags=False)
        if len(region_repos) == 1:
            repository.update_from_raw_create(region_repos[0].dict_src)
        else:
            dict_ret = self.provision_repository_raw(repository.generate_create_request())
            repository.update_from_raw_create(dict_ret)

        self.tag_resource(repository, arn_identifier="resourceArn", tags_identifier="tags")

    def provision_repository_raw(self, request_dict):
        """
        Provision ECR repo from dict request.

        @param request_dict:
        @return:
        """

        for response in self.execute(
            self.client.create_repository, "repository", filters_req=request_dict
        ):
            return response

    def get_all_images(self, repository):
        """
        Get all images in all regions.

        :return:
        """

        final_result = []
        AWSAccount.set_aws_region(repository.region)
        filters_req = {
            "repositoryName": repository.name,
            "filter": {"tagStatus": "ANY"},
        }
        for dict_src in self.execute(
            self.client.describe_images, "imageDetails", filters_req=filters_req
        ):
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

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_repositories(_region)

        return final_result

    def get_region_repositories(self, region, repository_names=None, get_tags=True):
        """
        Get region ECR repos.

        @param region:
        @param repository_names:
        @param get_tags:
        @return:
        """

        logger.info(f"Getting all repositories in region {str(region)}")
        filters_req = {}
        if repository_names is not None:
            filters_req["repositoryNames"] = repository_names

        final_result = []
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(
            self.client.describe_repositories,
            "repositories",
            filters_req=filters_req,
            exception_ignore_callback=lambda error: "RepositoryNotFoundException"
            in repr(error),
        ):
            obj = ECRRepository(dict_src)
            final_result.append(obj)
            if get_tags:
                obj.tags = self.get_tags(obj, function=self.client.list_tags_for_resource, arn_identifier="resourceArn", tags_identifier="tags")

        return final_result

    def dispose_repository(self, repository: ECRRepository):
        """
        Self explanatory

        @param repository:
        @return:
        """

        AWSAccount.set_aws_region(repository.region)

        dict_ret = self.dispose_repository_raw(repository.generate_dispose_request())
        return repository.update_from_raw_create(dict_ret)

    def dispose_repository_raw(self, request_dict):
        """
        Self explanatory

        @param request_dict:
        @return:
        """

        for response in self.execute(
            self.client.delete_repository, "repository", filters_req=request_dict
        ):
            return response

    def tag_image(self, image, new_tags):
        """
        Tag the image

        @param image:
        @return:
        """

        for response in self.execute(
            self.client.describe_images,
            "imageDetails",
            filters_req={
                "repositoryName": image.repository_name,
                "imageIds": [{"imageTag": image.image_tags[0]}],
            },
        ):

            if all(tag in response["imageTags"] for tag in new_tags):
                return

        images = None
        for response in self.execute(
            self.client.batch_get_image,
            None,
            raw_data=True,
            filters_req={
                "repositoryName": image.repository_name,
                "imageIds": [{"imageTag": image.image_tags[0]}],
            },
        ):
            images = response["images"]
            if response.get("failures"):
                raise RuntimeError(response.get("failures"))

        if len(images) != 1:
            raise RuntimeError(f"len(images) != 1: {len(images)}")

        image_manifest = images[0]["imageManifest"]
        for image_new_tag in new_tags:
            for response in self.execute(
                self.client.put_image,
                "image",
                filters_req={
                    "repositoryName": image.repository_name,
                    "imageManifest": image_manifest,
                    "imageTag": image_new_tag,
                },
            ):
                assert response

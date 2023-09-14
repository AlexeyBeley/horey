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

    # pylint: disable= too-many-arguments
    def yield_images(self, region=None, update_info=False, filters_req=None):
        """
        Yield images

        :return:
        """


        regional_fetcher_generator = self.yield_images_raw
        for obj in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  ECRImage,
                                                  update_info=update_info,
                                                  regions=[region] if region else None,
                                                  filters_req=filters_req):
            yield obj

    def yield_images_raw(self, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        if filters_req is None:
            for repository in self.yield_repositories(region=AWSAccount.get_aws_region()):
                _filters_req = {
                    "repositoryName": repository.name,
                    "filter": {"tagStatus": "ANY"},
                }
                for dict_src in self.execute(
                        self.client.describe_images, "imageDetails",
                        filters_req=_filters_req,
                        exception_ignore_callback=lambda error: "RepositoryNotFoundException"
                                                                in repr(error)
                ):
                    yield dict_src
            return

        for dict_src in self.execute(
                self.client.describe_images, "imageDetails",
                filters_req=filters_req,
                exception_ignore_callback=lambda error: "RepositoryNotFoundException"
            in repr(error)
        ):
            yield dict_src

    def get_all_images(self, region=None, filters_req=None):
        """
        Get all images in all regions.

        :return:
        """

        return list(self.yield_images(region=region, filters_req=filters_req))


    # pylint: disable= too-many-arguments
    def yield_repositories(self, region=None, update_info=False, filters_req=None, get_tags=True):
        """
        Yield repositories

        :return:
        """

        get_tags_callback = None if not get_tags else \
            lambda _obj: self.get_tags(_obj, function=self.client.list_tags_for_resource,
                                                                                 arn_identifier="resourceArn",
                                                                                 tags_identifier="tags")

        regional_fetcher_generator = self.yield_repositories_raw
        for obj in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  ECRRepository,
                                                  update_info=update_info,
                                                  get_tags_callback= get_tags_callback,
                                                  regions=[region] if region else None,
                                                  filters_req=filters_req):
            yield obj

    def yield_repositories_raw(self, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.client.describe_repositories, "repositories",
                filters_req=filters_req,
                exception_ignore_callback=lambda error: "RepositoryNotFoundException"
            in repr(error)
        ):
            yield dict_src

    def get_all_repositories(self, region=None):
        """
        Get all repositories in all regions.
        :return:
        """

        return list(self.yield_repositories(region=region))

    def get_region_repositories(self, region, repository_names=None, get_tags=True):
        """
        Get region ECR repos.

        @param region:
        @param repository_names:
        @param get_tags:
        @return:
        """

        logger.info(f"Getting all repositories in region {str(region)}")
        filters_req = None
        if repository_names is not None:
            filters_req = {"repositoryNames": repository_names}

        return list(self.yield_repositories(region=region, get_tags=get_tags, filters_req=filters_req))

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

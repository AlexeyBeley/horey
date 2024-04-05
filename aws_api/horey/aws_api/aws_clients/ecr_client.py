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
                self.get_session_client(region=region).get_authorization_token,
                "authorizationData",
                filters_req=filters_req,
            )
        )
        for dict_src in lst_ret:
            auth_user_token = b64decode(dict_src["authorizationToken"]).decode()
            user_name, decoded_token = auth_user_token.split(":")
            dict_src["user_name"] = user_name
            dict_src["decoded_token"] = decoded_token
            dict_src["proxy_host"] = dict_src["proxyEndpoint"][len("https://"):]
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
            dict_ret = self.provision_repository_raw(repository.region, repository.generate_create_request())
            repository.update_from_raw_create(dict_ret)

        self.tag_resource(repository, arn_identifier="resourceArn", tags_identifier="tags")

    def provision_repository_raw(self, region, request_dict):
        """
        Provision ECR repo from dict request.

        @param request_dict:
        @return:
        """

        for response in self.execute(
                self.get_session_client(region=region).create_repository, "repository", filters_req=request_dict
        ):
            return response

    # pylint: disable= too-many-arguments
    def yield_images(self, region=None, update_info=False, filters_req=None):
        """
        Yield images

        :return:
        """

        regional_fetcher_generator = self.yield_images_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            ECRImage,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_images_raw(self, region, filters_req=None):
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
                yield from self.execute(
                        self.get_session_client(region=region).describe_images, "imageDetails",
                        filters_req=_filters_req,
                        exception_ignore_callback=lambda error: "RepositoryNotFoundException"
                                                                in repr(error)
                )
            return

        yield from self.execute(
                self.get_session_client(region=region).describe_images, "imageDetails",
                filters_req=filters_req,
                exception_ignore_callback=lambda error: "RepositoryNotFoundException"
                                                        in repr(error)
        )

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
            lambda _obj: self.get_tags(_obj, function=self.get_session_client(region=region).list_tags_for_resource,
                                       arn_identifier="resourceArn",
                                       tags_identifier="tags")

        regional_fetcher_generator = self.yield_repositories_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            ECRRepository,
                                                            update_info=update_info,
                                                            get_tags_callback=get_tags_callback,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_repositories_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
                self.get_session_client(region=region).describe_repositories, "repositories",
                filters_req=filters_req,
                exception_ignore_callback=lambda error: "RepositoryNotFoundException"
                                                        in repr(error)
        )

    def get_repository_images(self, repository):
        """
        Get images of a repo.

        :return:
        """

        final_result = []
        AWSAccount.set_aws_region(repository.region)
        filters_req = {
            "repositoryName": repository.name,
            "filter": {"tagStatus": "ANY"},
        }
        for dict_src in self.execute(
                self.get_session_client(region=repository.region).describe_images, "imageDetails",
                filters_req=filters_req
        ):
            obj = ECRImage(dict_src)
            final_result.append(obj)

        return final_result

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
        Standard.

        @param repository:
        @return:
        """

        dict_ret = self.dispose_repository_raw(repository.region, repository.generate_dispose_request())
        if dict_ret:
            repository.update_from_raw_create(dict_ret)
        return True

    def dispose_repository_raw(self, region, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """

        for response in self.execute(
                self.get_session_client(region=region).delete_repository, "repository", filters_req=request_dict,
                exception_ignore_callback=lambda error: "RepositoryNotFoundException" in repr(error)

        ):
            return response

    def tag_image(self, image, new_tags):
        """
        Tag the image

        @param image:
        @return:
        """

        for response in self.execute(
                self.get_session_client(region=image.region).describe_images,
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
                self.get_session_client(region=image.region).batch_get_image,
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
                    self.get_session_client(region=image.region).put_image,
                    "image",
                    filters_req={
                        "repositoryName": image.repository_name,
                        "imageManifest": image_manifest,
                        "imageTag": image_new_tag,
                    },
            ):
                assert response

    def dispose_images(self, images):
        """
        Dispose the images.

        :param images:
        :return:
        """

        if not images:
            return None

        repository_names = {image.repository_name for image in images}

        if len(repository_names) > 1:
            raise NotImplementedError(repository_names)

        request_dict = {"repositoryName": images[0].repository_name,
                        "imageIds": [{"imageDigest": image.image_digest} for image in images]}
        return self.batch_delete_image_raw(images[0].region, request_dict)

    def batch_delete_image_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Deleting images: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).batch_delete_image, None, raw_data=True, filters_req=request_dict
        ):
            if response.get("failures"):
                raise ValueError(response)
            self.clear_cache(ECRImage)
            return response

"""
AWS client to handle service API requests.
"""

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.efs_file_system import EFSFileSystem
from horey.h_logger import get_logger

logger = get_logger()


class EFSClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    NEXT_PAGE_REQUEST_KEY = "Marker"
    NEXT_PAGE_RESPONSE_KEY = "NextMarker"

    def __init__(self):
        client_name = "efs"
        super().__init__(client_name)

    def provision_file_system(self, file_system: EFSFileSystem):
        """
        Standard

        @param file_system:
        @return:
        """
        raise NotImplementedError()
        repo_region = ECRfile_system({})
        repo_region.region = file_system.region
        repo_region.name = file_system.name
        if not self.update_file_system_information(repo_region, full_information=True):
            dict_ret = self.provision_file_system_raw(file_system.region, file_system.generate_create_request())
            file_system.update_from_raw_response(dict_ret)
        else:
            file_system.arn = repo_region.arn

        create_request, delete_request = repo_region.generate_change_file_system_policy_requests(file_system)
        if create_request:
            self.set_file_system_policy_raw(file_system.region, create_request)
        if delete_request:
            self.delete_file_system_policy_raw(file_system.region, delete_request)

        if file_system.tags != repo_region.tags:
            self.clear_cache(ECRfile_system)
            self.tag_resource(file_system, arn_identifier="resourceArn", tags_identifier="tags")

        self.update_file_system_information(file_system)
        return file_system

    def update_file_system_information(self, file_system: EFSFileSystem, full_information=True):
        """
        Update repo info.

        :param file_system:
        :return:
        """
        breakpoint()
        all_repos = list(self.yield_file_systems(region=file_system.region, filters_req={"file_systemNames": [file_system.name]}, full_information=full_information))
        if not all_repos:
            return False

        if len(all_repos) > 1:
            raise RuntimeError(f"{len(all_repos)=} for repo name {file_system.name=} ")

        for attr, value in all_repos[0].__dict__.items():
            setattr(file_system, attr, value)
        return True

    def provision_file_system_raw(self, region, request_dict):
        """
        Standard.

        @param request_dict:
        @return:
        :param region:
        """
        breakpoint()
        for response in self.execute(
                self.get_session_client(region=region).create_file_system, "file_system", filters_req=request_dict
        ):
            self.clear_cache(ECRfile_system)
            return response

    # pylint: disable= too-many-arguments
    def yield_file_systems(self, region=None, update_info=False, filters_req=None):
        """
        Yield images

        :return:
        """
        breakpoint()
        regional_fetcher_generator = self.yield_images_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            ECRImage,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_file_systems_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """
        breakpoint()
        if filters_req is None:
            for file_system in self.yield_file_systems(region=region):
                _filters_req = {
                    "file_systemName": file_system.name,
                    "filter": {"tagStatus": "ANY"},
                }
                yield from self.execute(
                        self.get_session_client(region=region).describe_images, "imageDetails",
                        filters_req=_filters_req,
                        exception_ignore_callback=lambda error: "file_systemNotFoundException"
                                                                in repr(error)
                )
            return

        yield from self.execute(
                self.get_session_client(region=region).describe_images, "imageDetails",
                filters_req=filters_req,
                exception_ignore_callback=lambda error: "file_systemNotFoundException"
                                                        in repr(error)
        )

    def get_all_file_systems(self, region=None, filters_req=None):
        """
        Get all images in all regions.

        :return:
        """
        breakpoint()
        return list(self.yield_images(region=region, filters_req=filters_req))

    def dispose_file_system(self, file_system: EFSFileSystem):
        """
        Standard.

        @param file_system:
        @return:
        """
        breakpoint()
        dict_ret = self.dispose_file_system_raw(file_system.region, file_system.generate_dispose_request())
        if dict_ret:
            file_system.update_from_raw_response(dict_ret)
        return True

    def dispose_file_system_raw(self, region, request_dict):
        """
        Standard.

        @param request_dict:
        @return:
        :param region:
        """

        breakpoint()
        for response in self.execute(
                self.get_session_client(region=region).create_file_system, "file_system", filters_req=request_dict
        ):
            self.clear_cache(EFSFileSystem)
            return response
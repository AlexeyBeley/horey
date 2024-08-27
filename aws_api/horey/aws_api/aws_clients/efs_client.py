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
        logger.info("Provisioning file system: " + file_system.get_tag("Name", casesensitive=True))
        current_file_system = EFSFileSystem({})
        current_file_system.region = file_system.region
        current_file_system.tags = file_system.tags
        if not self.update_file_system_information(current_file_system):
            response = self.provision_file_system_raw(file_system.region, file_system.generate_create_request())
            del response["ResponseMetadata"]
            file_system.update_from_raw_response(response)
            self.wait_for_status(file_system, self.update_file_system_information,
                                 [file_system.State.AVAILABLE],
                                 [file_system.State.CREATING,
                                  file_system.State.UPDATING],
                                 [file_system.State.ERROR,
                                  file_system.State.DELETED,
                                  file_system.State.DELETING])
            return True

        file_system.id = current_file_system.id
        request = current_file_system.generate_update_request(file_system)
        if request:
            response = self.update_file_system_raw(file_system.region, request)
            del response["ResponseMetadata"]
            file_system.update_from_raw_response(response)

            self.wait_for_status(file_system, self.update_file_system_information,
                             [file_system.State.AVAILABLE],
                             [file_system.State.UPDATING],
                             [file_system.State.ERROR,
                              file_system.State.DELETED,
                              file_system.State.DELETING,
                              file_system.State.CREATING])
            return True

        return self.update_file_system_information(file_system)

    def update_file_system_information(self, file_system: EFSFileSystem, update_info=True):
        """
        Update repo info.

        :param update_info:
        :param file_system:
        :return:
        """

        file_system_tagname = file_system.get_tagname()

        lst_ret = []
        for region_file_system in self.yield_file_systems(region=file_system.region, update_info=update_info):
            if region_file_system.get_tagname() == file_system_tagname:
                lst_ret.append(region_file_system)

        if len(lst_ret) > 1:
            raise RuntimeError(f"Found {len(lst_ret)} file systems with tag {file_system.get_tagname()} in region {file_system.region.region_mark}")

        if not lst_ret:
            file_system.life_cycle_state = file_system.State.DELETED.value
            return False

        return file_system.update_from_raw_response(lst_ret[0].dict_src)

    def provision_file_system_raw(self, region, request_dict):
        """
        Standard

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Creating efs file system: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).create_file_system, None, raw_data=True, filters_req=request_dict
        ):
            self.clear_cache(EFSFileSystem)
            return response

    def update_file_system_raw(self, region, request_dict):
        """
        Standard

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Updating efs file system: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).update_file_system, None, raw_data=True, filters_req=request_dict
        ):
            self.clear_cache(EFSFileSystem)
            return response

    def yield_file_systems(self, region=None, update_info=False, filters_req=None):
        """
        Yield objects

        :return:
        """

        regional_fetcher_generator = self.yield_file_systems_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            EFSFileSystem,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_file_systems_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
            self.get_session_client(region=region).describe_file_systems, "FileSystems",
            filters_req=filters_req
        )

    def dispose_file_system(self, file_system: EFSFileSystem):
        """
        Standard.

        @param file_system:
        @return:
        """

        current_file_system = EFSFileSystem({})
        current_file_system.region = file_system.region
        current_file_system.tags = file_system.tags

        if not self.update_file_system_information(current_file_system):
            file_system.life_cycle_state = file_system.State.DELETED.value
            return True

        self.dispose_file_system_raw(file_system.region, current_file_system.generate_dispose_request())
        self.wait_for_status(current_file_system, self.update_file_system_information,
                             [file_system.State.DELETED],
                             [file_system.State.DELETING,
                              file_system.State.AVAILABLE],
                             [file_system.State.ERROR,
                             file_system.State.CREATING,
                              file_system.State.UPDATING], timeout=600)

        self.clear_cache(EFSFileSystem)
        file_system.life_cycle_state = file_system.State.DELETED.value
        return True

    def dispose_file_system_raw(self, region, request_dict):
        """
        Standard.

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Deleting efs file system: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).delete_file_system, None, raw_data=True, filters_req=request_dict
        ):
            self.clear_cache(EFSFileSystem)
            return response

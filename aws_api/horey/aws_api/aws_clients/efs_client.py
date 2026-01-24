"""
AWS client to handle service API requests.
"""
import copy

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.efs_file_system import EFSFileSystem
from horey.aws_api.aws_services_entities.efs_access_point import EFSAccessPoint
from horey.aws_api.aws_services_entities.efs_mount_target import EFSMountTarget
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
            raise RuntimeError(
                f"Found {len(lst_ret)} file systems with tag {file_system.get_tagname()} in region {file_system.region.region_mark}")

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

    def provision_access_point_raw(self, region, request_dict):
        """
        Standard

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Creating efs access point: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).create_access_point, None, raw_data=True,
                filters_req=request_dict
        ):
            self.clear_cache(EFSAccessPoint)
            return response

    def dispose_access_point_raw(self, region, request_dict):
        """
        Standard.

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Deleting efs access point: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).delete_access_point, None, raw_data=True,
                filters_req=request_dict
        ):
            self.clear_cache(EFSAccessPoint)
            return response

    def dispose_access_point(self, access_point: EFSFileSystem):
        """
        Standard.

        @param access_point:
        @return:
        """

        current_access_point = EFSAccessPoint({})
        current_access_point.region = access_point.region
        current_access_point.tags = access_point.tags

        if not self.update_access_point_information(current_access_point):
            access_point.life_cycle_state = access_point.State.DELETED.value
            return True

        self.dispose_access_point_raw(access_point.region, current_access_point.generate_dispose_request())
        self.wait_for_status(current_access_point, self.update_access_point_information,
                             [access_point.State.DELETED],
                             [access_point.State.DELETING,
                              access_point.State.AVAILABLE],
                             [access_point.State.ERROR,
                              access_point.State.CREATING,
                              access_point.State.UPDATING], timeout=600)

        self.clear_cache(EFSFileSystem)
        access_point.life_cycle_state = access_point.State.DELETED.value
        return True

    def yield_access_points(self, region=None, update_info=False, filters_req=None):
        """
        Yield objects

        :return:
        """

        regional_fetcher_generator = self.yield_access_points_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            EFSAccessPoint,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_access_points_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
            self.get_session_client(region=region).describe_access_points, "AccessPoints",
            filters_req=filters_req
        )

    def provision_access_point(self, access_point: EFSAccessPoint):
        """
        Standard

        @param access_point:
        @return:
        """

        logger.info("Provisioning access point: " + access_point.get_tag("Name", casesensitive=True))
        current_access_point = EFSAccessPoint({})
        current_access_point.region = access_point.region
        current_access_point.tags = access_point.tags

        if not self.update_access_point_information(current_access_point):
            response = self.provision_access_point_raw(access_point.region, access_point.generate_create_request())
            del response["ResponseMetadata"]
            access_point.update_from_raw_response(response)
            self.wait_for_status(access_point, self.update_access_point_information,
                                 [access_point.State.AVAILABLE],
                                 [access_point.State.CREATING,
                                  access_point.State.UPDATING],
                                 [access_point.State.ERROR,
                                  access_point.State.DELETED,
                                  access_point.State.DELETING])
        else:
            access_point.update_from_attrs(current_access_point)

        return True

    def update_access_point_information(self, access_point: EFSAccessPoint, update_info=True):
        """
        Update object info from aws api.

        :param update_info:
        :param access_point:
        :return:
        """

        access_point_tagname = access_point.get_tagname()

        lst_ret = []
        for region_access_point in self.yield_access_points(region=access_point.region, update_info=update_info):
            if region_access_point.get_tagname() == access_point_tagname:
                lst_ret.append(region_access_point)

        if len(lst_ret) > 1:
            raise RuntimeError(
                f"Found {len(lst_ret)} access points with tag {access_point.get_tagname()} in region {access_point.region.region_mark}")

        if not lst_ret:
            access_point.life_cycle_state = access_point.State.DELETED.value
            return False

        return access_point.update_from_raw_response(lst_ret[0].dict_src)

    def yield_mount_targets(self, region=None, update_info=False, filters_req=None, full_information=True):
        """
        Yield objects

        :return:
        """

        if filters_req is None:
            filters_req = {}
        if "FileSystemId" in filters_req or "MountTargetId" in filters_req or "AccessPointId" in filters_req:
            filters = [filters_req]
        else:
            filters = []
            for file_system in self.yield_file_systems(region=region):
                _filters_req = copy.deepcopy(filters_req)
                _filters_req["FileSystemId"] = file_system.id
                filters.append(_filters_req)

        regional_fetcher_generator = self.yield_mount_targets_raw
        for _filters_req in filters:
            for mount_target in self.regional_service_entities_generator(regional_fetcher_generator,
                                                                EFSMountTarget,
                                                                update_info=update_info,
                                                                regions=[region] if region else None,
                                                                filters_req=_filters_req):
                if full_information:
                    for response in self.execute(
                        self.get_session_client(region=region).describe_mount_target_security_groups, None, raw_data=True,
                        filters_req={"MountTargetId": mount_target.id}
                    ):
                        del response["ResponseMetadata"]
                        if not mount_target.update_from_raw_response(response):
                            raise RuntimeError(f"Was not able to update {mount_target.id} with {response=}")

                yield mount_target

    def yield_mount_targets_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
            self.get_session_client(region=region).describe_mount_targets, "MountTargets",
            filters_req=filters_req
        )

    def provision_mount_target_raw(self, region, request_dict):
        """
        Standard

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Creating efs mount target: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).create_mount_target, None, raw_data=True, filters_req=request_dict
        ):
            self.clear_cache(EFSMountTarget)
            return response

    def dispose_mount_target_raw(self, region, request_dict):
        """
        Standard

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Deleting efs mount target: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).delete_mount_target, None, raw_data=True, filters_req=request_dict
        ):
            self.clear_cache(EFSMountTarget)
            return response

    def update_mount_target_information(self, mount_target: EFSMountTarget, update_info=True):
        """
        Update repo info.

        :param update_info:
        :param mount_target:
        :return:
        """

        lst_ret = []
        if not mount_target.file_system_id:
            raise ValueError("mount_target.file_system_id was not set")
        if not mount_target.subnet_id:
            raise ValueError("mount_target.subnet_id was not set")
        if not mount_target.region:
            raise ValueError("mount_target.region was not set")

        filters_req = {"FileSystemId": mount_target.file_system_id}
        for region_mount_target in self.yield_mount_targets(region=mount_target.region, update_info=update_info,
                                                            filters_req=filters_req):
            if region_mount_target.subnet_id != mount_target.subnet_id:
                continue
            lst_ret.append(region_mount_target)

        if len(lst_ret) > 1:
            raise RuntimeError(
                f"Found {len(lst_ret)} mount targets with tag {mount_target.file_system_id=} and {mount_target.subnet_id=}"
                f" in region {mount_target.region.region_mark}")

        if not lst_ret:
            mount_target.life_cycle_state = mount_target.State.DELETED.value
            return False

        return mount_target.update_from_attrs(lst_ret[0])

    def provision_mount_target(self, mount_target: EFSMountTarget):
        """
        Standard

        @param mount_target:
        @return:
        """

        logger.info("Provisioning mount target")
        current_mount_target = EFSMountTarget({})
        current_mount_target.region = mount_target.region
        current_mount_target.file_system_id = mount_target.file_system_id
        current_mount_target.subnet_id = mount_target.subnet_id

        if not self.update_mount_target_information(current_mount_target):
            response = self.provision_mount_target_raw(mount_target.region, mount_target.generate_create_request())
            del response["ResponseMetadata"]
            mount_target.update_from_raw_response(response)
            self.wait_for_status(mount_target, self.update_mount_target_information,
                                 [mount_target.State.AVAILABLE],
                                 [mount_target.State.CREATING,
                                  mount_target.State.UPDATING],
                                 [mount_target.State.ERROR,
                                  mount_target.State.DELETED,
                                  mount_target.State.DELETING])
            return True

        mount_target.id = current_mount_target.id
        request = current_mount_target.generate_modify_mount_target_security_groups_request(mount_target)
        if request:
            response = self.modify_mount_target_security_groups_raw(mount_target.region, request)
            del response["ResponseMetadata"]
            mount_target.update_from_raw_response(response)

            self.wait_for_status(mount_target, self.update_mount_target_information,
                                 [mount_target.State.AVAILABLE],
                                 [mount_target.State.UPDATING],
                                 [mount_target.State.ERROR,
                                  mount_target.State.DELETED,
                                  mount_target.State.DELETING,
                                  mount_target.State.CREATING])
            return True

        return self.update_mount_target_information(mount_target)

    def modify_mount_target_security_groups_raw(self, region, request_dict):
        """
        Standard

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Updating efs mount target security groups: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).modify_mount_target_security_groups, None, raw_data=True, filters_req=request_dict
        ):
            self.clear_cache(EFSMountTarget)
            return response

"""
AWS route-53 client to handle route-53 service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.route53_hosted_zone import HostedZone
from horey.h_logger import get_logger

logger = get_logger()


class Route53Client(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "route53"
        super().__init__(client_name)

    # pylint: disable= too-many-arguments
    def yield_hosted_zones(self, update_info=False, filters_req=None, full_information=True):
        """
        Yield hosted_zones

        :return:
        """

        regional_fetcher_generator = self.yield_hosted_zones_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                               HostedZone,
                                                               update_info=update_info,
                                                               full_information_callback=self.get_hosted_zone_full_information if full_information else None,
                                                               global_service=True,
                                                               filters_req=filters_req)

    def yield_hosted_zones_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
                self.get_session_client(region=region).list_hosted_zones, "HostedZones", filters_req=filters_req
        )

    def get_all_hosted_zones(self, full_information=True, name=None):
        """
        Get all hosted zones

        :param name:
        :param full_information:
        :return:
        """

        hosted_zones = list(self.yield_hosted_zones(full_information=False))
        if name is not None:
            if not name.endswith("."):
                name += "."
            hosted_zones = [hz for hz in hosted_zones if hz.name == name]

        if full_information:
            for hosted_zone in hosted_zones:
                self.get_hosted_zone_full_information(hosted_zone)

        return hosted_zones

    def get_hosted_zone_full_information(self, hosted_zone: HostedZone):
        """
        Standard.

        :param hosted_zone:
        :return:
        """
        hosted_zone.records = []
        for update_info in self.execute(
                self.get_session_client().list_resource_record_sets,
                "ResourceRecordSets",
                filters_req={"HostedZoneId": hosted_zone.id},
        ):
            hosted_zone.update_record_set(update_info)

        for response in self.execute(
                self.get_session_client().get_hosted_zone,
                None,
                raw_data=True,
                filters_req={"Id": hosted_zone.id},
        ):
            response.update(response["HostedZone"])
            del response["ResponseMetadata"]
            del response["HostedZone"]
            hosted_zone.update_from_raw_response(response)

        for response in self.execute(
                self.get_session_client().list_tags_for_resource,
                "ResourceTagSet",
                filters_req={"ResourceType": "hostedzone",
                             "ResourceId": hosted_zone.id.replace("/hostedzone/", "")},
        ):
            del response["ResourceType"]
            del response["ResourceId"]
            hosted_zone.update_from_raw_response(response)

    def provision_hosted_zone(self, hosted_zone, declarative=False):
        """
        Standard.

        :param declarative:
        :param hosted_zone:
        :return:
        """

        current_hosted_zone = HostedZone({})
        current_hosted_zone.name = hosted_zone.name
        current_hosted_zone.id = hosted_zone.id
        if not self.update_hosted_zone_information(current_hosted_zone, full_information=True):
            if not hosted_zone.tags:
                raise ValueError(f"Provisioning hosted zone without tags is not supported: {hosted_zone.generate_create_request()}")
            request = hosted_zone.generate_create_request()
            response = self.raw_create_hosted_zone(request)
            hosted_zone.id = response["Id"]
            self.associate_hosted_zone(hosted_zone)
            current_hosted_zone = HostedZone({"tags": [], "id": hosted_zone.id})

            change_tags_request = current_hosted_zone.generate_change_tags_request(hosted_zone)
            if change_tags_request:
                self.change_tags_for_resource_raw(change_tags_request)
            self.get_hosted_zone_full_information(hosted_zone)
            self.clear_cache(HostedZone)
            return hosted_zone

        hosted_zone.id = current_hosted_zone.id
        self.change_resource_record_sets(hosted_zone, current_hosted_zone=current_hosted_zone)

        associate_requests, disassociate_requests = current_hosted_zone.generate_association_requests(hosted_zone,
                                                                                                      declarative=declarative)

        if associate_requests:
            self.associate_vpc_with_hosted_zone_raw(associate_requests)

        if disassociate_requests:
            self.disassociate_vpc_from_hosted_zone_raw(disassociate_requests)

        change_tags_request = current_hosted_zone.generate_change_tags_request(hosted_zone)
        if change_tags_request:
            self.change_tags_for_resource_raw(change_tags_request)

        self.get_hosted_zone_full_information(hosted_zone)
        return hosted_zone

    def upsert_resource_record_sets(self, desired_hosted_zone, current_hosted_zone=None):
        """
        Change only records. UPSERT only!

        :param desired_hosted_zone:
        :param current_hosted_zone:
        :return:
        """

        if current_hosted_zone is None:
            current_hosted_zone = HostedZone({})
            current_hosted_zone.name = desired_hosted_zone.name
            current_hosted_zone.id = desired_hosted_zone.id
            if not self.update_hosted_zone_information(current_hosted_zone, full_information=True):
                raise ValueError(f"Could not find the hosted zone {desired_hosted_zone.name}, use provision instead")
            desired_hosted_zone.id = current_hosted_zone.id

        request = current_hosted_zone.generate_upsert_resource_record_sets_request(desired_hosted_zone)
        if request:
            self.change_resource_record_sets_raw(request)

    def change_resource_record_sets(self, desired_hosted_zone, current_hosted_zone=None):
        """
        Change only records. UPSERT only! Todo: make delete possible.

        :param desired_hosted_zone:
        :param current_hosted_zone:
        :return:
        """

        if current_hosted_zone is None:
            current_hosted_zone = HostedZone({})
            current_hosted_zone.name = desired_hosted_zone.name
            current_hosted_zone.id = desired_hosted_zone.id
            if not self.update_hosted_zone_information(current_hosted_zone, full_information=True):
                raise ValueError(f"Could not find the hosted zone {desired_hosted_zone.name}, use provision instead")
            desired_hosted_zone.id = current_hosted_zone.id

        request = current_hosted_zone.generate_upsert_resource_record_sets_request(desired_hosted_zone)
        if request:
            self.change_resource_record_sets_raw(request)

    def change_tags_for_resource_raw(self, request_dict):
        """
        Standard

        :param request_dict:
        :return:
        """

        logger.info(f"Updating resource tags: {request_dict}")

        for dict_src in self.execute(self.get_session_client().change_tags_for_resource, None, raw_data=True,
                                     filters_req=request_dict
                                     ):
            self.clear_cache(HostedZone)
            return dict_src

    def update(self, hosted_zone):
        """
        Update info.

        :param hosted_zone:
        :return:
        """

        hosted_zones = self.get_all_hosted_zones(name=hosted_zone.name)
        if len(hosted_zones) > 1:
            raise ValueError(f"More then 1 hosted_zone found: {len(hosted_zones)}")

        hosted_zone.updated(hosted_zones[0].dict_src)

    def associate_hosted_zone(self, hosted_zone):
        """
        To VPC.

        :param hosted_zone:
        :return:
        """

        for vpc_association in hosted_zone.vpc_associations:
            associate_request = {"HostedZoneId": hosted_zone.id, "VPC": vpc_association}
            self.associate_vpc_with_hosted_zone_raw(associate_request)

    def raw_create_hosted_zone(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Creating hosted zone: {request_dict}")
        for response in self.execute(
                self.get_session_client().create_hosted_zone, "HostedZone", filters_req=request_dict
        ):
            return response

    def associate_vpc_with_hosted_zone_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Associating VPC with hosted zone: {request_dict}")
        for response in self.execute(
                self.get_session_client().associate_vpc_with_hosted_zone,
                "ChangeInfo",
                filters_req=request_dict,
                exception_ignore_callback=lambda exception: "ConflictingDomainExists" in repr(exception)
        ):
            self.clear_cache(HostedZone)
            return response

    def disassociate_vpc_from_hosted_zone_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Disassociating VPC from hosted zone: {request_dict}")
        for response in self.execute(
                self.get_session_client().disassociate_vpc_from_hosted_zone,
                "ChangeInfo",
                filters_req=request_dict,
                exception_ignore_callback=lambda exception: "ConflictingDomainExists" in repr(exception)
        ):
            self.clear_cache(HostedZone)
            return response

    def change_resource_record_sets_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Updating hosted zone record set: {request_dict}")

        for response in self.execute(
                self.get_session_client().change_resource_record_sets,
                "ChangeInfo",
                filters_req=request_dict
        ):
            self.clear_cache(HostedZone)
            return response

        return None

    def update_hosted_zone_information(self, hosted_zone, full_information=False):
        """
        Standard.

        :param hosted_zone:
        :param full_information:
        :return:
        """

        hosted_zone_name = hosted_zone.name.strip(".")
        filters_req = {"DNSName": hosted_zone_name}
        if hosted_zone.id is None:
            for response in self.execute(
                    self.get_session_client().list_hosted_zones_by_name,
                    "HostedZones",
                    filters_req=filters_req,
            ):
                if response["Name"].strip(".") == hosted_zone_name:
                    hosted_zone.update_from_raw_response(response)
                    break
            else:
                return False

        if full_information:
            self.get_hosted_zone_full_information(hosted_zone)

        return True

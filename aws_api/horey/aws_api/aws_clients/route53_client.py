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
        for entity in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  HostedZone,
                                                  update_info=update_info,
                                                  full_information_callback=self.get_hosted_zone_full_information if full_information else None,
                                                  global_service=True,
                                                  filters_req=filters_req):
            yield entity

    def yield_hosted_zones_raw(self, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.client.list_hosted_zones, "HostedZones", filters_req=filters_req
        ):
            yield dict_src

    def get_all_hosted_zones(self, full_information=True, name=None):
        """
        Get all hosted zones

        :param name:
        :param full_information:
        :return:
        """

        hosted_zones = list(self.yield_hosted_zones(full_information=full_information))

        if name is not None:
            if not name.endswith("."):
                name += "."
            hosted_zones = [hz for hz in hosted_zones if hz.name == name]

        return hosted_zones

    def get_hosted_zone_full_information(self, hosted_zone: HostedZone):
        """
        Standard.

        :param hosted_zone:
        :return:
        """
        hosted_zone.records = []
        for update_info in self.execute(
            self.client.list_resource_record_sets,
            "ResourceRecordSets",
            filters_req={"HostedZoneId": hosted_zone.id},
        ):
            hosted_zone.update_record_set(update_info)

        for response in self.execute(
            self.client.get_hosted_zone,
            None,
            raw_data=True,
            filters_req={"Id": hosted_zone.id},
        ):
            response.update(response["HostedZone"])
            del response["ResponseMetadata"]
            del response["HostedZone"]
            hosted_zone.update_from_raw_response(response)

    def provision_hosted_zone(self, hosted_zone, declarative=False):
        """
        Standard.

        :param declarative:
        :param hosted_zone:
        :return:
        """

        hosted_zones = self.get_all_hosted_zones(name=hosted_zone.name, full_information=False)
        if len(hosted_zones) > 1:
            raise ValueError(
                f"More then 1 '{hosted_zone.name}' hosted_zone found: {len(hosted_zones)}"
            )

        if len(hosted_zones) == 0:
            request = hosted_zone.generate_create_request()
            response = self.raw_create_hosted_zone(request)
            hosted_zone.id = response["Id"]
            self.associate_hosted_zone(hosted_zone)
            return hosted_zone

        current_hosted_zone = hosted_zones[0]
        self.get_hosted_zone_full_information(current_hosted_zone)

        hosted_zone.id = current_hosted_zone.id
        request = current_hosted_zone.generate_change_resource_record_sets_request(hosted_zone)
        if request:
            self.change_resource_record_sets_raw(request)

        associate_requests, disassociate_requests = current_hosted_zone.generate_association_requests(hosted_zone, declarative=declarative)

        if associate_requests:
            self.associate_vpc_with_hosted_zone_raw(associate_requests)

        if disassociate_requests:
            self.disassociate_vpc_from_hosted_zone_raw(disassociate_requests)

        self.get_hosted_zone_full_information(hosted_zone)
        return hosted_zone

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
            self.client.create_hosted_zone, "HostedZone", filters_req=request_dict
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
            self.client.associate_vpc_with_hosted_zone,
            "ChangeInfo",
            filters_req=request_dict,
            exception_ignore_callback=lambda exception: "ConflictingDomainExists" in repr(exception)
        ):
            return response

    def disassociate_vpc_from_hosted_zone_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Disassociating VPC from hosted zone: {request_dict}")
        for response in self.execute(
                self.client.disassociate_vpc_from_hosted_zone,
                "ChangeInfo",
                filters_req=request_dict,
                exception_ignore_callback=lambda exception: "ConflictingDomainExists" in repr(exception)
        ):
            return response

    def change_resource_record_sets_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Updating hosted zone record set: {request_dict}")

        for response in self.execute(
            self.client.change_resource_record_sets,
            "ChangeInfo",
            filters_req=request_dict,
            exception_ignore_callback=lambda error: "InvalidChangeBatch" in repr(error)
        ):
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
        for response in self.execute(
            self.client.list_hosted_zones_by_name,
            "HostedZones",
            filters_req=filters_req,
        ):
            if response["Name"].strip(".") == hosted_zone_name:
                hosted_zone.update_from_raw_response(response)
                break
        else:
            raise RuntimeError(
                f"Can not find hosted_zone by name: '{hosted_zone.name}'"
            )

        if full_information:
            self.get_hosted_zone_full_information(hosted_zone)

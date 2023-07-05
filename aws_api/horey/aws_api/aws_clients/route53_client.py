"""
AWS route-53 client to handle route-53 service API requests.
"""
import sys
import os
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.route53_hosted_zone import HostedZone
from horey.h_logger import get_logger
import pdb

logger = get_logger()


class Route53Client(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "route53"
        super().__init__(client_name)

    def get_all_hosted_zones(self, full_information=True, name=None):
        """
        Get all osted zones
        :param full_information:
        :return:
        """
        final_result = list()
        if name is not None and not name.endswith("."):
            name += "."
        for response in self.execute(self.client.list_hosted_zones, "HostedZones"):
            obj = HostedZone(response)
            if name is not None and obj.name != name:
                continue

            if full_information:
                self.get_hosted_zone_full_information(obj)
            final_result.append(obj)

        return final_result

    def get_hosted_zone_full_information(self, hsoted_zone):
        hsoted_zone.records = []
        for update_info in self.execute(
            self.client.list_resource_record_sets,
            "ResourceRecordSets",
            filters_req={"HostedZoneId": hsoted_zone.id},
        ):
            hsoted_zone.update_record_set(update_info)

    def change_resource_record_sets(self, name):
        pdb.set_trace()
        ret = self.get_all_hosted_zones()

        for response in self.execute(
            self.client.list_traffic_policy_instances, "HostedZones", raw_data=True
        ):
            pdb.set_trace()

    def provision_hosted_zone(self, hosted_zone):
        changes = []
        for record in hosted_zone.records:
            change = {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": record.name,
                    "Type": record.type,
                }
            }

            if record.ttl is not None:
                change["ResourceRecordSet"]["TTL"] = record.ttl

            if record.resource_records is not None:
                change["ResourceRecordSet"]["ResourceRecords"] = record.resource_records

            if record.alias_target is not None:
                change["ResourceRecordSet"]["AliasTarget"] = record.alias_target

            changes.append(change)

        hosted_zones = self.get_all_hosted_zones(name=hosted_zone.name)
        if len(hosted_zones) > 1:
            raise ValueError(
                f"More then 1 '{hosted_zone.name}' hosted_zone found: {len(hosted_zones)}"
            )

        if len(hosted_zones) == 1:
            hosted_zone.update_from_raw_response(hosted_zones[0].dict_src)
        else:
            request = hosted_zone.generate_create_request()
            response = self.raw_create_hosted_zone(request)
            hosted_zone.id = response["Id"]

        self.associate_hosted_zone(hosted_zone)

        if len(changes) != 0:
            request = {
                "HostedZoneId": hosted_zone.id,
                "ChangeBatch": {"Changes": changes},
            }
            self.raw_change_resource_record_sets(request)

        hosted_zones = self.get_all_hosted_zones(name=hosted_zone.name)
        hosted_zone.update_from_raw_response(hosted_zones[0].dict_src)
        hosted_zone.records = hosted_zones[0].records

    def update(self, hosted_zone):
        hosted_zones = self.get_all_hosted_zones(name=hosted_zone.name)
        if len(hosted_zones) > 1:
            raise ValueError(f"More then 1 hosted_zone found: {len(hosted_zones)}")

        hosted_zone.updated(hosted_zones[0].dict_src)

    def associate_hosted_zone(self, hosted_zone):
        for vpc_association in hosted_zone.vpc_associations:
            associate_request = {"HostedZoneId": hosted_zone.id, "VPC": vpc_association}
            self.raw_associate_vpc_with_hosted_zone(associate_request)

    def raw_create_hosted_zone(self, request_dict):
        logger.info(f"Creating hosted zone: {request_dict}")
        for response in self.execute(
            self.client.create_hosted_zone, "HostedZone", filters_req=request_dict
        ):
            return response

    def raw_associate_vpc_with_hosted_zone(self, request_dict):
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

    def raw_change_resource_record_sets(self, request_dict):
        logger.info(f"Updating hosted zone record set: {request_dict}")
        try:
            for response in self.execute(
                self.client.change_resource_record_sets,
                "ChangeInfo",
                filters_req=request_dict,
            ):
                return response
        except Exception as exception_instance:
            repr_exception = repr(exception_instance)
            if "already exists" not in repr_exception:
                raise
            logger.warning(repr_exception)

    def update_hosted_zone_information(self, hosted_zone, full_information=False):
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

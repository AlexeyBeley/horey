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

    def get_all_hosted_zones(self, full_information=True):
        """
        Get all osted zones
        :param full_information:
        :return:
        """
        final_result = list()

        for response in self.execute(self.client.list_hosted_zones, "HostedZones"):

            obj = HostedZone(response)

            if full_information:
                for update_info in self.execute(self.client.list_resource_record_sets, "ResourceRecordSets", filters_req={"HostedZoneId": obj.id}):
                    obj.update_record_set(update_info)

            final_result.append(obj)
        return final_result

    def change_resource_record_sets(self, name):
        pdb.set_trace()
        ret = self.get_all_hosted_zones()

        for response in self.execute(self.client.list_traffic_policy_instances, "HostedZones", raw_data=True):
            pdb.set_trace()

    def create_hosted_zone(self, hosted_zone):
        request = hosted_zone.generate_create_request()
        try:
            response = self.raw_create_hosted_zone(request)
            hosted_zone.id = response["Id"]
        except Exception as exception_instance:
            logger.warning(repr(exception_instance))
            if "ConflictingDomainExists" not in repr(exception_instance):
                raise
            response = self.get_hosted_zone(name=hosted_zone.name)
            hosted_zone.id = response["Id"]

    def get_hosted_zone(self, name=None):
        if name is None:
            raise ValueError("Name not set")

        request_dict = {"DNSName": name}

        for response in self.execute(self.client.list_hosted_zones_by_name, "HostedZones", filters_req=request_dict):
            return response

    def raw_create_hosted_zone(self, request_dict):
        for response in self.execute(self.client.create_hosted_zone, "HostedZone", filters_req=request_dict):
            return response

    def raw_associate_vpc_with_hosted_zone(self, request_dict):
        try:
            for response in self.execute(self.client.associate_vpc_with_hosted_zone, "ChangeInfo", filters_req=request_dict):
                return response
        except Exception as exception_instance:
            repr_exception = repr(exception_instance)
            logger.warning(repr_exception)
            if "ConflictingDomainExists" not in repr_exception:
                raise

    def raw_change_resource_record_sets(self, request_dict):
        try:
            for response in self.execute(self.client.change_resource_record_sets, "ChangeInfo", filters_req=request_dict):
                return response
        except Exception as exception_instance:
            repr_exception = repr(exception_instance)
            if "already exists" not in repr_exception:
                raise
            logger.warning(repr_exception)

"""
AWS route-53 client to handle route-53 service API requests.
"""
import sys
import os
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.route53_hosted_zone import HostedZone
import pdb


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
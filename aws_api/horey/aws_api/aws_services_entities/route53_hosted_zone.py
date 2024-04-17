"""
Module handling AWS route53 hosted zone
"""
import copy
import datetime

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.h_logger import get_logger

logger = get_logger()


class HostedZone(AwsObject):
    """
    Class representing AWS Route53 hosted zone.
    """

    def __init__(self, dict_src, from_cache=False):
        self.records = []
        self.vpc_associations = []
        self.config = None
        self.type = None
        self.delegation_set = None

        super().__init__(dict_src)
        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "Id": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "Name": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "CallerReference": self.init_default_attr,
            "Config": self.init_default_attr,
            "ResourceRecordSetCount": self.init_default_attr,
            "LinkedService": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def _init_object_from_cache(self, dict_src):
        """
        Init the object from saved cache dict
        :param dict_src:
        :return:
        """
        options = {"records": self._init_records_from_cache}
        self._init_from_cache(dict_src, options)

    def update_record_set(self, dict_src):
        """
        Update information from AWS API response
        :param dict_src:
        :return:
        """
        self.records.append(self.Record(dict_src))

    def _init_records_from_cache(self, _, lst_src):
        """
        Init records with aws api information
        :param _:
        :param lst_src:
        :return:
        """
        if self.records:
            raise NotImplementedError("Can't reinit existing")

        for record in lst_src:
            self.records.append(self.Record(record, from_cache=True))

    def generate_create_request(self):
        """
        Standard.

        :return:
        """

        request = {
            "Name": self.name,
            "CallerReference": self.name + str(datetime.datetime.now()),
            "HostedZoneConfig": self.config,
        }
        if len(self.vpc_associations) > 0:
            request["VPC"] = self.vpc_associations[0]

        return request

    class Record(AwsObject):
        """
        Class representing AWS hosted zone record
        """

        def __init__(self, dict_src, from_cache=False):
            super().__init__(dict_src)
            self.ttl = None
            self.resource_records = None
            self.alias_target = None
            self.type = None

            if from_cache:
                self._init_object_from_cache(dict_src)
                return

            init_options = {
                "Name": lambda x, y: self.init_default_attr(
                    x, y, formatted_name="name"
                ),
                "Type": self.init_default_attr,
                "AliasTarget": self.init_default_attr,
                "TTL": self.init_default_attr,
                "ResourceRecords": self.init_default_attr,
                "SetIdentifier": self.init_default_attr,
                "Weight": self.init_default_attr,
                "MultiValueAnswer": self.init_default_attr,
                "HealthCheckId": self.init_default_attr,
                "LinkedService": self.init_default_attr,
            }

            self.init_attrs(dict_src, init_options)

        def _init_object_from_cache(self, dict_src):
            """
            Init the object from saved cache dict
            :param dict_src:
            :return:
            """
            options = {}
            self._init_from_cache(dict_src, options)

        def generate_dispose_request(self):
            """
            Standard.

            :return:
            """

            return {
                "Action": "DELETE",
                "ResourceRecordSet": {
                    "Name": self.name,
                    "Type": self.type,
                    "TTL": self.ttl,
                    "ResourceRecords": self.resource_records,
                },
            }

    def update_from_raw_response(self, dict_src):
        """
        Standard.

        :param dict_src:
        :return:
        """
        init_options = {
            "Name": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "Id": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "Type": self.init_default_attr,
            "AliasTarget": self.init_default_attr,
            "TTL": self.init_default_attr,
            "ResourceRecords": self.init_default_attr,
            "SetIdentifier": self.init_default_attr,
            "Weight": self.init_default_attr,
            "MultiValueAnswer": self.init_default_attr,
            "HealthCheckId": self.init_default_attr,
            "CallerReference": self.init_default_attr,
            "Config": self.init_default_attr,
            "ResourceRecordSetCount": self.init_default_attr,
            "LinkedService": self.init_default_attr,
            "VPCs": lambda x, y: self.init_default_attr(x, y, formatted_name="vpc_associations"),
            "DelegationSet": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options, raise_on_no_option=True)

    def generate_change_resource_record_sets_request(self, desired_state):
        """
        Standard.

        :param desired_state:
        :return:
        """

        self_records = [record.dict_src for record in self.records]

        changes = []
        for record in desired_state.records:
            if not record.dict_src["Name"].endswith("."):
                dict_record = copy.deepcopy(record.dict_src)
                dict_record["Name"] += "."
            else:
                dict_record = record.dict_src

            if dict_record in self_records:
                continue

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

        if len(changes) != 0:
            return {
                "HostedZoneId": self.id,
                "ChangeBatch": {"Changes": changes},
            }

        return None

    def generate_association_requests(self, desired_state, declarative=False):
        """
        Standard.

        :param declarative:
        :param desired_state:
        :return: associate_vpc, disassociate_vpcs
        """

        associate_requests, disassociate_requests = [], []
        if declarative:
            for vpc_association in self.vpc_associations:
                if vpc_association not in desired_state.vpc_associations:
                    disassociate_requests.append({"HostedZoneId": self.id, "VPC": vpc_association})

        for vpc_association in desired_state.vpc_associations:
            if vpc_association not in self.vpc_associations:
                associate_requests.append({"HostedZoneId": self.id, "VPC": vpc_association})

        return associate_requests, disassociate_requests

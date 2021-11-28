"""
AWS client to handle service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.event_bridge_rule import EventBridgeRule
from horey.aws_api.aws_services_entities.event_bridge_target import EventBridgeTarget

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.h_logger import get_logger
logger = get_logger()

import pdb


class EventsClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "events"
        super().__init__(client_name)

    def get_all_rules(self, region=None, full_information=True):
        """
        Get all rules in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_rules(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_rules(region, full_information=full_information)

        return final_result

    def get_region_rules(self, region, full_information=True, custom_filter=None):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.list_rules, "Rules", filters_req=custom_filter):
            obj = EventBridgeRule(dict_src)
            final_result.append(obj)
            if full_information:
                self.update_rule_targets(obj)
                self.update_rule_tags(obj)
                pass

        return final_result

    def update_rule_targets(self, rule):
        filters_req = {"Rule": rule.name}
        rule.targets = []
        for dict_src in self.execute(self.client.list_targets_by_rule, "Targets", filters_req=filters_req):
            obj = EventBridgeTarget(dict_src)
            rule.targets.append(obj)

    def update_rule_tags(self, rule):
        filters_req = {"ResourceARN": rule.arn}
        rule.tags = []
        for dict_src in self.execute(self.client.list_tags_for_resource, "Tags", filters_req=filters_req):
            rule.targets.append(dict_src)

    def get_samples(self):
        ret = list(self.execute(self.client.list_connections, None, raw_data=True))
        ret = list(self.execute(self.client.list_event_buses, None, raw_data=True))
        ret = list(self.execute(self.client.list_event_sources, None, raw_data=True))
        ret = list(self.execute(self.client.list_partner_event_source_accounts, None, raw_data=True))
        ret = list(self.execute(self.client.list_partner_event_sources, None, raw_data=True))
        ret = list(self.execute(self.client.list_replays, None, raw_data=True))
        ret = list(self.execute(self.client.list_rule_names_by_target, None, raw_data=True))
        ret = list(self.execute(self.client.list_targets_by_rule, None, raw_data=True, filters_req={"Rule":"initiator-production-InitiatorEventsRuleSchedule1-MWYJ6917GUN9"}))

    def update_rule_information(self, rule):
        region_rules = self.get_region_rules(rule.region, custom_filter={"NamePrefix": rule.name})
        if len(region_rules) == 1:
            rule.update_from_raw_response(region_rules[0].dict_src)
            return

        if len(region_rules) > 1:
            raise RuntimeError(region_rules)

    def provision_rule(self, rule: EventBridgeRule):
        self.update_rule_information(rule)
        AWSAccount.set_aws_region(rule.region)

        if rule.arn is None:
            response = self.provision_rule_raw(rule.generate_create_request())
            del response["ResponseMetadata"]
            rule.update_from_raw_response(response)

        put_targets_request = rule.generate_put_targets_request()
        if put_targets_request is not None:
            self.put_targets_raw(put_targets_request)

    def provision_rule_raw(self, request_dict):
        logger.info(f"Creating rule: {request_dict}")
        for response in self.execute(self.client.put_rule, None, raw_data=True,
                                     filters_req=request_dict):
            return response

    def put_targets_raw(self, request_dict):
        logger.info(f"Putting targets: {request_dict}")
        for response in self.execute(self.client.put_targets, None, raw_data=True,
                                     filters_req=request_dict):
            if response.get("FailedEntryCount") != 0:
                raise RuntimeError(response)

            return response

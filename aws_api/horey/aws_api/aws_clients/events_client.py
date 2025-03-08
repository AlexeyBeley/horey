"""
AWS client to handle service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.event_bridge_rule import EventBridgeRule
from horey.aws_api.aws_services_entities.event_bridge_target import EventBridgeTarget

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.h_logger import get_logger

logger = get_logger()


class EventsClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "events"
        super().__init__(client_name)

    def yield_rules(self, region=None, update_info=False, filters_req=None, get_tags=True, full_information=True):
        """
        Yield tables

        :return:
        """

        regional_fetcher_generator = self.yield_rules_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            EventBridgeRule,
                                                            update_info=update_info,
                                                            get_tags_callback=self.update_rule_tags if get_tags else None,
                                                            full_information_callback=self.update_rule_targets if full_information else None,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_rules_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
            self.get_session_client(region=region).list_rules, "Rules", filters_req=filters_req
        )

    def get_all_rules(self, region=None, full_information=True):
        """
        Get all rules in all regions.
        :return:
        """

        return list(self.yield_rules(region=region, full_information=full_information))

    def get_region_rules(self, region, full_information=True, filters_req=None):
        """
        Standard

        :param region:
        :param full_information:
        :param custom_filter:
        :return:
        """

        return list(self.yield_rules(region=region, full_information=full_information, filters_req=filters_req))

    def update_rule_targets(self, rule):
        """
        Standard

        :param rule:
        :return:
        """
        filters_req = {"Rule": rule.name}
        rule.targets = []
        for dict_src in self.execute(
                self.get_session_client(region=rule.region).list_targets_by_rule, "Targets", filters_req=filters_req
        ):
            obj = EventBridgeTarget(dict_src)
            rule.targets.append(obj)

    def update_rule_tags(self, rule):
        """
        Standard

        :param rule:
        :return:
        """
        filters_req = {"ResourceARN": rule.arn}
        rule.tags = []
        for dict_src in self.execute(
                self.get_session_client(region=rule.region).list_tags_for_resource, "Tags", filters_req=filters_req
        ):
            rule.targets.append(dict_src)

    def update_rule_information(self, rule):
        """
        Standard

        :param rule:
        :return:
        """

        region_rules = self.get_region_rules(
            rule.region, custom_filter={"NamePrefix": rule.name}
        )

        if len(region_rules) == 1:
            rule.update_from_raw_response(region_rules[0].dict_src)
            return True

        if len(region_rules) > 1:
            raise RuntimeError(region_rules)

        return False

    def provision_rule(self, rule: EventBridgeRule):
        """
        Standard

        :param rule:
        :return:
        """

        self.update_rule_information(rule)

        if rule.arn is None:
            response = self.provision_rule_raw(rule.region, rule.generate_create_request())
            del response["ResponseMetadata"]
            rule.update_from_raw_response(response)
        put_targets_request = rule.generate_put_targets_request()
        if put_targets_request is not None:
            self.put_targets_raw(rule.region, put_targets_request)

    def provision_rule_raw(self, region, request_dict):
        """
        Standard

        :param region:
        :param request_dict:
        :return:
        """
        logger.info(f"Creating rule: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).put_rule, None, raw_data=True, filters_req=request_dict
        ):
            return response

    def put_targets_raw(self, region, request_dict):
        """
        Standard

        :param region:
        :param request_dict:
        :return:
        """
        logger.info(f"Putting targets: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).put_targets, None, raw_data=True, filters_req=request_dict
        ):
            if response.get("FailedEntryCount") != 0:
                raise RuntimeError(response)

            return response

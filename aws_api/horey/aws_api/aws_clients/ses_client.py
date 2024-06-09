"""
AWS lambda client to handle lambda service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.aws_services_entities.ses_identity import SESIdentity
from horey.aws_api.aws_services_entities.ses_receipt_rule_set import SESReceiptRuleSet
from horey.common_utils.common_utils import CommonUtils

from horey.h_logger import get_logger

logger = get_logger()


class SESClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    UNSUPPORTED_REGIONS = ["ap-east-1", "ap-southeast-3"]

    def __init__(self):
        client_name = "ses"
        super().__init__(client_name)

    # pylint: disable= too-many-arguments
    def yield_receipt_rule_sets(self, region=None, update_info=False, filters_req=None):
        """
        Yield receipt_rule_sets

        :return:
        """

        regional_fetcher_generator = self.yield_receipt_rule_sets_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            SESReceiptRuleSet,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_receipt_rule_sets_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.get_session_client(region=region).list_receipt_rule_sets, "RuleSets", filters_req=filters_req
        ):
            for dict_src_tmp in self.execute(
                    self.get_session_client(region=region).describe_receipt_rule_set, None, raw_data=True,
                    filters_req={"RuleSetName": dict_src["Name"]}
            ):
                del dict_src_tmp["Metadata"]
                del dict_src_tmp["ResponseMetadata"]
                dict_src.update(dict_src_tmp)
            yield dict_src

    def provision_receipt_rule_set(self, rule_set: SESReceiptRuleSet):
        """
        Standard.

        :param rule_set:
        :return:
        """

        region_rule_set = SESReceiptRuleSet({"name": rule_set.name})
        region_rule_set.region = rule_set.region

        if not self.update_rule_set_information(region_rule_set):
            self.create_receipt_rule_set_raw(region_rule_set.region, {"RuleSetName": region_rule_set.name})
            region_rule_set.active = False
        else:
            region_rule_set.active = self.get_active_rule_set_name(rule_set.region) == region_rule_set.name

        reorder_request, create_requests, delete_requests = region_rule_set.generate_change_rules_requests(rule_set)
        if reorder_request:
            raise NotImplementedError("Reorder rules set")

        for create_request in create_requests:
            self.create_receipt_rule_raw(rule_set.region, create_request)

        for delete_request in delete_requests:
            self.delete_receipt_rule_raw(rule_set.region, delete_request)

        update_requests = region_rule_set.generate_update_receipt_rule_requests(rule_set)
        for update_request in update_requests:
            self.update_receipt_rule_raw(rule_set.region, update_request)

        activate_request, deactivate_requests, = region_rule_set.generate_change_active_requests(rule_set)

        if deactivate_requests:
            raise NotImplementedError("deactivate_requests")

        if activate_request:
            self.set_active_receipt_rule_set_raw(rule_set.region, {"RuleSetName": rule_set.name})

        return self.update_rule_set_information(rule_set)

    def get_active_rule_set_name(self, region):
        """
        Fetch current active rule set name.

        :return:
        """

        for dict_ret in self.execute(
                self.get_session_client(region=region).describe_active_receipt_rule_set, "Metadata"
        ):
            return dict_ret["Name"]

    def update_rule_set_information(self, rule_set):
        """
        Standard

        :param rule_set:
        :return:
        """
        all_sets = list(self.yield_receipt_rule_sets(region=rule_set.region))
        name_sets = CommonUtils.find_objects_by_values(all_sets, {"name": rule_set.name})
        if len(name_sets) == 0:
            return False

        if len(name_sets) > 1:
            raise ValueError(f"More then 1 rule set found: {rule_set.name=}")

        return rule_set.update_from_attrs(name_sets[0])

    def set_active_receipt_rule_set_raw(self, region, dict_request):
        """
        Standard.

        :return:
        """
        logger.info(f"Activatomg RuleSet: {dict_request} ")
        for dict_ret in self.execute(
                self.get_session_client(region=region).set_active_receipt_rule_set, None, raw_data=True, filters_req=dict_request
        ):
            self.clear_cache(SESReceiptRuleSet)
            return dict_ret

    def delete_receipt_rule_raw(self, region, dict_request):
        """
        Standard.

        :return:
        """
        logger.info(f"Deleting rule: {dict_request} ")
        for dict_ret in self.execute(
                self.get_session_client(region=region).delete_receipt_rule, None, raw_data=True, filters_req=dict_request
        ):
            self.clear_cache(SESReceiptRuleSet)
            return dict_ret

    def update_receipt_rule_raw(self, region, dict_request):
        """
        Yield dictionaries.

        :return:
        """
        logger.info(f"Updating rule: {dict_request} ")
        for dict_ret in self.execute(
                self.get_session_client(region=region).update_receipt_rule, None, raw_data=True, filters_req=dict_request
        ):
            self.clear_cache(SESReceiptRuleSet)
            return dict_ret

    def create_receipt_rule_raw(self, region, dict_request):
        """
        Yield dictionaries.

        :return:
        """
        logger.info(f"Creating rule: {dict_request} ")
        for dict_ret in self.execute(
                self.get_session_client(region=region).create_receipt_rule, None, raw_data=True, filters_req=dict_request
        ):
            self.clear_cache(SESReceiptRuleSet)
            return dict_ret

    def create_receipt_rule_set_raw(self, region, dict_request=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_ret in self.execute(
                self.get_session_client(region=region).create_receipt_rule_set, None, raw_data=True, filters_req=dict_request
        ):
            self.clear_cache(SESReceiptRuleSet)
            return dict_ret

    # pylint: disable= too-many-arguments
    def yield_identities(self, region=None, update_info=False, filters_req=None, full_information=True):
        """
        Yield identities

        :return:
        """
        full_information_callback = self.update_identity_full_information if full_information else None
        regional_fetcher_generator = self.yield_identities_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            SESIdentity,
                                                            update_info=update_info,
                                                            full_information_callback=full_information_callback,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_identities_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for str_src in self.execute(
                self.get_session_client(region=region).list_identities, "Identities", filters_req=filters_req
        ):
            yield {"name": str_src}

    def update_identity_information(self, obj: SESIdentity, full_information=False):
        """
        Update from AWS API.

        :param full_information:
        :param obj:
        :return:
        """

        for identity in self.yield_identities():
            if identity.name == obj.name:
                if full_information:
                    self.update_identity_full_information(obj)
                return True

        return False

    def update_identity_full_information(self, obj: SESIdentity):
        """
        Standard.

        :param obj:
        :return:
        """

        for dict_src in self.execute(
                self.get_session_client(region=obj.region).get_identity_dkim_attributes, "DkimAttributes",
                filters_req={"Identities": [obj.name]}
        ):
            if list(dict_src.keys()) != [obj.name]:
                raise ValueError(dict_src)
            obj.update_from_raw_response(dict_src[obj.name])

        for dict_src in self.execute(
                self.get_session_client(region=obj.region).get_identity_mail_from_domain_attributes,
                "MailFromDomainAttributes", filters_req={"Identities": [obj.name]}
        ):
            if list(dict_src.keys()) != [obj.name]:
                raise ValueError(dict_src)
            obj.update_from_raw_response(dict_src[obj.name])

        for dict_src in self.execute(
                self.get_session_client(region=obj.region).get_identity_notification_attributes,
                "NotificationAttributes", filters_req={"Identities": [obj.name]}
        ):
            if list(dict_src.keys()) != [obj.name]:
                raise ValueError(dict_src)
            obj.update_from_raw_response(dict_src[obj.name])

        policy_names = list(self.execute(
            self.get_session_client(region=obj.region).list_identity_policies, "PolicyNames",
            filters_req={"Identity": obj.name}
        ))
        if policy_names:
            dict_policies = {"Policies": list(self.execute(
                self.get_session_client(region=obj.region).get_identity_policies, "Policies",
                filters_req={"Identity": obj.name, "PolicyNames": policy_names}))}
            obj.update_from_raw_response(dict_policies)
        else:
            logger.info(f"No identity policies for identity '{obj.name}'")

        for dict_src in self.execute(
                self.get_session_client(region=obj.region).get_identity_verification_attributes,
                "VerificationAttributes", filters_req={"Identities": [obj.name]}
        ):
            if list(dict_src.keys()) != [obj.name]:
                raise ValueError(dict_src)
            obj.update_from_raw_response(dict_src[obj.name])
        return False

    def provision_identity(self, current_email_identity: SESIdentity, desired_email_identity: SESIdentity):
        """
        Standard

        @param current_email_identity:
        @param desired_email_identity:
        @return:
        """

        if not self.update_identity_information(current_email_identity, full_information=True):
            raise ValueError("Create the identity using sesv2_client")
        """ 
                put_identity_policy
                set_identity_dkim_enabled
                set_identity_feedback_forwarding_enabled
                set_identity_headers_in_notifications_enabled
                set_identity_mail_from_domain
                set_identity_notification_topic
        """

        if desired_email_identity.dkim_attributes:
            raise NotImplementedError(f"{desired_email_identity.dkim_attributes=}")

        if desired_email_identity.dkim_signing_attributes:
            raise NotImplementedError(f"{desired_email_identity.dkim_signing_attributes=}")

        if current_email_identity.mail_from_attributes.get("BehaviorOnMxFailure") != "USE_DEFAULT_VALUE":
            raise NotImplementedError(f"{current_email_identity.mail_from_attributes=}")

        if not current_email_identity.feedback_forwarding_status:
            raise NotImplementedError(f"{current_email_identity.feedback_forwarding_status}")

        if current_email_identity.policies:
            raise NotImplementedError(f"{current_email_identity.policies}")

        if desired_email_identity.policies:
            raise NotImplementedError(f"{desired_email_identity.policies}")
        return True

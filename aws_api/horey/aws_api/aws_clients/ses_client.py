"""
AWS lambda client to handle lambda service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.aws_services_entities.ses_identity import SESIdentity
from horey.aws_api.aws_services_entities.ses_receipt_rule_set import SESReceiptRuleSet

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

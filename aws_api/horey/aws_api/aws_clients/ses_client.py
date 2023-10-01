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

        breakpoint()
        regional_fetcher_generator = self.yield_receipt_rule_sets_raw
        for obj in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  SESReceiptRuleSet,
                                                  update_info=update_info,
                                                  regions=[region] if region else None,
                                                  filters_req=filters_req):
            yield obj

    def yield_receipt_rule_sets_raw(self, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.client.get_account, None, raw_data=True, filters_req=filters_req
        ):
            yield dict_src

    # pylint: disable= too-many-arguments
    def yield_identities(self, region=None, update_info=False, filters_req=None, full_information=True):
        """
        Yield identities

        :return:
        """
        breakpoint()
        regional_fetcher_generator = self.yield_identities_raw
        for obj in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  SESIdentity,
                                                  update_info=update_info,
                                                  regions=[region] if region else None,
                                                  filters_req=filters_req):
            yield obj

    def yield_identities_raw(self, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.client.list_identities, "Identities", filters_req=filters_req
        ):
            breakpoint()
            yield dict_src

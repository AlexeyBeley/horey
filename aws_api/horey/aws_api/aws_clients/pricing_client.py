"""
AWS service client representation.
"""
import datetime

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.h_logger import get_logger

logger = get_logger()


class PricingClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    NEXT_PAGE_REQUEST_KEY = "NextToken"
    NEXT_PAGE_RESPONSE_KEY = "NextToken"
    NEXT_PAGE_INITIAL_KEY = ""

    def __init__(self):
        client_name = "pricing"
        super().__init__(client_name)

    def get_services(self):
        """
        Get the full list

        :return:
        """
        return list(self.yield_all_services())

    def yield_all_services(self):
        """
        Yield over the cloudfront services

        :return:
        """

        for response in self.execute(
            self.client.describe_services,
            "Services",
        ):
            yield response

    def get_price_list_urls(self, service_code, region):
        """
        Standard.

        :param service_code:
        :param region:
        :return:
        """

        ret = []
        AWSAccount.set_aws_region("us-east-1")
        for response in self.execute(
                self.client.list_price_lists,
                "PriceLists",
                filters_req={"ServiceCode":service_code,
                             "EffectiveDate": datetime.datetime.now(),
                             "RegionCode": region.region_mark,
                             "CurrencyCode": "USD"}
        ):
            for response_file in self.execute(
                    self.client.get_price_list_file_url,
                    "Url",
                    filters_req={"PriceListArn": response["PriceListArn"],
                                 "FileFormat": "json",
                                 }
            ):
                ret.append(response_file)
        return ret

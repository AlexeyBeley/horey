"""
AWS service client representation.
"""
import requests

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.price_list import PriceList
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
        Yield over the services

        :return:
        """

        for response in self.execute(
            self.client.describe_services,
            "Services",
        ):
            yield response

    def yield_price_lists(self, region=None, update_info=False, filters_req=None):
        """
        Yield over all price_lists.

        :return:
        """

        def cache_filter_callback(filters):
            """
            Generate cache file suffix based on the filter.

            :param filters:
            :return:
            """
            return filters["ServiceCode"]

        regional_fetcher_generator = self.yield_price_lists_raw
        for obj in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  PriceList,
                                                  update_info=update_info,
                                                  regions=[region] if region else None,
                                                  filters_req=filters_req, cache_filter_callback=cache_filter_callback):
            yield obj

    def yield_price_lists_raw(self, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """
        AWSAccount.set_aws_region("us-east-1")
        for response in self.execute(
                self.client.list_price_lists,
                "PriceLists",
                filters_req=filters_req
        ):
            for response_file_url in self.execute(
                    self.client.get_price_list_file_url,
                    "Url",
                    filters_req={"PriceListArn": response["PriceListArn"],
                                 "FileFormat": "json",
                                 }
            ):
                headers = {"Content-Type": "application/json"}
                logger.info(f"Fetching the price list from url: {response_file_url}")
                response = requests.get(response_file_url, headers=headers, timeout=5*60)
                price_list = response.json()
                yield price_list

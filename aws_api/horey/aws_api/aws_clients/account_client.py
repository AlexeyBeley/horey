"""
AWS account client
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.region import Region

from horey.h_logger import get_logger

logger = get_logger()


class AccountClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    Validate fingerprint
    openssl pkcs8 -in file_name.pem -inform PEM -outform DER -topk8 -nocrypt | openssl sha1 -c
    """

    def __init__(self):
        client_name = "account"
        super().__init__(client_name)

    def yield_regions(self, update_info=False):
        """
        Yield regions

        :return:
        """

        regional_fetcher_generator = self.yield_regions_raw
        for region in self.regional_service_entities_generator(regional_fetcher_generator,
                                                               Region,
                                                               update_info=update_info,
                                                               global_service=True):
            delattr(region, "region")
            yield region

    def get_all_regions(self, update_info=False):
        """
        Get all acm_regions in all regions.

        :return:
        """

        return list(self.yield_regions(update_info=update_info))

    def yield_regions_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """
        yield from self.execute(
                self.get_session_client(region=region).list_regions, "Regions", filters_req=filters_req
        )

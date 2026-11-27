"""
AWS client to handle service API requests.
"""

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.s3_access_point import S3AccessPoint
from horey.h_logger import get_logger

logger = get_logger()


class S3ControlClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self, aws_account=None):
        client_name = "s3control"
        super().__init__(client_name, aws_account=aws_account)

    def yield_access_points(self, region=None, update_info=False, filters_req=None, full_information=True):
        """
        Yield objects

        :return:
        """

        regional_fetcher_generator = self.yield_access_points_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            S3AccessPoint,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req,
                                                            full_information_callback=None if not full_information else self.update_access_point_full_information)

    def yield_access_points_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        filters_req = filters_req or {}
        if "AccountId" not in filters_req:
            filters_req["AccountId"] = self.account_id

        yield from self.execute(
                self.get_session_client(region=region).list_access_points, "AccessPointList",
                filters_req=filters_req
        )

    def update_access_point_full_information(self, access_point: S3AccessPoint):
        """
        Standard

        :param access_point:
        :return:
        """

        filters_req = {"AccountId": access_point.bucket_account_id,
                       "Name": access_point.name}
        for response in self.execute(
                self.get_session_client(region=access_point.region).get_access_point, None, raw_data=True,
                filters_req=filters_req
        ):
            access_point.update_from_raw_response(response)

"""
AWS elb client to handle elb service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.elb_load_balancer import ClassicLoadBalancer


class ELBClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self, aws_account=None):
        client_name = "elb"
        super().__init__(client_name, aws_account=aws_account)

    def get_all_load_balancers(self, region=None, update_info=False, filters_req=None):
        """
        Get all load balancers.

        :param filters_req:
        :param region:
        :param update_info:
        :param full_information:
        :return:
        """

        return list(self.yield_load_balancers(region=region, update_info=update_info, filters_req=filters_req))

    def yield_load_balancers(self, region=None, update_info=False, filters_req=None):
        """
        Yield load_balancers

        :return:
        """

        regional_fetcher_generator = self.yield_load_balancers_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                                    ClassicLoadBalancer,
                                                                    update_info=update_info,
                                                                    regions=[region] if region else None,
                                                                    filters_req=filters_req)

    def yield_load_balancers_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
                self.get_session_client(region=region).describe_load_balancers, "LoadBalancerDescriptions",
                filters_req=filters_req
        )

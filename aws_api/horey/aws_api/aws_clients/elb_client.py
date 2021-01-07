"""
AWS elb client to handle elb service API requests.
"""
from boto3_client import Boto3Client
from elb_load_balancer import ClassicLoadBalancer
from aws_account import AWSAccount


class ELBClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """
    def __init__(self):
        client_name = "elb"
        super().__init__(client_name)

    def get_all_load_balancers(self, full_information=True):
        """
        Get all loadbalancers.
        :param full_information:
        :return:
        """
        final_result = list()

        for region in AWSAccount.get_aws_account().regions.values():
            AWSAccount.set_aws_region(region)
            for response in self.execute(self.client.describe_load_balancers, "LoadBalancerDescriptions"):
                obj = ClassicLoadBalancer(response)
                final_result.append(obj)

                if full_information:
                    pass

        return final_result

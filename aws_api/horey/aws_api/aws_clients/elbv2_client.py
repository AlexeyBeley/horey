"""
AWS elb-v2 client to handle elb-v2 service API requests.
"""
from boto3_client import Boto3Client

from elbv2_load_balancer import LoadBalancer
from elbv2_target_group import ELBV2TargetGroup
from aws_account import AWSAccount


class ELBV2Client(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """
    def __init__(self):
        client_name = "elbv2"
        super().__init__(client_name)

    def get_all_load_balancers(self, full_information=True):
        """
        Get all loadnbalancers
        :param full_information:
        :return:
        """
        final_result = list()

        for region in AWSAccount.get_aws_account().regions.values():
            AWSAccount.set_aws_region(region)
            for response in self.execute(self.client.describe_load_balancers, "LoadBalancers"):
                obj = LoadBalancer(response)
                final_result.append(obj)

                if full_information:
                    pass

        return final_result

    def get_all_target_groups(self, full_information=True):
        """
        Get all target groups.
        :param full_information:
        :return:
        """
        final_result = list()
        for response in self.execute(self.client.describe_target_groups, "TargetGroups"):

            obj = ELBV2TargetGroup(response)
            final_result.append(obj)

            if full_information:
                try:
                    for update_info in self.execute(self.client.describe_target_health, "TargetHealthDescriptions", filters_req={"TargetGroupArn": obj.arn}):
                        obj.update_target_health(update_info)
                except Exception as inst:
                    print(response)
                    str_repr = repr(inst)
                    print(str_repr)
                    raise

        return final_result

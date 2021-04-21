"""
AWS elb-v2 client to handle elb-v2 service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.aws_services_entities.elbv2_load_balancer import LoadBalancer
from horey.aws_api.aws_services_entities.elbv2_target_group import ELBV2TargetGroup
from horey.aws_api.base_entities.aws_account import AWSAccount
import pdb

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

                for listener_response in self.execute(self.client.describe_listeners, "Listeners", filters_req={"LoadBalancerArn": obj.arn}):
                    obj.add_raw_listener(listener_response)

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

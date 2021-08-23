"""
AWS elb-v2 client to handle elb-v2 service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.aws_services_entities.elbv2_load_balancer import LoadBalancer
from horey.aws_api.aws_services_entities.elbv2_target_group import ELBV2TargetGroup
from horey.aws_api.base_entities.aws_account import AWSAccount
import pdb
from horey.h_logger import get_logger
logger = get_logger()


class ELBV2Client(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """
    def __init__(self):
        client_name = "elbv2"
        super().__init__(client_name)

    def get_all_load_balancers(self, full_information=True, region=None):
        """
        Get all loadnbalancers
        :param full_information:
        :param region:
        :return:
        """
        if region is not None:
            return self.get_region_load_balancers(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_load_balancers(region, full_information=full_information)
        return final_result

    def get_region_load_balancers(self, region, full_information=True):
        AWSAccount.set_aws_region(region)
        final_result = list()

        for response in self.execute(self.client.describe_load_balancers, "LoadBalancers"):
            obj = LoadBalancer(response)
            final_result.append(obj)

            if full_information:
                for listener_response in self.execute(self.client.describe_listeners, "Listeners",
                                                      filters_req={"LoadBalancerArn": obj.arn}):
                    obj.add_raw_listener(listener_response)
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

    def get_region_load_balancers(self, region, full_information=True):
        AWSAccount.set_aws_region(region)
        final_result = list()
        for response in self.execute(self.client.describe_load_balancers, "LoadBalancers"):
            obj = LoadBalancer(response)
            final_result.append(obj)

            if full_information:
                for listener_response in self.execute(self.client.describe_listeners, "Listeners",
                                                      filters_req={"LoadBalancerArn": obj.arn}):
                    obj.add_raw_listener(listener_response)
        return final_result

    def get_region_target_groups(self, region, full_information=True, target_group_names=None):
        AWSAccount.set_aws_region(region)
        final_result = list()
        filters_req = dict()
        if target_group_names is not None:
            filters_req["Names"] = target_group_names

        for response in self.execute(self.client.describe_target_groups, "TargetGroups", filters_req=filters_req):
            obj = ELBV2TargetGroup(response)
            final_result.append(obj)

            if full_information:
                try:
                    for update_info in self.execute(self.client.describe_target_health, "TargetHealthDescriptions",
                                                    filters_req={"TargetGroupArn": obj.arn}):
                        obj.update_target_health(update_info)
                except Exception as inst:
                    print(response)
                    str_repr = repr(inst)
                    print(str_repr)
                    raise
        return final_result

    def get_region_listeners(self, region, full_information=False, load_balancer_arn=None):
        AWSAccount.set_aws_region(region)
        final_result = list()

        filters_req = None
        if load_balancer_arn is not None:
            filters_req = {"LoadBalancerArn": load_balancer_arn}

        for response in self.execute(self.client.describe_listeners, "Listeners", filters_req=filters_req):
            obj = LoadBalancer.Listener(response)
            final_result.append(obj)

            if full_information:
                raise NotImplementedError()
        return final_result

    def provision_load_balancer(self, load_balancer):
        region_load_balancers = self.get_region_load_balancers(load_balancer.region, full_information=False)
        for region_load_balancer in region_load_balancers:
            if region_load_balancer.get_state() not in [region_load_balancer.State.PROVISIONING, region_load_balancer.State.ACTIVE, region_load_balancer.State.ACTIVE_IMPAIRED]:
                continue
            if region_load_balancer.get_tagname(ignore_missing_tag=True) == load_balancer.get_tagname():
                load_balancer.arn = region_load_balancer.arn
                return

        response = self.provision_load_balancer_raw(load_balancer.generate_create_request())
        load_balancer.arn = response["LoadBalancerArn"]

    def provision_load_balancer_raw(self, request_dict):
        for response in self.execute(self.client.create_load_balancer, "LoadBalancers", filters_req=request_dict):
            return response
        
    def provision_load_balancer_target_group(self, target_group):
        region_target_groups = self.get_region_target_groups(target_group.region, full_information=False)
        for region_target_group in region_target_groups:
            if region_target_group.get_tagname(ignore_missing_tag=True) == target_group.get_tagname():
                target_group.arn = region_target_group.arn
                return

        response = self.provision_load_balancer_target_group_raw(target_group.generate_create_request())
        target_group.arn = response["TargetGroupArn"]

        register_targets_request = target_group.generate_register_targets_request()
        if register_targets_request:
            self.register_targets_raw(register_targets_request)

    def provision_load_balancer_target_group_raw(self, request_dict):
        for response in self.execute(self.client.create_target_group, "TargetGroups", filters_req=request_dict):
            return response

    def register_targets_raw(self, request_dict):
        for response in self.execute(self.client.register_targets, None, filters_req=request_dict, raw_data=True):
            return response

    def provision_load_balancer_listener(self, listener):
        region_listeners = self.get_region_listeners(listener.region, full_information=False, load_balancer_arn=listener.load_balancer_arn)
        for region_listener in region_listeners:
            if region_listener.port == listener.port:
                listener.arn = region_listener.arn
                return

        response = self.provision_load_balancer_listener_raw(listener.generate_create_request())
        listener.arn = response["ListenerArn"]

    def provision_load_balancer_listener_raw(self, request_dict):
        for response in self.execute(self.client.create_listener, "Listeners", filters_req=request_dict):
            return response

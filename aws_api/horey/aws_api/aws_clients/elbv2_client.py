"""
AWS elb-v2 client to handle elb-v2 service API requests.
"""

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.elbv2_load_balancer import LoadBalancer
from horey.aws_api.aws_services_entities.elbv2_target_group import ELBV2TargetGroup
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.common_utils.common_utils import CommonUtils
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

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_load_balancers(_region, full_information=full_information)
        return final_result

    def get_region_load_balancers(self, region, names=None, full_information=True, get_tags=True):
        """
        Standard

        @param region:
        @param names:
        @param full_information:
        @param get_tags:
        @return:
        """
        AWSAccount.set_aws_region(region)
        final_result = []

        filters_req = None
        if names is not None:
            filters_req = {"Names": names}

        for response in self.execute(self.client.describe_load_balancers, "LoadBalancers", filters_req=filters_req,
                                     exception_ignore_callback=lambda error: "LoadBalancerNotFound" in repr(error)):
            obj = LoadBalancer(response)
            final_result.append(obj)

            if full_information:
                self.get_load_balancer_full_information(obj)

        if get_tags:
            self.update_tags(final_result)
        return final_result

    def update_tags(self, objects):
        """
        Standard

        @param objects:
        @return:
        """
        if len(objects) == 0:
            return
        for response in self.execute(self.client.describe_tags, "TagDescriptions",
                                     filters_req={"ResourceArns": [obj.arn for obj in objects]}):
            obj = \
                CommonUtils.find_objects_by_values(objects, {"arn": response["ResourceArn"]}, max_count=1)[0]
            obj.tags = response["Tags"]

    def get_load_balancer_full_information(self, load_balancer):
        """
        Standard

        @param load_balancer:
        @return:
        """

        for listener_response in self.execute(self.client.describe_listeners, "Listeners",
                                          filters_req={"LoadBalancerArn": load_balancer.arn}):

            load_balancer.add_raw_listener(listener_response)

            for rule_response in self.execute(self.client.describe_rules, "Rules",
                                                  filters_req={"ListenerArn": listener_response["ListenerArn"]}):
                load_balancer.add_raw_rule(rule_response)

    def get_all_target_groups(self, full_information=True):
        """
        Get all target groups.

        :param full_information:
        :return:
        """

        final_result = []
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

    def get_region_target_groups(self, region, full_information=True, target_group_names=None, load_balancer_arn=None):
        """
        Standard

        @param region:
        @param full_information:
        @param target_group_names:
        @param load_balancer_arn:
        @return:
        """

        AWSAccount.set_aws_region(region)
        final_result = []
        filters_req = {}
        if target_group_names is not None:
            filters_req["Names"] = target_group_names
        if load_balancer_arn is not None:
            filters_req["LoadBalancerArn"] = load_balancer_arn

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
        """
        Standard

        @param region:
        @param full_information:
        @param load_balancer_arn:
        @return:
        """

        AWSAccount.set_aws_region(region)
        final_result = []

        filters_req = None
        if load_balancer_arn is not None:
            filters_req = {"LoadBalancerArn": load_balancer_arn}

        for response in self.execute(self.client.describe_listeners, "Listeners", filters_req=filters_req):
            obj = LoadBalancer.Listener(response)
            final_result.append(obj)

            if full_information:
                raise NotImplementedError()
        return final_result

    def get_region_rules(self, region, full_information=False, listener_arn=None, get_tags=True):
        """
        Standard

        @param region:
        @param full_information:
        @param listener_arn:
        @param get_tags:
        @return:
        """

        AWSAccount.set_aws_region(region)
        final_result = []

        filters_req = None
        if listener_arn is not None:
            filters_req = {"ListenerArn": listener_arn}

        for response in self.execute(self.client.describe_rules, "Rules", filters_req=filters_req):
            obj = LoadBalancer.Rule(response)
            final_result.append(obj)

            if full_information:
                raise NotImplementedError()

        if get_tags:
            self.update_tags(final_result)

        return final_result

    def provision_load_balancer(self, load_balancer):
        """
        Standard

        @param load_balancer:
        @return:
        """

        region_load_balancers = self.get_region_load_balancers(load_balancer.region, full_information=False, names=[load_balancer.name])
        for region_load_balancer in region_load_balancers:
            if region_load_balancer.get_state() not in [region_load_balancer.State.PROVISIONING, region_load_balancer.State.ACTIVE, region_load_balancer.State.ACTIVE_IMPAIRED]:
                continue
            load_balancer.arn = region_load_balancer.arn
            return

        response = self.provision_load_balancer_raw(load_balancer.generate_create_request())
        load_balancer.arn = response["LoadBalancerArn"]

    def provision_load_balancer_raw(self, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """

        for response in self.execute(self.client.create_load_balancer, "LoadBalancers", filters_req=request_dict):
            return response

    def provision_load_balancer_target_group(self, target_group):
        """
        Standard

        @param target_group:
        @return:
        """

        region_target_groups = self.get_region_target_groups(target_group.region, full_information=False)
        for region_target_group in region_target_groups:
            if region_target_group.get_tagname(ignore_missing_tag=True) == target_group.get_tagname():
                target_group.arn = region_target_group.arn
                break
        else:
            response = self.provision_load_balancer_target_group_raw(target_group.generate_create_request())
            target_group.arn = response["TargetGroupArn"]

        register_targets_request = target_group.generate_register_targets_request()
        if register_targets_request:
            self.register_targets_raw(register_targets_request)

    def provision_load_balancer_target_group_raw(self, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """
        for response in self.execute(self.client.create_target_group, "TargetGroups", filters_req=request_dict):
            return response

    def register_targets_raw(self, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """
        for response in self.execute(self.client.register_targets, None, filters_req=request_dict, raw_data=True):
            return response

    def provision_load_balancer_listener(self, listener):
        """
        Standard

        @param listener:
        @return:
        """
        region_listeners = self.get_region_listeners(listener.region, full_information=False, load_balancer_arn=listener.load_balancer_arn)
        for region_listener in region_listeners:
            if region_listener.port == listener.port:
                listener.arn = region_listener.arn
                return

        response = self.provision_load_balancer_listener_raw(listener.generate_create_request())
        listener.arn = response["ListenerArn"]

    def provision_load_balancer_listener_raw(self, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """
        for response in self.execute(self.client.create_listener, "Listeners", filters_req=request_dict):
            return response

    def provision_load_balancer_rule(self, rule: LoadBalancer.Rule):
        """
        Standard

        @param rule:
        @return:
        """
        region_rules = self.get_region_rules(rule.region, full_information=False, listener_arn=rule.listener_arn)
        for region_rule in region_rules:
            if region_rule.get_tagname(ignore_missing_tag=True) == rule.get_tagname():
                rule.arn = region_rule.arn
                return

        response = self.provision_load_balancer_rule_raw(rule.generate_create_request())
        rule.update_from_raw_response(response)

    def provision_load_balancer_rule_raw(self, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """

        for response in self.execute(self.client.create_rule, "Rules", filters_req=request_dict):
            return response

    def dispose_load_balancer(self, load_balancer):
        """
        Standard

        @param load_balancer:
        @return:
        """
        AWSAccount.set_aws_region(load_balancer.region)

        if load_balancer.arn is None:
            region_lbs = self.get_region_load_balancers(load_balancer.region, names=[load_balancer.name])

            if len(region_lbs) > 1:
                raise ValueError(f"Can not find load_balancer '{load_balancer.name}': found {len(region_lbs)}")

            if len(region_lbs) == 0:
                return

            load_balancer.update_from_raw_response(region_lbs[0].dict_src)

        lb_listeners = self.get_region_listeners(load_balancer.region, load_balancer_arn=load_balancer.arn)
        for listener in lb_listeners:
            self.dispose_listener_raw(listener.generate_dispose_request())

        lb_target_groups = self.get_region_target_groups(load_balancer.region, load_balancer_arn=load_balancer.arn)
        for target_group in lb_target_groups:
            self.dispose_target_group_raw(target_group.generate_dispose_request())

        self.dispose_load_balancer_raw(load_balancer.generate_dispose_request())

    def dispose_target_group_raw(self, request):
        """
        Standard

        @param request:
        @return:
        """
        for response in self.execute(self.client.delete_target_group, None, raw_data=True,  filters_req=request):
            return response

    def dispose_load_balancer_raw(self, request):
        """
        Standard

        @param request:
        @return:
        """
        for response in self.execute(self.client.delete_load_balancer, None, raw_data=True,  filters_req=request):
            return response

    def dispose_listener_raw(self, request):
        """
        Standard

        @param request:
        @return:
        """

        for response in self.execute(self.client.delete_listener, None, raw_data=True,  filters_req=request):
            return response

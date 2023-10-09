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

    # pylint: disable= too-many-arguments
    def get_all_load_balancers(self, region=None, update_info=False, filters_req=None, full_information=True, get_tags=True):
        """
        Get all load balancers.

        :param filters_req:
        :param region:
        :param update_info:
        :param full_information:
        :return:
        """

        return list(self.yield_load_balancers(region=region, update_info=update_info, filters_req=filters_req, full_information=full_information, get_tags=get_tags))

    # pylint: disable= too-many-arguments
    def yield_load_balancers(self, region=None, update_info=False, filters_req=None, full_information=True, get_tags=True):
        """
        Yield load_balancers

        :return:
        """

        regional_fetcher_generator = self.yield_load_balancers_raw
        for certificate in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  LoadBalancer,
                                                  update_info=update_info,
                                                  full_information_callback=self.get_load_balancer_full_information if full_information else None,
                                                  get_tags_callback=self.get_tags if get_tags else None,
                                                  regions=[region] if region else None,
                                                  filters_req=filters_req):
            yield certificate

    def yield_load_balancers_raw(self, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.client.describe_load_balancers, "LoadBalancers", filters_req=filters_req
        ):
            yield dict_src

    # pylint: disable= too-many-arguments
    def get_region_load_balancers(
        self, region, names=None, full_information=True, get_tags=True, filters_req=None):
        """
        Standard

        @param region:
        @param names:
        @param full_information:
        @param filters_req:
        @param get_tags:
        @return:

        """
        AWSAccount.set_aws_region(region)

        if names is not None:
            logger.error("DEPRECATION WARNING! Use filters_req")
            if filters_req is None:
                filters_req = {}
            filters_req["Names"] = names

        return list(self.yield_load_balancers(full_information=full_information, region=region, get_tags=get_tags, filters_req=filters_req))


    def update_tags(self, objects):
        """
        Standard

        @param objects:
        @return:
        """
        if len(objects) == 0:
            return
        for response in self.execute(
            self.client.describe_tags,
            "TagDescriptions",
            filters_req={"ResourceArns": [obj.arn for obj in objects]},
        ):
            obj = CommonUtils.find_objects_by_values(
                objects, {"arn": response["ResourceArn"]}, max_count=1
            )[0]
            obj.tags = response["Tags"]

    # pylint: disable= arguments-differ
    def get_tags(self, obj):
        """
        Standard

        @param obj:
        @return:
        """

        for response in self.execute(
            self.client.describe_tags,
            "TagDescriptions",
            filters_req={"ResourceArns": [obj.arn]},
        ):
            obj.tags = response["Tags"]


    def get_load_balancer_full_information(self, load_balancer):
        """
        Standard

        @param load_balancer:
        @return:
        """

        for listener_response in self.execute(
            self.client.describe_listeners,
            "Listeners",
            filters_req={"LoadBalancerArn": load_balancer.arn},
        ):

            listener = load_balancer.Listener(listener_response)
            load_balancer.listeners.append(listener)

            listener.rules = list(self.execute(
                self.client.describe_rules,
                "Rules",
                filters_req={"ListenerArn": listener_response["ListenerArn"]},
            ))

    def get_target_group_full_information(self, target_group):
        """
        Target group full info.

        :param target_group:
        :return:
        """

        for response in self.execute(
                self.client.describe_target_health,
                "TargetHealthDescriptions",
                filters_req={"TargetGroupArn": target_group.arn},
        ):
            target_group.update_target_health(response)

    def yield_target_groups(self, region=None, update_info=False, full_information=True, filters_req=None):
        """
        Yield target_groups

        :return:
        """

        full_information_callback = None if not full_information else self.get_target_group_full_information

        regional_fetcher_generator = self.yield_target_groups_raw
        for certificate in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  ELBV2TargetGroup,
                                                  update_info=update_info,
                                                  full_information_callback=full_information_callback,
                                                  regions=[region] if region else None,
                                                  filters_req=filters_req):
            yield certificate

    def yield_target_groups_raw(self, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.client.describe_target_groups, "TargetGroups", filters_req=filters_req
        ):
            yield dict_src

    def get_all_target_groups(self, full_information=True, update_info=False):
        """
        Get all target groups.

        :param update_info:
        :param full_information:
        :return:
        """

        return list(self.yield_target_groups(full_information=full_information, update_info=update_info))

    def get_region_target_groups(
        self,
        region,
        full_information=True,
        target_group_names=None,
        load_balancer_arn=None,
    ):
        """
        Standard

        @param region:
        @param full_information:
        @param target_group_names:
        @param load_balancer_arn:
        @return:
        """

        AWSAccount.set_aws_region(region)
        filters_req = {}
        if target_group_names is not None:
            filters_req["Names"] = target_group_names
        if load_balancer_arn is not None:
            filters_req["LoadBalancerArn"] = load_balancer_arn

        filters_req = filters_req if filters_req else None
        return list(self.yield_target_groups(region=region, full_information=full_information, filters_req=filters_req))

    def get_region_listeners(
        self, region, full_information=False, load_balancer_arn=None
    ):
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

        for response in self.execute(
            self.client.describe_listeners, "Listeners", filters_req=filters_req
        ):
            obj = LoadBalancer.Listener(response)
            final_result.append(obj)

            if full_information:
                raise NotImplementedError()
        return final_result

    def get_region_rules(
        self, region, full_information=False, listener_arn=None, get_tags=True
    ):
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

        for response in self.execute(
            self.client.describe_rules, "Rules", filters_req=filters_req
        ):
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

        region_load_balancers = self.get_region_load_balancers(
            load_balancer.region, full_information=False, names=[load_balancer.name]
        )
        for region_load_balancer in region_load_balancers:
            if region_load_balancer.get_state() not in [
                region_load_balancer.State.PROVISIONING,
                region_load_balancer.State.ACTIVE,
                region_load_balancer.State.ACTIVE_IMPAIRED,
            ]:
                continue
            load_balancer.arn = region_load_balancer.arn
            load_balancer.dns_name = region_load_balancer.dns_name
            return

        response = self.provision_load_balancer_raw(
            load_balancer.generate_create_request()
        )
        load_balancer.arn = response["LoadBalancerArn"]

    def provision_load_balancer_raw(self, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """
        logger.info(f"Provisioning load balancer: {request_dict}")
        for response in self.execute(
            self.client.create_load_balancer, "LoadBalancers", filters_req=request_dict
        ):
            return response

    def provision_load_balancer_target_group(self, target_group):
        """
        Standard

        @param target_group:
        @return:
        """

        region_target_groups = self.get_region_target_groups(
            target_group.region, full_information=False
        )
        for region_target_group in region_target_groups:
            if (
                region_target_group.get_tagname(ignore_missing_tag=True)
                == target_group.get_tagname()
            ):
                target_group.arn = region_target_group.arn
                break
        else:
            response = self.provision_load_balancer_target_group_raw(
                target_group.generate_create_request()
            )
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

        logger.info(f"Provisioning load balancer's target group: {request_dict}")
        for response in self.execute(
            self.client.create_target_group, "TargetGroups", filters_req=request_dict
        ):
            self.clear_cache(ELBV2TargetGroup)
            return response

    def register_targets_raw(self, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """
        logger.info(f"Registering load balancers' targets: {request_dict}")

        for response in self.execute(
            self.client.register_targets, None, filters_req=request_dict, raw_data=True
        ):
            self.clear_cache(ELBV2TargetGroup)
            return response

    def provision_load_balancer_listener(self, listener: LoadBalancer.Listener):
        """
        Standard

        @param listener:
        @return:
        """
        region_listeners = self.get_region_listeners(
            listener.region,
            full_information=False,
            load_balancer_arn=listener.load_balancer_arn,
        )
        for region_listener in region_listeners:
            if region_listener.port == listener.port:
                listener.arn = region_listener.arn
                return

        response = self.provision_load_balancer_listener_raw(
            listener.generate_create_request()
        )
        listener.arn = response["ListenerArn"]

        for request in listener.generate_add_certificate_requests():
            self.add_listener_certificates_raw(request)

    def provision_load_balancer_listener_raw(self, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """
        logger.info(f"Provisioning load balancer's listener: {request_dict}")

        for response in self.execute(
            self.client.create_listener, "Listeners", filters_req=request_dict
        ):
            self.clear_cache(LoadBalancer.Listener)
            return response

    def add_listener_certificates_raw(self, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """

        logger.info(f"Adding load balancer listener's certificate: {request_dict}")

        for response in self.execute(
            self.client.add_listener_certificates, "Certificates", filters_req=request_dict
        ):
            self.clear_cache(LoadBalancer.Listener)
            return response

    def provision_load_balancer_rule(self, rule: LoadBalancer.Rule):
        """
        Standard

        @param rule:
        @return:
        """
        region_rules = self.get_region_rules(
            rule.region, full_information=False, listener_arn=rule.listener_arn
        )
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

        logger.info(f"Provisioning load balancer listener's rule: {request_dict}")

        for response in self.execute(
            self.client.create_rule, "Rules", filters_req=request_dict
        ):
            return response

    def dispose_load_balancer(self, load_balancer):
        """
        Standard

        @param load_balancer:
        @return:
        """
        AWSAccount.set_aws_region(load_balancer.region)

        if load_balancer.arn is None:
            region_lbs = self.get_region_load_balancers(
                load_balancer.region, names=[load_balancer.name]
            )

            if len(region_lbs) > 1:
                raise ValueError(
                    f"Can not find load_balancer '{load_balancer.name}': found {len(region_lbs)}"
                )

            if len(region_lbs) == 0:
                return

            load_balancer.update_from_raw_response(region_lbs[0].dict_src)

        lb_listeners = self.get_region_listeners(
            load_balancer.region, load_balancer_arn=load_balancer.arn
        )
        for listener in lb_listeners:
            self.dispose_listener_raw(listener.generate_dispose_request())

        lb_target_groups = self.get_region_target_groups(
            load_balancer.region, load_balancer_arn=load_balancer.arn
        )
        for target_group in lb_target_groups:
            self.dispose_target_group_raw(target_group.generate_dispose_request())

        self.dispose_load_balancer_raw(load_balancer.generate_dispose_request())

    def dispose_target_group_raw(self, request):
        """
        Standard

        @param request:
        @return:
        """
        logger.info(f"Disposing load balancer's target group: {request}")

        for response in self.execute(
            self.client.delete_target_group, None, raw_data=True, filters_req=request
        ):
            return response

    def dispose_load_balancer_raw(self, request):
        """
        Standard

        @param request:
        @return:
        """
        logger.info(f"Disposing load balancer: {request}")

        for response in self.execute(
            self.client.delete_load_balancer, None, raw_data=True, filters_req=request
        ):
            return response

    def dispose_listener_raw(self, request):
        """
        Standard

        @param request:
        @return:
        """
        logger.info(f"Disposing load balancer's listener: {request}")

        for response in self.execute(
            self.client.delete_listener, None, raw_data=True, filters_req=request
        ):
            return response

    def set_rule_priorities_raw(self, request):
        """
        Standard
        {"RulePriorities": [{"RuleArn": "string", "Priority": 123}]}
        {"RulePriorities": [{"RuleArn": "string", "Priority": 1}, {"RuleArn": "string", "Priority": 2}, {"RuleArn": "string", "Priority": 3}]}
        @param request:
        @return:
        """
        logger.info(f"Change load balancer rule priority: {request}")

        for response in self.execute(
            self.client.set_rule_priorities, "Rules", filters_req=request
        ):
            return response

"""
AWS elb-v2 client to handle elb-v2 service API requests.
"""

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.elbv2_load_balancer import LoadBalancer
from horey.aws_api.aws_services_entities.elbv2_target_group import ELBV2TargetGroup
from horey.common_utils.common_utils import CommonUtils
from horey.h_logger import get_logger

logger = get_logger()


class ELBV2Client(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """
    # https://docs.aws.amazon.com/general/latest/gr/elb.html
    HOSTED_ZONES = {
        "eu-central-1": "Z215JYRZR1TBD5",
        "us-east-1": "Z35SXDOTRQ7X7K",
        "us-west-2": "Z1H1FL5HABSF5",
        "us-west-1": "Z368ELLRRE2KJ0",
        "us-east-2": "Z3AADJGX6KTTL2"
    }

    def __init__(self):
        client_name = "elbv2"
        super().__init__(client_name)

    # pylint: disable= too-many-arguments
    def get_all_load_balancers(self, region=None, update_info=False, filters_req=None, full_information=True,
                               get_tags=True):
        """
        Get all load balancers.

        :param filters_req:
        :param region:
        :param update_info:
        :param full_information:
        :return:
        """

        return list(self.yield_load_balancers(region=region, update_info=update_info, filters_req=filters_req,
                                              full_information=full_information, get_tags=get_tags))

    # pylint: disable= too-many-arguments
    def yield_load_balancers(self, region=None, update_info=False, filters_req=None, full_information=True,
                             get_tags=True):
        """
        Yield load_balancers

        :return:
        """

        regional_fetcher_generator = self.yield_load_balancers_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            LoadBalancer,
                                                            update_info=update_info,
                                                            full_information_callback=self.get_load_balancer_full_information if full_information else None,
                                                            get_tags_callback=self.get_tags if get_tags else None,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_load_balancers_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
            self.get_session_client(region=region).describe_load_balancers, "LoadBalancers",
            filters_req=filters_req,
            exception_ignore_callback=lambda error: "LoadBalancerNotFoundException" in repr(error)
        )

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

        if names is not None:
            logger.error("DEPRECATION WARNING! Use filters_req")
            if filters_req is None:
                filters_req = {}
            filters_req["Names"] = names

        return list(self.yield_load_balancers(full_information=full_information, region=region, get_tags=get_tags,
                                              filters_req=filters_req))

    def update_tags(self, objects):
        """
        Standard

        @param objects:
        @return:
        """
        if len(objects) == 0:
            return
        for response in self.execute(
                self.get_session_client(region=objects[0].region).describe_tags,
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
                self.get_session_client(region=obj.region).describe_tags,
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
                self.get_session_client(region=load_balancer.region).describe_listeners,
                "Listeners",
                filters_req={"LoadBalancerArn": load_balancer.arn},
        ):
            listener = load_balancer.Listener(listener_response)
            load_balancer.listeners.append(listener)

            listener.rules = list(self.execute(
                self.get_session_client(region=load_balancer.region).describe_rules,
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
                self.get_session_client(region=target_group.region).describe_target_health,
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
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            ELBV2TargetGroup,
                                                            update_info=update_info,
                                                            full_information_callback=full_information_callback,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_target_groups_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
            self.get_session_client(region=region).describe_target_groups, "TargetGroups", filters_req=filters_req
        )

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

        filters_req = {}
        if target_group_names is not None:
            filters_req["Names"] = target_group_names
        if load_balancer_arn is not None:
            filters_req["LoadBalancerArn"] = load_balancer_arn

        filters_req = filters_req if filters_req else None
        return list(self.yield_target_groups(region=region, full_information=full_information, filters_req=filters_req))

    def update_listener_info(self, listener):
        """
        Standard.

        :param listener:
        :return:
        """

        for attr_name in ["load_balancer_arn", "region", "port"]:
            if not getattr(listener, attr_name):
                raise ValueError(f"Load balancer listener attribute '{attr_name}' was not set")

        for current_listener in self.get_region_listeners(listener.region,
                                                          load_balancer_arn=listener.load_balancer_arn):
            if current_listener.port == listener.port:
                listener.update_from_raw_response(current_listener.dict_src)
                return True

        return False

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

        final_result = []

        filters_req = None
        if load_balancer_arn is not None:
            filters_req = {"LoadBalancerArn": load_balancer_arn}

        for response in self.execute(
                self.get_session_client(region=region).describe_listeners, "Listeners", filters_req=filters_req
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

        final_result = []

        filters_req = None
        if listener_arn is not None:
            filters_req = {"ListenerArn": listener_arn}

        for response in self.execute(
                self.get_session_client(region=region).describe_rules, "Rules", filters_req=filters_req
        ):
            obj = LoadBalancer.Rule(response)
            final_result.append(obj)

            if full_information:
                raise NotImplementedError()

        if get_tags:
            self.update_tags(final_result)

        return final_result

    def update_load_balancer_information(self, load_balancer):
        """
        Standard.

        :param load_balancer:
        :return:
        """

        region_load_balancers = self.get_region_load_balancers(
            load_balancer.region, full_information=False, filters_req={"Names": [load_balancer.name]}
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
            return True
        return False

    def provision_load_balancer(self, load_balancer):
        """
        Standard

        @param load_balancer:
        @return:
        """

        current_load_balancer = LoadBalancer({})
        current_load_balancer.region = load_balancer.region
        current_load_balancer.name = load_balancer.name

        if self.update_load_balancer_information(current_load_balancer):
            load_balancer.arn = current_load_balancer.arn
            load_balancer.dns_name = current_load_balancer.dns_name
            return True

        response = self.provision_load_balancer_raw(load_balancer.region,
                                                    load_balancer.generate_create_request()
                                                    )
        load_balancer.arn = response["LoadBalancerArn"]
        return True

    def provision_load_balancer_raw(self, region, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """
        logger.info(f"Provisioning load balancer: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_load_balancer, "LoadBalancers", filters_req=request_dict
        ):
            return response

    def provision_load_balancer_target_group(self, target_group: ELBV2TargetGroup):
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
                    region_target_group.name
                    == target_group.name
            ):
                if target_group.protocol != region_target_group.protocol:
                    raise ValueError(f"{target_group.protocol=} {region_target_group.protocol=}")
                target_group.arn = region_target_group.arn
                request = region_target_group.generate_modify_request(target_group)
                if request:
                    self.modify_target_group_raw(target_group.region, request)
                break
        else:
            response = self.provision_load_balancer_target_group_raw(target_group.region,
                                                                     target_group.generate_create_request()
                                                                     )
            target_group.arn = response["TargetGroupArn"]

        register_targets_request = target_group.generate_register_targets_request()
        if register_targets_request:
            self.register_targets_raw(target_group.region, register_targets_request)

    def provision_load_balancer_target_group_raw(self, region, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """

        logger.info(f"Provisioning load balancer's target group: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_target_group, "TargetGroups", filters_req=request_dict
        ):
            self.clear_cache(ELBV2TargetGroup)
            return response

    def register_targets_raw(self, region, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """
        logger.info(f"Registering load balancers' targets: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).register_targets, None, filters_req=request_dict, raw_data=True
        ):
            self.clear_cache(ELBV2TargetGroup)
            return response

    def update_listener_information(self, listener, full_information=False):
        """
        Standard.

        :param full_information:
        :param listener:
        :return:
        """

        for regional_listener in self.get_region_listeners(
                listener.region,
                full_information=False,
                load_balancer_arn=listener.load_balancer_arn):
            if regional_listener.port == listener.port:
                listener.update_from_raw_response(regional_listener.dict_src)
                if full_information:
                    if regional_listener.protocol == "HTTPS":
                        request = {"ListenerArn": listener.arn}
                        listener.certificates = list(self.execute(self.get_session_client(region=listener.region).describe_listener_certificates, "Certificates", filters_req=request))
                return True
        return False

    def provision_load_balancer_listener(self, listener: LoadBalancer.Listener):
        """
        Standard

        @param listener:
        @return:
        """

        region_listener = LoadBalancer.Listener({})
        region_listener.region = listener.region
        region_listener.load_balancer_arn = listener.load_balancer_arn
        region_listener.port = listener.port

        if self.update_listener_information(region_listener, full_information=True):
            listener.arn = region_listener.arn
            request = region_listener.generate_modify_request(listener)
            if request:
                self.modify_listener_raw(listener.region, request)
            add_requests, remove_requests = region_listener.generate_modify_certificates_requests(listener)
            for add_request in add_requests:
                self.add_listener_certificates_raw(listener.region, add_request)
            for remove_request in remove_requests:
                self.remove_listener_certificates_raw(listener.region, remove_request)
            return True

        self.provision_load_balancer_listener_raw(listener.region,
                                                             listener.generate_create_request()
                                                             )
        return self.update_listener_information(listener)

    def provision_load_balancer_listener_raw(self, region, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """
        logger.info(f"Provisioning load balancer's listener: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).create_listener, "Listeners", filters_req=request_dict
        ):
            self.clear_cache(LoadBalancer.Listener)
            return response

    def modify_listener_raw(self, region, request_dict):
        """
        Standard.

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Modifying loadbalancer's listener: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).modify_listener, "Listeners", filters_req=request_dict
        ):
            self.clear_cache(LoadBalancer.Listener)
            return response

    def modify_target_group_raw(self, region, request_dict):
        """
        Standard.

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Modifying loadbalancer's targetgroup: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).modify_target_group, "TargetGroups", filters_req=request_dict
        ):
            self.clear_cache(ELBV2TargetGroup)
            return response

    def add_listener_certificates_raw(self, region, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """

        logger.info(f"Adding load balancer listener's certificate: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).add_listener_certificates, "Certificates",
                filters_req=request_dict
        ):
            self.clear_cache(LoadBalancer.Listener)
            return response

    def remove_listener_certificates_raw(self, region, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """

        logger.info(f"Removing load balancer listener's certificate: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).remove_listener_certificates, "Certificates",
                filters_req=request_dict
        ):
            self.clear_cache(LoadBalancer.Listener)
            return response

    def update_rule_information(self, rule: LoadBalancer.Rule):
        """
        Standard.

        :param rule:
        :return:
        """

        region_rules = self.get_region_rules(
            rule.region, full_information=False, listener_arn=rule.listener_arn
        )

        for region_rule in region_rules:
            if region_rule.get_tagname() == rule.get_tagname():
                rule.update_from_raw_response(region_rule.dict_src)
                return True

        return False

    def provision_load_balancer_rule(self, rule: LoadBalancer.Rule):
        """
        Standard

        @param rule:
        @return:
        """

        current_rule = LoadBalancer.Rule({})
        current_rule.listener_arn = rule.listener_arn
        if current_rule.tags is None:
            raise ValueError(f"Tags were not set: {rule.listener_arn=}")
        current_rule.tags = rule.tags

        if self.update_rule_information(current_rule):
            rule.arn = current_rule.arn
            modify_request = current_rule.generate_modify_request(rule)
            if modify_request:
                self.modify_rule_raw(rule.region, modify_request)

            return self.update_rule_information(rule)

        response = self.create_rule_raw(rule.region, rule.generate_create_request())
        rule.update_from_raw_response(response)
        return True

    def create_rule_raw(self, region, request_dict):
        """
        Standard.

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Provisioning load balancer listener's rule: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).create_rule, "Rules", filters_req=request_dict
        ):
            return response

    def modify_rule_raw(self, region, request_dict):
        """
        Standard.

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Modifying load balancer listener's rule: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).modify_rule, "Rules", filters_req=request_dict
        ):
            return response

    def delete_rule_raw(self, region, request_dict):
        """
        Standard.

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Deleting load balancer listener's rule: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).delete_rule, None, raw_data=True, filters_req=request_dict
        ):
            return response

    def dispose_load_balancer(self, load_balancer):
        """
        Standard

        @param load_balancer:
        @return:
        """

        if load_balancer.arn is None:
            region_lbs = self.get_region_load_balancers(
                load_balancer.region, filters_req={"Names": [load_balancer.name]}
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
            self.dispose_listener_raw(listener.region, listener.generate_dispose_request())

        lb_target_groups = self.get_region_target_groups(
            load_balancer.region, load_balancer_arn=load_balancer.arn
        )
        for target_group in lb_target_groups:
            self.dispose_target_group_raw(target_group.region, target_group.generate_dispose_request())

        self.dispose_load_balancer_raw(load_balancer.region, load_balancer.generate_dispose_request())

    def dispose_target_group_raw(self, region, request):
        """
        Standard

        @param request:
        @return:
        """
        logger.info(f"Disposing load balancer's target group: {request}")

        for response in self.execute(
                self.get_session_client(region=region).delete_target_group, None, raw_data=True, filters_req=request
        ):
            return response

    def dispose_load_balancer_raw(self, region, request):
        """
        Standard

        @param request:
        @return:
        """
        logger.info(f"Disposing load balancer: {request}")

        for response in self.execute(
                self.get_session_client(region=region).delete_load_balancer, None, raw_data=True, filters_req=request
        ):
            return response

    def dispose_listener_raw(self, region, request):
        """
        Standard

        @param request:
        @return:
        """
        logger.info(f"Disposing load balancer's listener: {request}")

        for response in self.execute(
                self.get_session_client(region=region).delete_listener, None, raw_data=True, filters_req=request
        ):
            return response

    def set_rule_priorities_raw(self, region, request):
        """
        Standard
        {"RulePriorities": [{"RuleArn": "string", "Priority": 123}]}
        {"RulePriorities": [{"RuleArn": "string", "Priority": 1}, {"RuleArn": "string", "Priority": 2}, {"RuleArn": "string", "Priority": 3}]}
        @param request:
        @return:
        """
        logger.info(f"Change load balancer rule priority: {request}")

        for response in self.execute(
                self.get_session_client(region=region).set_rule_priorities, "Rules", filters_req=request
        ):
            return response

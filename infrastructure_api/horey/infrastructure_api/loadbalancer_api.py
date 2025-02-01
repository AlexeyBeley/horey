"""
Standard Load balancing maintainer.

"""

from horey.h_logger import get_logger
from horey.aws_api.aws_services_entities.elbv2_load_balancer import LoadBalancer
from horey.aws_api.aws_services_entities.elbv2_target_group import ELBV2TargetGroup


logger = get_logger()


class LoadbalancerAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

    def provision(self):
        """
        Provision ECS infrastructure.

        :return:
        """

        loadbalancer = self.provision_load_balancer()
        target_group = self.provision_load_balancer_target_group()
        listener = self.provision_load_balancer_listener(loadbalancer)
        self.provision_listener_rules(listener, target_group)
        return True

    def provision_load_balancer(self):
        """
        Provision log group.

        :return:
        """

        load_balancer = LoadBalancer({})
        load_balancer.name = self.configuration.load_balancer_name
        load_balancer.scheme = self.configuration.scheme
        if load_balancer.scheme == "internet-facing":
            load_balancer.subnets = [subnet.id for subnet in self.environment_api.public_subnets]
        else:
            raise NotImplementedError(self.configuration.scheme)
        load_balancer.region = self.environment_api.region

        load_balancer.tags = self.environment_api.configuration.tags
        load_balancer.tags.append({
            "Key": "Name",
            "Value": load_balancer.name
        })
        load_balancer.type = "application"
        load_balancer.ip_address_type = "ipv4"

        security_groups = self.environment_api.get_security_groups(self.configuration.security_groups)

        load_balancer.security_groups = [security_group.id for security_group in security_groups]
        self.environment_api.aws_api.provision_load_balancer(load_balancer)
        return load_balancer

    def provision_load_balancer_target_group(self):
        """
        Provision load balancer target group.

        :return:
        """
        target_group = ELBV2TargetGroup({})
        target_group.region = self.environment_api.region
        target_group.name = self.configuration.target_group_name
        target_group.protocol = "HTTPS"
        target_group.port = 443
        target_group.vpc_id = self.environment_api.vpc.id

        target_group.health_check_protocol = "HTTPS"
        target_group.health_check_port = "traffic-port"

        target_group.health_check_enabled = True
        target_group.health_check_interval_seconds = 30
        target_group.health_check_timeout_seconds = 5
        target_group.healthy_threshold_count = 2
        target_group.unhealthy_threshold_count = 2

        target_group.health_check_path = "/health-check"
        target_group.target_type = self.configuration.target_type

        if self.configuration.target_group_targets:
            target_group.targets = self.configuration.target_group_targets

        target_group.matcher = {"HttpCode": "200"}
        target_group.tags = self.environment_api.configuration.tags
        target_group.tags.append({
            "Key": "Name",
            "Value": target_group.name
        })

        self.environment_api.aws_api.provision_load_balancer_target_group(target_group)
        return target_group

    def provision_load_balancer_listener(self, load_balancer):
        """
        Standard

        :param load_balancer:
        :return:
        """

        # listener 80
        listener_80 = LoadBalancer.Listener({})
        listener_80.protocol = "HTTP"

        listener_80.port = 80
        listener_80.default_actions = [
            {
                "Type": "redirect",
                "Order": 1,
                "RedirectConfig": {
                    "Protocol": "HTTPS",
                    "Port": "443",
                    "Host": "#{host}",
                    "Path": "/#{path}",
                    "Query": "#{query}",
                    "StatusCode": "HTTP_301"
                }
            }
        ]
        listener_80.load_balancer_arn = load_balancer.arn
        listener_80.region = self.environment_api.region

        listener_80.tags = self.environment_api.configuration.tags
        listener_80.tags.append({
            "Key": "Name",
            "Value": f"{load_balancer.name}_{listener_80.port}"
        })

        self.environment_api.aws_api.elbv2_client.provision_load_balancer_listener(listener_80)

        # listener 443
        certificates = [self.environment_api.aws_api.acm_client.get_certificate_by_domain_name(self.environment_api.region, dns) for dns in self.configuration.public_domain_names + self.configuration.unmanaged_public_domain_names]
        listener = LoadBalancer.Listener({})
        listener.protocol = "HTTPS"
        listener.ssl_policy = "ELBSecurityPolicy-TLS13-1-2-2021-06"
        listener.mutual_authentication = {"Mode": "off"}

        listener.certificates = [
            {
                "CertificateArn": cert.arn,
                "IsDefault": False
            } for cert in certificates
        ]
        listener.certificates[0]["IsDefault"] = True

        listener.port = 443
        listener.default_actions = [{"Type": "fixed-response",
                                     "FixedResponseConfig": {
                                         "StatusCode": "200",
                                         "ContentType": "text/plain",
                                         "MessageBody": "Hello world!"
                                     }}]

        listener.load_balancer_arn = load_balancer.arn
        listener.region = self.environment_api.region
        listener.tags = self.environment_api.configuration.tags
        listener.tags.append({
            "Key": "Name",
            "Value": f"{load_balancer.name}_{listener.port}"
        })

        self.environment_api.aws_api.elbv2_client.provision_load_balancer_listener(listener)

        return listener

    def provision_listener_rules(self, listener, target_group):
        """
        Provision rule for specific service.

        :return:
        """
        # todo: cleanup report reorder rules by usage
        # todo: cleanup report host rule without certificate

        current_rules = self.environment_api.aws_api.elbv2_client.get_region_rules(listener.region, listener_arn=listener.arn)

        rule = LoadBalancer.Rule({})

        current_rule = LoadBalancer.Rule({})
        current_rule.listener_arn = listener.arn
        current_rule.region = self.environment_api.region
        current_rule.tags = self.environment_api.configuration.tags
        current_rule.tags.append({
            "Key": "Name",
            "Value": self.configuration.target_group_name
        })

        if self.environment_api.aws_api.elbv2_client.update_rule_information(current_rule, region_rules=current_rules):
            rule.priority = current_rule.priority
            rule.arn = current_rule.arn
        else:
            priorities = [int(_rule.priority) for _rule in current_rules if _rule.priority != "default"]
            rule.priority = 10 if not priorities else max(priorities) + 10

        rule.listener_arn = listener.arn
        rule.region = self.environment_api.region
        rule.tags = self.environment_api.configuration.tags
        rule.tags.append({
            "Key": "Name",
            "Value": self.configuration.target_group_name
        })

        rule.priority = self.configuration.rule_priority or rule.priority
        rule.conditions = self.configuration.rule_conditions or [
            {
                "Field": "host-header",
                "HostHeaderConfig": {
                    "Values": self.configuration.public_domain_names + self.configuration.unmanaged_public_domain_names
                }
            }
        ]

        rule.actions = [
            {
                "Type": "forward",
                "TargetGroupArn": target_group.arn,
                "Order": 1,
                "ForwardConfig": {
                    "TargetGroups": [
                        {
                            "TargetGroupArn": target_group.arn,
                            "Weight": 1
                        }
                    ],
                    "TargetGroupStickinessConfig": {
                        "Enabled": False
                    }
                }
            }
        ]

        rule.tags = self.environment_api.configuration.tags
        rule.tags.append({
            "Key": "Name",
            "Value": self.configuration.target_group_name
        })
        self.environment_api.aws_api.provision_load_balancer_rule(rule)

    def get_loadbalancer(self):
        """
        Get the object.

        :return:
        """

        load_balancer = LoadBalancer({})
        load_balancer.name = self.configuration.load_balancer_name
        load_balancer.region = self.environment_api.region
        if not self.environment_api.aws_api.elbv2_client.update_load_balancer_information(load_balancer):
            raise RuntimeError(f"Was not able to find loadbalancer '{load_balancer.name }' in region '{load_balancer.region}'")
        return load_balancer

    def get_targetgroup(self):
        """
        Get the object.

        :return:
        """

        target_group = ELBV2TargetGroup({})
        target_group.region = self.environment_api.region
        target_group.name = self.configuration.target_group_name

        if not self.environment_api.aws_api.elbv2_client.update_target_group_information(target_group):
            raise RuntimeError(f"Was not able to find target group '{target_group.name }' in region '{target_group.region}'")
        return target_group

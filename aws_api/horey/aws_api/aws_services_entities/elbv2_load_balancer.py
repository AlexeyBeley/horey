"""
AWS ELB V2 handling
"""
from enum import Enum
from horey.aws_api.aws_services_entities.aws_object import AwsObject


class LoadBalancer(AwsObject):
    """
    AWS ELB V2 representation
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.dns_name = None
        self.security_groups = None
        self.listeners = []
        self.rules = []
        self.subnets = None
        self.scheme = None
        self.type = None
        self.ip_address_type = None
        self.state = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "LoadBalancerArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "LoadBalancerName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "DNSName": self.init_default_attr,
            "CanonicalHostedZoneId": self.init_default_attr,
            "CreatedTime": self.init_default_attr,
            "Scheme": self.init_default_attr,
            "VpcId": self.init_default_attr,
            "State": self.init_default_attr,
            "Type": self.init_default_attr,
            "IpAddressType": self.init_default_attr,
            "AvailabilityZones": self.init_default_attr,
            "SecurityGroups": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def _init_object_from_cache(self, dict_src):
        """
        Init the object from saved cache dict
        :param dict_src:
        :return:
        """
        options = {"listeners": self.init_listeners_from_cache}
        self._init_from_cache(dict_src, options)

    def init_listeners_from_cache(self, _, lst_src):
        """
        Init objects

        @param _:
        @param lst_src:
        @return:
        """
        for dict_listener in lst_src:
            listener = self.Listener(dict_listener, from_cache=True)
            self.listeners.append(listener)

    def get_dns_records(self):
        """
        Get dns fqdn pointing this db

        :return:
        """
        ret = [self.dns_name] if self.dns_name else []

        return ret

    def get_security_groups_endpoints(self):
        """
        Get sg ids, specified in this lb

        :return:
        """
        ret = []
        grps = self.__dict__.get("network_security_groups")
        grps = grps if grps is not None else []

        for sg in grps:
            endpoint = {
                "sg_id": sg,
                "dns": self.dns_name,
                "description": f"lb: {self.name}",
            }
            ret.append(endpoint)

        return ret

    def add_raw_listener(self, dict_src):
        """
        Add listener from raw AWS response

        @param dict_src:
        @return:
        """
        listener = self.Listener(dict_src)
        self.listeners.append(listener)

    def add_raw_rule(self, dict_src):
        """
        Add rule object from dict_src like dict

        @param dict_src:
        @return:
        """

        rule = self.Rule(dict_src)

        self.rules.append(rule)

    def get_all_addresses(self):
        """
        Get all self addresses
        :return:
        """
        return [self.dns_name]

    def generate_create_request(self):
        """
        response = client.create_load_balancer(
        Name='string',
        Subnets=[
        SecurityGroups=[
        Scheme='internet-facing'|'internal',
        Tags=[
        {
            'Key': 'string',
            'Value': 'string'
        },
        ],
        Type='application'|'network'|'gateway',
        IpAddressType='ipv4'|'dualstack',
        CustomerOwnedIpv4Pool='string'
        """

        request = {"Name": self.name, "Subnets": self.subnets}

        if self.security_groups is not None:
            request["SecurityGroups"] = self.security_groups

        request["Scheme"] = self.scheme
        request["Tags"] = self.tags
        request["Type"] = self.type
        request["IpAddressType"] = self.ip_address_type

        return request

    def update_from_raw_response(self, dict_src):
        """
        Standard

        @param dict_src:
        @return:
        """
        init_options = {
            "LoadBalancerArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "LoadBalancerName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "DNSName": self.init_default_attr,
            "CanonicalHostedZoneId": self.init_default_attr,
            "CreatedTime": self.init_default_attr,
            "Scheme": self.init_default_attr,
            "VpcId": self.init_default_attr,
            "State": self.init_default_attr,
            "Type": self.init_default_attr,
            "IpAddressType": self.init_default_attr,
            "AvailabilityZones": self.init_default_attr,
            "SecurityGroups": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_dispose_request(self):
        """
        Standard

        @return:
        """
        return {"LoadBalancerArn": self.arn}

    def get_state(self):
        """
        Used in waiter.

        @return:
        """
        # pylint: disable=unsubscriptable-object
        if self.state["Code"] == "active":
            return self.State.ACTIVE
        if self.state["Code"] == "provisioning":
            return self.State.PROVISIONING
        if self.state["Code"] == "active_impaired":
            return self.State.ACTIVE_IMPAIRED
        if self.state["Code"] == "failed":
            return self.State.FAILED

        raise NotImplementedError(self.state["Code"])

    class State(Enum):
        """
        Load balancer possible states

        """

        ACTIVE = 0
        PROVISIONING = 1
        ACTIVE_IMPAIRED = 2
        FAILED = 3

    class Listener(AwsObject):
        """
        LB Listener

        """

        def __init__(self, dict_src, from_cache=False):
            super().__init__(dict_src)
            self.ssl_policy = None
            self.certificates = []
            self.protocol = None
            self.port = None
            self.load_balancer_arn = None
            self.default_actions = None
            self.rules = []

            if from_cache:
                self._init_object_from_cache(dict_src)
                return

            self.update_from_raw_response(dict_src)

        def update_from_raw_response(self, dict_src):
            """
            Standard

            @param dict_src:
            @return:
            """

            init_options = {
                "ListenerArn": lambda x, y: self.init_default_attr(
                    x, y, formatted_name="arn"
                ),
                "LoadBalancerArn": self.init_default_attr,
                "Port": self.init_default_attr,
                "Protocol": self.init_default_attr,
                "Certificates": self.init_default_attr,
                "SslPolicy": self.init_default_attr,
                "DefaultActions": self.init_default_attr,
                "MutualAuthentication": self.init_default_attr,
            }

            self.init_attrs(dict_src, init_options)

        def _init_object_from_cache(self, dict_src):
            """
            Init the object from saved cache dict
            :param dict_src:
            :return:
            """
            options = {}
            self._init_from_cache(dict_src, options)

        def generate_create_request(self):
            """
            Standard

            @return:
            """
            request = {}

            if self.ssl_policy is not None:
                request["SslPolicy"] = self.ssl_policy

            if self.certificates:
                request["Certificates"] = self.certificates[:1]

            request["Protocol"] = self.protocol
            request["Port"] = self.port
            request["LoadBalancerArn"] = self.load_balancer_arn
            request["DefaultActions"] = self.default_actions
            return request

        def generate_add_certificate_requests(self):
            """
            Only one certificate can be added per request.

            :return:
            """

            return [{"ListenerArn": self.arn,
                     "Certificates": [cert
                                      ]} for cert in self.certificates[1:]]

        def generate_dispose_request(self):
            """
            Standard

            @return:
            """

            request = {"ListenerArn": self.arn}
            return request

    class Rule(AwsObject):
        """
        Listener rule

        """

        def __init__(self, dict_src, from_cache=False):
            super().__init__(dict_src)
            self.listener_arn = None
            self.conditions = None
            self.priority = None
            self.actions = None

            if from_cache:
                self._init_object_from_cache(dict_src)
                return

            init_options = {
                "RuleArn": lambda x, y: self.init_default_attr(
                    x, y, formatted_name="arn"
                ),
                "Priority": self.init_default_attr,
                "Conditions": self.init_default_attr,
                "Actions": self.init_default_attr,
                "IsDefault": self.init_default_attr,
            }

            self.init_attrs(dict_src, init_options)

        def _init_object_from_cache(self, dict_src):
            """
            Init the object from saved cache dict
            :param dict_src:
            :return:
            """
            options = {}
            self._init_from_cache(dict_src, options)

        def generate_create_request(self):
            """
            Standard

            @return:
            """
            request = {
                "ListenerArn": self.listener_arn,
                "Conditions": self.conditions,
                "Priority": self.priority,
                "Actions": self.actions,
                "Tags": self.tags,
            }

            return request

        def generate_dispose_request(self):
            """
            Standard

            @return:
            """

            raise NotImplementedError(
                """
            request = dict()
            request["ListenerArn"] = self.arn
            return request"""
            )

        def update_from_raw_response(self, dict_src):
            """
            Standard

            @param dict_src:
            @return:
            """
            init_options = {
                "RuleArn": lambda x, y: self.init_default_attr(
                    x, y, formatted_name="arn"
                ),
                "Priority": self.init_default_attr,
                "Conditions": self.init_default_attr,
                "Actions": self.init_default_attr,
                "IsDefault": self.init_default_attr,
            }

            self.init_attrs(dict_src, init_options)

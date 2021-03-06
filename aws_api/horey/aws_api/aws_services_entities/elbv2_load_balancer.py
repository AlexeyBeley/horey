"""
AWS ELB V2 handling
"""
import pdb
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
        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
                        "LoadBalancerArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
                        "LoadBalancerName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
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
            endpoint = {"sg_id": sg}
            endpoint["dns"] = self.dns_name
            endpoint["description"] = "lb: {}".format(self.name)
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

        request = dict()
        request["Name"] = self.name
        request["Subnets"] = self.subnets

        if self.security_groups is not None:
            request["SecurityGroups"] = self.security_groups

        request["Scheme"] = self.scheme
        request["Tags"] = self.tags
        request["Type"] = self.type
        request["IpAddressType"] = self.ip_address_type

        return request

    def get_state(self):
        if self.state["Code"] == "active":
            return self.State.ACTIVE
        elif self.state["Code"] == "provisioning":
            return self.State.PROVISIONING
        elif self.state["Code"] == "active_impaired":
            return self.State.ACTIVE_IMPAIRED
        elif self.state["Code"] == "failed":
            return self.State.FAILED
        else:
            raise NotImplementedError(self.state["Code"])

    class State(Enum):
        ACTIVE = 0
        PROVISIONING = 1
        ACTIVE_IMPAIRED = 2
        FAILED = 3

    class Listener(AwsObject):
        def __init__(self, dict_src, from_cache=False):
            super().__init__(dict_src)
            if from_cache:
                self._init_object_from_cache(dict_src)
                return

            init_options = {
                "ListenerArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
                "LoadBalancerArn": self.init_default_attr,
                "Port": self.init_default_attr,
                "Protocol": self.init_default_attr,
                "Certificates": self.init_default_attr,
                "SslPolicy": self.init_default_attr,
                "DefaultActions": self.init_default_attr,
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
            response = client.create_listener(
            LoadBalancerArn='string',
            Protocol='HTTP'|'HTTPS'|'TCP'|'TLS'|'UDP'|'TCP_UDP'|'GENEVE',
            Port=123,
            SslPolicy='string',
            Certificates=[
                {
                'CertificateArn': 'string',
                'IsDefault': True|False
            },
        ],
            DefaultActions=[
        {
            'Type': 'forward'|'authenticate-oidc'|'authenticate-cognito'|'redirect'|'fixed-response',
            'TargetGroupArn': 'string',
            'AuthenticateOidcConfig': {
                'Issuer': 'string',
                'AuthorizationEndpoint': 'string',
                'TokenEndpoint': 'string',
                'UserInfoEndpoint': 'string',
                'ClientId': 'string',
                'ClientSecret': 'string',
                'SessionCookieName': 'string',
                'Scope': 'string',
                'SessionTimeout': 123,
                'AuthenticationRequestExtraParams': {
                    'string': 'string'
                },
                'OnUnauthenticatedRequest': 'deny'|'allow'|'authenticate',
                'UseExistingClientSecret': True|False
            },
            'AuthenticateCognitoConfig': {
                'UserPoolArn': 'string',
                'UserPoolClientId': 'string',
                'UserPoolDomain': 'string',
                'SessionCookieName': 'string',
                'Scope': 'string',
                'SessionTimeout': 123,
                'AuthenticationRequestExtraParams': {
                    'string': 'string'
                },
                'OnUnauthenticatedRequest': 'deny'|'allow'|'authenticate'
            },
            'Order': 123,
            'RedirectConfig': {
                'Protocol': 'string',
                'Port': 'string',
                'Host': 'string',
                'Path': 'string',
                'Query': 'string',
                'StatusCode': 'HTTP_301'|'HTTP_302'
            },
            'FixedResponseConfig': {
                'MessageBody': 'string',
                'StatusCode': 'string',
                'ContentType': 'string'
            },
            'ForwardConfig': {
                'TargetGroups': [
                    {
                        'TargetGroupArn': 'string',
                        'Weight': 123
                    },
                ],
                'TargetGroupStickinessConfig': {
                    'Enabled': True|False,
                    'DurationSeconds': 123
                }
            }
        },
    ],
    AlpnPolicy=[
        'string',
    ],
    Tags=[

)
            """

            request = dict()
            request["Tags"] = self.tags

            request["Protocol"] = self.protocol
            request["Port"] = self.port
            request["LoadBalancerArn"] = self.load_balancer_arn
            request["DefaultActions"] = self.default_actions
            return request



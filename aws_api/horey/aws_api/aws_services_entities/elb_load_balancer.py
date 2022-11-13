"""
Classic Loadbalancer module.
"""

from horey.network.dns import DNS
from horey.aws_api.aws_services_entities.aws_object import AwsObject
import pdb


class ClassicLoadBalancer(AwsObject):
    """
    Classic Loadbalancer representation.
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
            "LoadBalancerName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "DNSName": self.init_default_attr,
            "CanonicalHostedZoneNameID": self.init_default_attr,
            "ListenerDescriptions": self.init_listener_descriptions,
            "Policies": self.init_default_attr,
            "BackendServerDescriptions": self.init_default_attr,
            "Subnets": self.init_default_attr,
            "VPCId": self.init_default_attr,
            "Instances": self.init_default_attr,
            "HealthCheck": self.init_default_attr,
            "SourceSecurityGroup": self.init_default_attr,
            "CreatedTime": self.init_default_attr,
            "SecurityGroups": self.init_default_attr,
            "Scheme": self.init_default_attr,
            "AvailabilityZones": self.init_default_attr,
            "CanonicalHostedZoneName": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def init_listener_descriptions(self, _, lst_src):
        for dict_src in lst_src:
            listener = self.Listener(dict_src)
            self.listeners.append(listener)

    def _init_object_from_cache(self, dict_src):
        """
        Init self from cached dict
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
        Get self dns record
        :return:
        """
        ret = [self.dns_name] if self.dns_name else []

        return ret

    def get_all_addresses(self):
        """
        Get all addresses.
        :return:
        """
        return [DNS(self.dns_name)]

    class Listener(AwsObject):
        def __init__(self, dict_src, from_cache=False):
            super().__init__(dict_src)
            if from_cache:
                self._init_object_from_cache(dict_src)
                return

            init_options = {
                "Listener": self.init_listener,
                "PolicyNames": self.init_default_attr,
            }

            self.init_attrs(dict_src, init_options)

        def init_listener(self, _, dict_src):
            init_options = {
                "Protocol": self.init_default_attr,
                "LoadBalancerPort": lambda x, y: self.init_default_attr(
                    x, y, formatted_name="port"
                ),
                "InstanceProtocol": self.init_default_attr,
                "InstancePort": self.init_default_attr,
                "SSLCertificateId": self.init_default_attr,
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

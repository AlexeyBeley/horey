"""
AWS ELB V2 target group
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


# pylint: disable=too-many-instance-attributes
class ELBV2TargetGroup(AwsObject):
    """
    Class representing AWS ELB V2 target group
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        self.health_check_path = None
        self.target_health = None
        self.targets = None
        self.arn = None

        self.protocol = None
        self.port = None
        self.vpc_id = None

        self.health_check_protocol = None
        self.health_check_port = None

        self.health_check_enabled = None
        self.health_check_interval_seconds = None
        self.health_check_timeout_seconds = None
        self.healthy_threshold_count = None
        self.unhealthy_threshold_count = None
        self.target_type = None

        init_options = {
            "TargetGroupArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "TargetGroupName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "Protocol": self.init_default_attr,
            "Port": self.init_default_attr,
            "VpcId": self.init_default_attr,
            "HealthCheckProtocol": self.init_default_attr,
            "HealthCheckPort": self.init_default_attr,
            "HealthCheckEnabled": self.init_default_attr,
            "HealthCheckIntervalSeconds": self.init_default_attr,
            "HealthCheckTimeoutSeconds": self.init_default_attr,
            "HealthyThresholdCount": self.init_default_attr,
            "UnhealthyThresholdCount": self.init_default_attr,
            "HealthCheckPath": self.init_default_attr,
            "Matcher": self.init_default_attr,
            "LoadBalancerArns": self.init_default_attr,
            "TargetType": self.init_default_attr,
            "ProtocolVersion": self.init_default_attr,
            "IpAddressType": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def _init_object_from_cache(self, dict_src):
        """
        Init the object from saved cache dict
        :param dict_src:
        :return:
        """
        options = {
        }
        self._init_from_cache(dict_src, options)

    def update_target_health(self, dict_src):
        """
        Update extra information as required
        :param dict_src:
        :return:
        """
        self.target_health = dict_src

    def generate_create_request(self):
        """
        Generate create request dict

        @return:
        """

        request = {"Name": self.name,
                   "Protocol": self.protocol,
                   "Port": self.port,
                   "VpcId": self.vpc_id,
                   "HealthCheckEnabled": self.health_check_enabled,
                   "HealthCheckIntervalSeconds": self.health_check_interval_seconds,
                   "HealthCheckTimeoutSeconds": self.health_check_timeout_seconds,
                   "HealthyThresholdCount": self.healthy_threshold_count,
                   "UnhealthyThresholdCount": self.unhealthy_threshold_count,
                   "TargetType": self.target_type}

        if self.health_check_path is not None:
            request["HealthCheckPath"] = self.health_check_path

        if self.health_check_protocol is not None:
            request["HealthCheckProtocol"] = self.health_check_protocol

        if self.health_check_port is not None:
            request["HealthCheckPort"] = self.health_check_port

        request["Tags"] = self.tags

        return request

    def generate_register_targets_request(self):
        """
        Trivial.

        @return:
        """

        if self.targets is None:
            return None

        if self.arn is None:
            raise ValueError(f"Target group '{self.name}' arn was not set")

        request = {"TargetGroupArn": self.arn, "Targets": self.targets}

        return request

    def generate_dispose_request(self):
        """
        Trivial

        @return:
        """

        return {"TargetGroupArn": self.arn}

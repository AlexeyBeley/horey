"""
AWS ELB V2 target group
"""
from horey.aws_api.aws_services_entities.aws_object import AwsObject


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
        client.create_target_group(
        Name='string',
        Protocol='HTTP'|'HTTPS'|'TCP'|'TLS'|'UDP'|'TCP_UDP'|'GENEVE',
        ProtocolVersion='string',
        Port=123,
        VpcId='string',
        HealthCheckProtocol='HTTP'|'HTTPS'|'TCP'|'TLS'|'UDP'|'TCP_UDP'|'GENEVE',
        HealthCheckPort='string',
        HealthCheckEnabled=True|False,
        HealthCheckPath='string',
        HealthCheckIntervalSeconds=123,
        HealthCheckTimeoutSeconds=123,
        HealthyThresholdCount=123,
        UnhealthyThresholdCount=123,
        Matcher={
            'HttpCode': 'string',
            'GrpcCode': 'string'
        },
        TargetType='instance'|'ip'|'lambda',
        Tags=[
        {
            'Key': 'string',
            'Value': 'string'
        },
    ]
)
        """
        request = dict()
        request["Name"] = self.name
        request["Protocol"] = self.protocol
        request["Port"] = self.port
        request["VpcId"] = self.vpc_id

        request["HealthCheckProtocol"] = self.health_check_protocol
        request["HealthCheckPort"] = self.health_check_port

        request["HealthCheckEnabled"] = self.health_check_enabled
        request["HealthCheckIntervalSeconds"] = self.health_check_interval_seconds
        request["HealthCheckTimeoutSeconds"] = self.health_check_timeout_seconds
        request["HealthyThresholdCount"] = self.healthy_threshold_count
        request["UnhealthyThresholdCount"] = self.unhealthy_threshold_count
        request["TargetType"] = self.target_type
        if self.health_check_path is not None:
            request["HealthCheckPath"] = self.health_check_path
        request["Tags"] = self.tags

        return request

    def generate_register_targets_request(self):
        if self.targets is None:
            return

        request = dict()

        if self.arn is None:
            raise ValueError(f"Target group '{self.name}' arn is not set")

        request["TargetGroupArn"] = self.arn
        request["Targets"] = self.targets

        return request

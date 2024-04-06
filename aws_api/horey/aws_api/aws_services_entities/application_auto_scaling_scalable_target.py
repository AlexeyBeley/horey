"""
AWS ApplicationAutoScalingScalableTarget representation
"""
from horey.aws_api.aws_services_entities.aws_object import AwsObject


class ApplicationAutoScalingScalableTarget(AwsObject):
    """
    AWS ApplicationAutoScalingScalableTarget class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None
        self.target_tracking_configuration = None
        self.service_namespace = None
        self.resource_id = None
        self.scalable_dimension = None
        self.min_capacity = None
        self.max_capacity = None
        self.role_arn = None
        self.suspended_state = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "MinCapacity": self.init_default_attr,
            "MaxCapacity": self.init_default_attr,
            "RoleARN": self.init_default_attr,
            "SuspendedState": self.init_default_attr,
            "ServiceNamespace": self.init_default_attr,
            "ResourceId": self.init_default_attr,
            "ScalableDimension": self.init_default_attr,
            "CreationTime": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def _init_object_from_cache(self, dict_src):
        """
        Init from cache
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def update_from_raw_response(self, dict_src):
        """
        Standard
        :param dict_src:
        :return:
        """
        init_options = {}
        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard

        :return:
        """
        request = {"ServiceNamespace": self.service_namespace, "ResourceId": self.resource_id,
                   "ScalableDimension": self.scalable_dimension}

        if self.min_capacity is not None:
            request["MinCapacity"] = self.min_capacity

        if self.max_capacity is not None:
            request["MaxCapacity"] = self.max_capacity

        if self.role_arn is not None:
            request["RoleARN"] = self.role_arn

        if self.suspended_state is not None:
            request["SuspendedState"] = self.suspended_state

        return request

    def generate_dispose_request(self):
        """
        Standard

        :return:
        """
        raise NotImplementedError("""
        request = dict()
        request["ServiceNamespace"] = self.service_namespace
        request["ResourceId"] = self.resource_id
        request["ScalableDimension"] = self.scalable_dimension
        return request""")

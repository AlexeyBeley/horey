"""
Module to handle AWS RDS param group
"""
from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class RDSDBClusterParameterGroup(AwsObject):
    """
    Class representing RDS DB param group
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None
        self.db_parameter_group_family = None
        self.description = None
        self.parameters = []

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        self.update_from_raw_response(dict_src)

    def _init_object_from_cache(self, dict_src):
        """
        Init the object from saved cache dict
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

        init_options = {
            "DBClusterParameterGroupName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "DBClusterParameterGroupArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "DBParameterGroupFamily": self.init_default_attr,
            "Description": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard.

        :return:
        """
        request = {"DBParameterGroupFamily": self.db_parameter_group_family, "DBClusterParameterGroupName": self.name,
                   "Description": self.description, "Tags": self.tags}

        return request

    def generate_modify_db_cluster_parameter_group_request(self, desired_param_group):
        """
        Standard.

        :return:
        """
        if len(self.parameters) != len({param["ParameterName"] for param in self.parameters}):
            raise RuntimeError(f"Expect single name in source param list: {self.name}")

        desired_params_by_name = {}
        for param in desired_param_group.parameters:
            if param.get("Source") != "user":
                raise ValueError(f"Only source = User supported: {param} in {self.name}")
            desired_params_by_name[param["ParameterName"]] = param
        if len(desired_params_by_name) != len(desired_param_group.parameters):
            raise RuntimeError(f"Expect single name in desired param list: {self.name}")

        # self.parameters = [] means new deployment, no values yet.
        desired_changes = [] if self.parameters else desired_param_group.parameters

        for current_param_value in self.parameters:
            if desired_param_value := desired_params_by_name.get(current_param_value["ParameterName"]):
                if desired_param_value != current_param_value:
                    desired_changes.append(desired_param_value)

            elif current_param_value.get("Source") not in ["engine-default", "system"]:
                raise ValueError(f"Unknown param source {current_param_value}")

        if not desired_changes:
            return None
        request = {
                   "DBClusterParameterGroupName": self.name,
                   "Parameters": desired_changes}

        return request

    @property
    def region(self):
        """
        Standard.

        :return:
        """
        if self._region is not None:
            return self._region

        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value

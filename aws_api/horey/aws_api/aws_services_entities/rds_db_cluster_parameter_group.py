"""
Module to handle AWS RDS instances
"""
from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class RDSDBClusterParameterGroup(AwsObject):
    """
    Class representing RDS DB instance
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None
        self.parameters = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "DBClusterParameterGroupName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "DBClusterParameterGroupArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "DBParameterGroupFamily": self.init_default_attr,
            "Description": self.init_default_attr,
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

    def update_from_raw_response(self, dict_src):
        init_options = {
            "DBClusterParameterGroupName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "DBClusterParameterGroupArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "DBParameterGroupFamily": self.init_default_attr,
            "Description": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        request = dict()
        request["DBParameterGroupFamily"] = self.db_parameter_group_family
        request["DBClusterParameterGroupName"] = self.name
        request["Description"] = self.description
        request["Tags"] = self.tags

        return request

    @property
    def region(self):
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

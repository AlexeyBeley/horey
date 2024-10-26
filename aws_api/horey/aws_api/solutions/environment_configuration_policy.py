"""
AWS Environment config

"""
from copy import deepcopy

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring


class EnvironmentConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """
    
    def __init__(self):
        super().__init__()
        self._region = None
        self._vpc_name = None
        self._tags = None
        self._vpc_primary_subnet = None
        self._availability_zones_count = None
        self._subnet_mask_length = None
        self._subnet_name_template = None
        self._internet_gateway_name = None
        self._route_table_name_template = None

    @property
    def route_table_name_template(self):
        if self._route_table_name_template is None:
            raise self.UndefinedValueError("route_table_name_template")
        return self._route_table_name_template

    @route_table_name_template.setter
    def route_table_name_template(self, value):
        self._route_table_name_template = value

    @property
    def internet_gateway_name(self):
        if self._internet_gateway_name is None:
            raise self.UndefinedValueError("internet_gateway_name")
        return self._internet_gateway_name

    @internet_gateway_name.setter
    def internet_gateway_name(self, value):
        self._internet_gateway_name = value

    @property
    def subnet_name_template(self):
        if self._subnet_name_template is None:
            raise self.UndefinedValueError("subnet_name_template")
        return self._subnet_name_template

    @subnet_name_template.setter
    def subnet_name_template(self, value):
        self._subnet_name_template = value

    @property
    def subnet_mask_length(self):
        if self._subnet_mask_length is None:
            raise self.UndefinedValueError("subnet_mask_length")
        return self._subnet_mask_length

    @subnet_mask_length.setter
    def subnet_mask_length(self, value):
        self._subnet_mask_length = value

    @property
    def availability_zones_count(self):
        if self._availability_zones_count is None:
            raise self.UndefinedValueError("availability_zones_count")
        return self._availability_zones_count

    @availability_zones_count.setter
    def availability_zones_count(self, value):
        self._availability_zones_count = value

    @property
    def vpc_primary_subnet(self):
        if self._vpc_primary_subnet is None:
            raise self.UndefinedValueError("vpc_primary_subnet")
        return self._vpc_primary_subnet

    @vpc_primary_subnet.setter
    def vpc_primary_subnet(self, value):
        self._vpc_primary_subnet = value

    @property
    def tags(self):
        if self._tags is None:
            raise self.UndefinedValueError("tags")
        return deepcopy(self._tags)

    @tags.setter
    def tags(self, value):
        self._tags = value

    @property
    def vpc_name(self):
        if self._vpc_name is None:
            raise self.UndefinedValueError("vpc_name")
        return self._vpc_name

    @vpc_name.setter
    def vpc_name(self, value):
        self._vpc_name = value
    
    @property
    def region(self):
        if self._region is None:
            raise self.UndefinedValueError("region")
        return self._region

    @region.setter
    def region(self, value):
        self._region = value

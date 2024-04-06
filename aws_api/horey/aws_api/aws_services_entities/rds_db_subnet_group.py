"""
Module to handle AWS RDS instances
"""
from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class RDSDBSubnetGroup(AwsObject):
    """
    Class representing RDS DB instance
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None
        self.db_subnet_group_description = None
        self.subnet_ids = None

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
        Standard.

        :param dict_src:
        :return:
        """
        init_options = {
            "DBSubnetGroupName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "DBSubnetGroupArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "DBSubnetGroupDescription": self.init_default_attr,
            "VpcId": self.init_default_attr,
            "SubnetGroupStatus": self.init_default_attr,
            "Subnets": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard.

        :return:
        """
        request = {"DBSubnetGroupName": self.name, "DBSubnetGroupDescription": self.db_subnet_group_description,
                   "SubnetIds": self.subnet_ids, "Tags": self.tags}

        return request

    def generate_modify_request(self, desired_state):
        """
        Modify the subnet group.

        :param desired_state:
        :return:
        """

        if self.name != desired_state.name:
            raise ValueError(f"{self.name=} {desired_state.name=}")

        if self.db_subnet_group_description == desired_state.db_subnet_group_description and \
                self.subnet_ids == desired_state.subnet_ids:
            return None

        return {"DBSubnetGroupName": self.name,
                "DBSubnetGroupDescription": desired_state.db_subnet_group_description,
                "SubnetIds": desired_state.subnet_ids,
                }

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

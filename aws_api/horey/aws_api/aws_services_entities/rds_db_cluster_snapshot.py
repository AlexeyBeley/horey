"""
Module to handle AWS RDS instances
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class RDSDBClusterSnapshot(AwsObject):
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
            "DBClusterSnapshotIdentifier": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "DBClusterSnapshotArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "AvailabilityZones": self.init_default_attr,
            "DBClusterIdentifier": self.init_default_attr,
            "SnapshotCreateTime": self.init_default_attr,
            "Engine": self.init_default_attr,
            "EngineMode": self.init_default_attr,
            "AllocatedStorage": self.init_default_attr,
            "Status": self.init_default_attr,
            "Port": self.init_default_attr,
            "VpcId": self.init_default_attr,
            "ClusterCreateTime": self.init_default_attr,
            "MasterUsername": self.init_default_attr,
            "EngineVersion": self.init_default_attr,
            "LicenseModel": self.init_default_attr,
            "SnapshotType": self.init_default_attr,
            "PercentProgress": self.init_default_attr,
            "StorageEncrypted": self.init_default_attr,
            "KmsKeyId": self.init_default_attr,
            "IAMDatabaseAuthenticationEnabled": self.init_default_attr,
            "TagList": self.init_default_attr,
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
            "DBClusterSnapshotIdentifier": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "DBClusterSnapshotArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "AvailabilityZones": self.init_default_attr,
            "DBClusterIdentifier": self.init_default_attr,
            "SnapshotCreateTime": self.init_default_attr,
            "Engine": self.init_default_attr,
            "EngineMode": self.init_default_attr,
            "AllocatedStorage": self.init_default_attr,
            "Status": self.init_default_attr,
            "Port": self.init_default_attr,
            "VpcId": self.init_default_attr,
            "ClusterCreateTime": self.init_default_attr,
            "MasterUsername": self.init_default_attr,
            "EngineVersion": self.init_default_attr,
            "LicenseModel": self.init_default_attr,
            "SnapshotType": self.init_default_attr,
            "PercentProgress": self.init_default_attr,
            "StorageEncrypted": self.init_default_attr,
            "KmsKeyId": self.init_default_attr,
            "IAMDatabaseAuthenticationEnabled": self.init_default_attr,
            "TagList": self.init_default_attr,
            "SourceDBClusterSnapshotArn": self.init_default_attr
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        request = dict()
        pdb.set_trace()
        request["Tags"] = self.tags

        return request

    def generate_copy_request(self, dst_cluster_snapshot):
        request = dict()
        request["SourceDBClusterSnapshotIdentifier"] = self.arn
        request["TargetDBClusterSnapshotIdentifier"] = dst_cluster_snapshot.id
        request["KmsKeyId"] = dst_cluster_snapshot.kms_key_id
        request["CopyTags"] = False

        request["Tags"] = dst_cluster_snapshot.tags
        request["Tags"].append(self.get_src_snapshot_id_tag())

        request["SourceRegion"] = self.region.region_mark
        return request

    def get_src_snapshot_id_tag(self):
        return {
            "Key": "src_snapshot_id",
            "Value": self.arn
        }

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

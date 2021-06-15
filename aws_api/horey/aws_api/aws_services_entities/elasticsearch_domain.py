"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class ElasticsearchDomain(AwsObject):
    """
    Elasticsearch domain class
    """
    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.instances = []

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "DomainId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "DomainName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "ARN": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "Created": self.init_default_attr,
            "Deleted": self.init_default_attr,
            "Endpoint": self.init_default_attr,
            "Processing": self.init_default_attr,
            "UpgradeProcessing": self.init_default_attr,
            "ElasticsearchVersion": self.init_default_attr,
            "ElasticsearchClusterConfig": self.init_default_attr,
            "EBSOptions": self.init_default_attr,
            "AccessPolicies": self.init_default_attr,
            "SnapshotOptions": self.init_default_attr,
            "CognitoOptions": self.init_default_attr,
            "EncryptionAtRestOptions": self.init_default_attr,
            "NodeToNodeEncryptionOptions": self.init_default_attr,
            "AdvancedOptions": self.init_default_attr,
            "ServiceSoftwareOptions": self.init_default_attr,
            "DomainEndpointOptions": self.init_default_attr,
            "AdvancedSecurityOptions": self.init_default_attr,
            "AutoTuneOptions": self.init_default_attr,
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

    def update_value_from_raw_response(self, raw_value):
        pdb.set_trace()

"""
AWS Opensearch domain representation
"""
from enum import Enum
from horey.aws_api.aws_services_entities.aws_object import AwsObject

# pylint: disable = too-many-instance-attributes


class ElasticsearchDomain(AwsObject):
    """
    Elasticsearch domain class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.advanced_options = None
        self.node_to_node_encryption_options = None
        self.elasticsearch_cluster_config = None
        self.ebs_options = None
        self.access_policies = None
        self.cognito_options = None
        self.encryption_at_rest_options = None
        self.elasticsearch_version = None
        self.snapshot_options = None
        self.vpc_options = None
        self.log_publishing_options = None
        self.domain_endpoint_options = None
        self.advanced_security_options = None
        self.auto_tune_options = None
        self.domain_processing_status = "NONE"

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        self.update_from_raw_response(dict_src)

    def update_from_raw_response(self, dict_src):
        """
        Standard.

        :param dict_src:
        :return:
        """

        init_options = {
            "DomainId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "DomainName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
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
            "ChangeProgressDetails": self.init_default_attr,
            "DomainProcessingStatus": self.init_default_attr,
            "ModifyingProperties": self.init_default_attr
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

    def get_status(self):
        """
        Standard.

        :return:
        """
        if self.domain_processing_status is None:
            raise self.UndefinedStatusError("domain_processing_status was not set")
        for enum_value in self.State.__members__.values():
            if enum_value.value == self.domain_processing_status:
                return enum_value
        raise KeyError(f"Has no state configured for value: '{self.domain_processing_status=}'")

    class State(Enum):
        """
        Domain state
        """
        CREATING = "Creating"
        ACTIVE = "Active"
        MODIFYING = "Modifying"
        UPDATING_ENGINE_VERSION = "UpgradingEngineVersion"
        UPDATING_SERVICE_SOFTWARE = "UpdatingServiceSoftware"
        ISOLATED = "Isolated"
        DELETING = "Deleting"
        NONE = "NONE"

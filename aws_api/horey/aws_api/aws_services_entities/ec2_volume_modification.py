"""
Volume modification
"""
from enum import Enum
from horey.aws_api.aws_services_entities.aws_object import AwsObject


class EC2VolumeModification(AwsObject):
    """
    Main class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.progress = None
        self.modification_state = None
        self.volume_id = None

        if from_cache:
            self._init_instance_from_cache(dict_src)
            return

        init_options = {
            "ModificationState": self.init_default_attr,
            "TargetSize": self.init_default_attr,
            "TargetIops": self.init_default_attr,
            "TargetVolumeType": self.init_default_attr,
            "TargetMultiAttachEnabled": self.init_default_attr,
            "OriginalSize": self.init_default_attr,
            "OriginalIops": self.init_default_attr,
            "OriginalVolumeType": self.init_default_attr,
            "OriginalMultiAttachEnabled": self.init_default_attr,
            "Progress": self.init_default_attr,
            "StartTime": self.init_default_attr,
            "VolumeId": self.init_default_attr,
            "EndTime": self.init_default_attr,
            "TargetThroughput": self.init_default_attr,
            "OriginalThroughput": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

        tag_name = self.get_tagname("Name")
        self.name = tag_name if tag_name else self.id

    def update_from_raw_response(self, dict_src):
        """
        Standard.

        :param dict_src:
        :return:
        """
        init_options = {
            "ModificationState": self.init_default_attr,
            "TargetSize": self.init_default_attr,
            "TargetIops": self.init_default_attr,
            "TargetVolumeType": self.init_default_attr,
            "TargetMultiAttachEnabled": self.init_default_attr,
            "OriginalSize": self.init_default_attr,
            "OriginalIops": self.init_default_attr,
            "OriginalVolumeType": self.init_default_attr,
            "OriginalMultiAttachEnabled": self.init_default_attr,
            "Progress": self.init_default_attr,
            "StartTime": self.init_default_attr,
            "VolumeId": self.init_default_attr,
            "EndTime": self.init_default_attr,
            "TargetThroughput": self.init_default_attr,
            "OriginalThroughput": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def _init_instance_from_cache(self, dict_src):
        """
        Init self from preserved dict.
        :param dict_src:
        :return:
        """
        options = {}

        self._init_from_cache(dict_src, options)

    def get_status(self):
        """
        Return status.

        """
        mapping = {key.lower().replace("_", "-"): value for key, value in self.State.__members__.items()}
        return mapping[self.modification_state]

    class State(Enum):
        """
        Volume modification state.
        'modifying'|'optimizing'|'completed'|'failed'

        """

        MODIFYING = 0
        OPTIMIZING = 1
        COMPLETED = 2
        FAILED = 3

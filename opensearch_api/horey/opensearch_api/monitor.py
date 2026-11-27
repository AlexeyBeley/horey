"""
Index pattern.

"""
import copy

from horey.opensearch_api.opensearch_object import OpensearchObject

# pylint: disable= too-many-instance-attributes


class Monitor(OpensearchObject):
    """
    Main class.
    """

    def __init__(self, dict_src):
        self.id = None
        self.type = None
        self.schema_version = None
        self.name = None
        self.monitor_type = None
        self.enabled = None
        self.enabled_time = None
        self.schedule = None
        self.inputs = None
        self.triggers = None
        self.last_update_time = None
        self.data_sources = None
        self.owner = None
        self.is_child = None
        self.shards = None
        self.is_distributed = None
        self.delete_query_index_in_every_run = None
        self.should_create_single_alert_for_findings = None

        super().__init__(dict_src)

    def generate_create_request(self):
        """
        Generate dictionary to POST request.

        :return:
        """

        ret = {"type": "monitor",
               "name": self.name,
               "enabled": self.enabled,
               "schedule": self.schedule,
               "inputs": self.inputs,
               "triggers": self.triggers}
        return ret

    def generate_update_request(self, desired_monitor):
        """
        Generate dictionary to POST request.

        :return:
        """

        for attr_name in ["type",
                          "enabled",
                          "schedule",
                          "inputs",
                          "triggers"]:
            if getattr(desired_monitor, attr_name) != getattr(self, attr_name):
                return desired_monitor.generate_create_request()

        return None

    def copy(self):
        """
        Copy self.

        :return:
        """

        ret = Monitor(copy.deepcopy(self.dict_src))
        ret.id = self.id
        return ret

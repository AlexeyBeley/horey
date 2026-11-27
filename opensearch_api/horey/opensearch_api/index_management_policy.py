"""
Index State Management (ISM) policy.
https://opensearch.org/docs/latest/im-plugin/ism/api/

"""
import copy
import re

from horey.opensearch_api.opensearch_object import OpensearchObject

# pylint: disable= too-many-instance-attributes


class IndexManagementPolicy(OpensearchObject):
    """
    Main class.
    dict_src is the "policy" part of the ISM API response/request.
    """

    DAYS_IN_MONTH = 30  # ISM min_index_age has no month unit ("m" means minutes).
    DEFAULT_PRIORITY = 100

    def __init__(self, dict_src):
        self.id = None
        self.seq_no = None
        self.primary_term = None

        self.policy_id = None
        self.description = None
        self.default_state = None
        self.states = None
        self.ism_template = None
        self.error_notification = None
        self.schema_version = None
        self.last_updated_time = None

        super().__init__(dict_src)

    @classmethod
    def init_from_retention(cls, policy_id, month_retention, ism_template_format, priority=DEFAULT_PRIORITY):
        """
        Policy keeps indices in the "hot" state and deletes them after month_retention months.
        Applied automatically to new indices matching ism_template_format.

        :param policy_id:
        :param month_retention:
        :param ism_template_format: Index pattern, e.g. "my-project-*"
        :param priority: ISM template priority
        :return:
        """

        if not re.fullmatch(r"[A-Za-z0-9._-]+", policy_id):
            raise ValueError("policy_id must contain only letters, digits, '.', '_' or '-'")
        if not isinstance(month_retention, int) or isinstance(month_retention, bool) or month_retention < 1:
            raise ValueError("month_retention must be a positive integer")

        dict_src = {
            "policy_id": policy_id,
            "description": f"Delete indices after {month_retention} month(s)",
            "default_state": "hot",
            "states": [
                {
                    "name": "hot",
                    "actions": [],
                    "transitions": [
                        {"state_name": "delete",
                         "conditions": {"min_index_age": f"{month_retention * cls.DAYS_IN_MONTH}d"}}
                    ]
                },
                {
                    "name": "delete",
                    "actions": [{"delete": {}}],
                    "transitions": []
                }
            ],
            "ism_template": [
                {"index_patterns": [ism_template_format], "priority": priority}
            ]
        }

        return cls(dict_src)

    @property
    def name(self):
        """
        Policy name - the same as the policy id. Used as the key in the API.

        :return:
        """

        return self.policy_id

    def generate_create_request(self):
        """
        Generate dictionary to PUT request.

        :return:
        """

        policy = {"description": self.description,
                  "default_state": self.default_state,
                  "states": self.states,
                  "ism_template": self.ism_template}

        if self.error_notification is not None:
            policy["error_notification"] = self.error_notification

        return {"policy": policy}

    def generate_update_request(self, desired_policy):
        """
        Generate dictionary to PUT request. None if there is nothing to update.

        :return:
        """

        for attr_name in ["description",
                          "default_state",
                          "states",
                          "ism_template"]:
            if self._normalize(attr_name, getattr(desired_policy, attr_name)) != \
                    self._normalize(attr_name, getattr(self, attr_name)):
                return desired_policy.generate_create_request()

        return None

    @staticmethod
    def _normalize(attr_name, value):
        """
        Remove fields added by the server so the current and the desired policies are comparable.

        :param attr_name:
        :param value:
        :return:
        """

        value = copy.deepcopy(value)
        if attr_name == "states":
            for state in value or []:
                for action in state.get("actions", []):
                    action.pop("retry", None)
        elif attr_name == "ism_template":
            if isinstance(value, dict):
                value = [value]
            for template in value or []:
                template.pop("last_updated_time", None)

        return value

    def copy(self):
        """
        Copy self.

        :return:
        """

        ret = IndexManagementPolicy(copy.deepcopy(self.dict_src))
        ret.id = self.id
        ret.seq_no = self.seq_no
        ret.primary_term = self.primary_term
        return ret

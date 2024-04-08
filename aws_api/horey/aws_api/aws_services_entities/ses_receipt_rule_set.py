"""
AWS SESReceiptRuleSet representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class SESReceiptRuleSet(AwsObject):
    """
    AWS SESReceiptRuleSet class
    """

    def __init__(self, dict_src, from_cache=False):
        self.created_timestamp = None
        self.rules = []
        super().__init__(dict_src)

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        self.update_from_raw_response(dict_src)

    def _init_object_from_cache(self, dict_src):
        """
        Init from cache

        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def update_from_raw_response(self, dict_src):
        """
        dict received from server.

        for key_name in dict_src: print(f"self.{self.format_attr_name(key_name)} = None")

        :param dict_src:
        :return:
        """

        init_options = {
            "Name": self.init_default_attr,
            "CreatedTimestamp": self.init_default_attr,
            "Rules": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_change_rules_requests(self, desired_state):
        """
        Standard

        :param desired_state:
        :return: Reorder request, Create requestS, Delete requestS.
        """
        reorder_request = []
        create_requests = []

        # create
        self_names = [rule["Name"] for rule in self.rules]
        for rule_index, rule in enumerate(desired_state.rules):
            if rule["Name"] not in self_names:
                request = {"RuleSetName": self.name, "Rule": rule}
                if rule_index != 0:
                    request["After"] = desired_state.rules[rule_index - 1]["Name"]
                create_requests.append(request)

        # delete
        desired_names = [rule["Name"] for rule in desired_state.rules]
        delete_requests = [{"RuleSetName": self.name, "RuleName": name} for name in self_names if name not in desired_names]

        self_without_changes = [name for name in self_names if name in desired_names]
        desired_without_changes = [name for name in desired_names if name in self_names]
        if self_without_changes != desired_without_changes:
            reorder_request = {"RuleSetName": self.name, "RuleNames": desired_without_changes}

        return reorder_request, create_requests, delete_requests

    def generate_update_receipt_rule_requests(self, desired_state):
        """
        Standard

        :param desired_state:
        :return: Update requestS
        """
        requests = []
        desired_names = [rule["Name"] for rule in desired_state.rules]
        for rule in self.rules:
            try:
                desired_index = desired_names.index(rule["Name"])
            except ValueError:
                continue

            if rule != desired_state.rules[desired_index]:
                requests.append({"RuleSetName": self.name, "Rule": desired_state.rules[desired_index]})

        return requests

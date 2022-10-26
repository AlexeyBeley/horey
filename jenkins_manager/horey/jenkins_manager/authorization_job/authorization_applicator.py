"""
Authorization Job

"""

import json
from horey.h_logger import get_logger

logger = get_logger()


class AuthorizationApplicator:
    """
    Main class.

    """

    def __init__(self):
        self.rules = []

    def append_rule(self, rule):
        """
        Add rule at the bottom.

        @param rule:
        @return:
        """

        self.rules.append(rule)

    def serialize(self, file_path):
        """
        Serialize rules to file

        @param file_path:
        @return:
        """
        rules = [rule.convert_to_dict() for rule in self.rules]
        with open(file_path, "w", encoding="utf-8") as file_handler:
            json.dump(rules, file_handler, indent=4)

    def deserialize(self, file_path):
        """
        Deserialize rules from file

        @param file_path:
        @return:
        """

        with open(file_path, encoding="utf-8") as file_handler:
            raw_rules = json.load(file_handler)

        self.rules = [self.Rule(rule) for rule in raw_rules]

    def authorize(self, request):
        """
        Check the request against all rules.

        @param request:
        @return:
        """

        for rule in self.rules:
            if rule.authorize(request):
                return True
        return False

    class Request:
        """
        Request for jenkins job run.

        """
        SPECIAL_CHARS_MAP = {"<": "horey_special_char_replacement_less",
                             ">": "horey_special_char_replacement_more"}

        def __init__(self, str_src):

            for special_char, replacement in self.SPECIAL_CHARS_MAP.items():
                str_src = str_src.replace(replacement, special_char)

            dict_src = json.loads(str_src)
            self.dict_src = dict_src
            self.user_identity = dict_src.get("user_identity")
            self.job_name = dict_src.get("job_name")
            self.parameters = dict_src.get("parameters")

        def serialize(self):
            """
            Serialize the request.

            @return:
            """
            ret = json.dumps(self.convert_to_dict())

            for special_char, replacement in self.SPECIAL_CHARS_MAP.items():
                ret = ret.replace(special_char, replacement)

            return ret

        def convert_to_dict(self):
            """
            Serialize

            @return:
            """

            return {"user_identity": self.user_identity,
                    "job_name": self.job_name,
                    "parameters": self.parameters}

    class Rule:
        """
        Authorization rule.

        """

        def __init__(self, dict_src):
            self.job_name = dict_src["job_name"]
            if "*" in self.job_name and self.job_name != "*":
                raise NotImplementedError("REGex not yet supported, only *")

            self.user_identity = dict_src["user_identity"]
            self.parameters_restrictions = [AuthorizationApplicator.ParameterRestriction(param_dict_src) for
                                            param_dict_src in dict_src["parameters_restrictions"]]

        def convert_to_dict(self):
            """
            Serialize

            @return:
            """
            return {"job_name": self.job_name,
                    "user_identity": self.user_identity,
                    "parameters_restrictions": [parameters_restriction.convert_to_dict() for parameters_restriction in
                                                self.parameters_restrictions]}

        def authorize(self, request):
            """
            Authorize request against the rule.

            @param request:
            @return:
            """

            if self.user_identity != request.user_identity:
                return False

            # pylint: disable= consider-using-in
            if request.job_name != self.job_name and self.job_name != "*":
                return False

            authorized_params = []

            for restriction in self.parameters_restrictions:
                for param_var, param_val in request.parameters.items():
                    if restriction.authorize(param_var, param_val):
                        if param_var not in authorized_params:
                            authorized_params.append(param_var)
                        break
                else:
                    if restriction.required:
                        return False
            if len(request.parameters) != len(authorized_params):
                return False

            return True

    class ParameterRestriction:
        """
        Restrict parameter values.
        """

        def __init__(self, dict_src):
            self.dict_src = dict_src
            self.name = dict_src["name"]
            self.value = dict_src["value"]
            self.required = dict_src["required"]

        def convert_to_dict(self):
            """
            Serialize

            @return:
            """

            return {"name": self.name,
                    "value": self.value,
                    "required": self.required}

        def authorize(self, var, val):
            """
            Authorize variable/value match.

            @param var:
            @param val:
            @return:
            """

            return self.name == var and self.value == val

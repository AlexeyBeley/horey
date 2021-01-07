"""
Module handling AWS Iam Policy object
"""
from enum import Enum
from aws_object import AwsObject


class IamPolicy(AwsObject):
    """
    Class representing AWS Iam Policy object
    """
    def __init__(self, dict_src, from_cache=False):
        """
        Init with boto3 dict
        :param dict_src:
        """
        self.document = None

        super().__init__(dict_src, from_cache=from_cache)
        if from_cache:
            self._init_policy_from_cashe(dict_src)
            return

        init_options = {
                        "PolicyId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
                        "Path": self.init_default_attr,
                        "PolicyName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
                        "Arn": self.init_default_attr,
                        "CreateDate": self.init_default_attr,
                        "DefaultVersionId": self.init_default_attr,
                        "AttachmentCount": self.init_default_attr,
                        "PermissionsBoundaryUsageCount": self.init_default_attr,
                        "IsAttachable": self.init_default_attr,
                        "UpdateDate": self.init_default_attr}

        self.init_attrs(dict_src, init_options)

    def _init_policy_from_cashe(self, dict_src):
        """
        Init the object from saved cache dict
        :param dict_src:
        :return:
        """
        options = {"create_date": self.init_date_attr_from_formatted_string,
                   "update_date":  self.init_date_attr_from_formatted_string,
                   "document": self.init_document_from_cache,
                   }

        self._init_from_cache(dict_src, options)

    def init_document_from_cache(self, _, value):
        """
        Init the document from saved cache dict.
        :param _:
        :param value:
        :return:
        """
        self.document = IamPolicy.Document(value, from_cache=True)

    def update_statements(self, dict_src):
        """
        Update statement from AWS API dict
        :param dict_src:
        :return:
        """
        init_options = {"CreateDate": self.init_default_attr,
                        "IsDefaultVersion": self.init_default_attr,
                        "VersionId": self.init_default_attr,
                        "Document": self.init_document
                        }

        self.init_attrs(dict_src, init_options)

    def init_document(self, _, value):
        """
        Init document. Value received from AWS API
        :param _:
        :param value:
        :return:
        """
        document = IamPolicy.Document(value)
        self.init_default_attr("document", document)

    class Document(AwsObject):
        """
        Class representing AWS Policy Document object.
        """
        def __init__(self, dict_src, from_cache=False):
            self.statements = []

            super(IamPolicy.Document, self).__init__(dict_src, from_cache=from_cache)

            if from_cache:
                self.init_document_from_cache(dict_src)
                return

            init_options = {"Version": self.init_default_attr,
                            "Statement": self.init_statement,
                            "Id": self.init_default_attr,
                            }

            self.init_attrs(dict_src, init_options)

        def init_document_from_cache(self, dict_src):
            """
            Init previously cached dict.
            :param dict_src:
            :return:
            """
            options = {"statements": lambda key, value: self.init_statement(key, value, from_cache=True),
                       }

            self._init_from_cache(dict_src, options)

        def init_statement(self, _, lst_src, from_cache=False):
            """
            Init single statement.
            :param key:
            :param lst_src:
            :param from_cache:
            :return:
            """
            if not isinstance(lst_src, list):
                lst_src = [lst_src]

            for dict_src in lst_src:
                statement = IamPolicy.Document.Statement(dict_src, from_cache=from_cache)

                self.statements.append(statement)

        class Statement(AwsObject):
            """
            Class representing single AWS Policy Document Statement object.
            """

            def __init__(self, dict_src, from_cache=False):
                self.effect = None
                self.action = {}
                self.not_action = {}
                self.resource = None
                self.not_resource = None
                super(IamPolicy.Document.Statement, self).__init__(dict_src, from_cache=from_cache)

                if from_cache:
                    self.init_statement_from_cache(dict_src)
                    return

                init_options = {"Sid": self.init_default_attr,
                                "Effect": self.init_effect,
                                "Action": self.init_action,
                                "Resource": self.init_resource,
                                "Condition": self.init_default_attr,
                                "NotAction": self.init_action,
                                "NotResource": self.init_resource,
                                }

                self.init_attrs(dict_src, init_options)

            def init_statement_from_cache(self, dict_src):
                """
                Init previously saved cache dict.
                :param dict_src:
                :return:
                """
                options = {"effect": self.init_effect}
                self._init_from_cache(dict_src, options)

            def init_action(self, attr_name, value):
                """
                Init action. Value received from AWS API
                :param attr_name:
                :param value:
                :return:
                """
                if isinstance(value, str):
                    value = [value]
                action = getattr(self, self.format_attr_name(attr_name))

                if not isinstance(value, list):
                    raise ValueError(value)

                for str_action in value:
                    if ":" not in str_action:
                        if str_action == "*":
                            action[str_action] = str_action
                            continue

                        raise NotImplementedError("Not yet implemented, replaced pdb.set_trace")

                    service_name, action_value = str_action.split(":", 1)

                    if service_name not in action:
                        action[service_name] = []
                    action[service_name].append(action_value)

            def init_resource(self, key, value):
                """
                Init resource. Value received from AWS API.
                :param key:
                :param value:
                :return:
                """
                if isinstance(value, str):
                    value = [value]
                elif isinstance(value, list):
                    pass
                else:
                    raise TypeError(type(value))

                self.init_default_attr(key, value)

            def init_effect(self, key, value):
                """
                Init effect. Value received from AWS API.
                :param key:
                :param value:
                :return:
                """
                for enum_attr in self.Effects:
                    if enum_attr.value == value:
                        self.init_default_attr(key, enum_attr)
                        return
                raise ValueError(value)

            # pylint: disable=R0911
            @staticmethod
            def tail_position_regexes_intersect(str_1, str_2):
                """
                Find intersection for tail position *.

                :param str_1:
                :param str_2:
                :return:
                """
                i = 0
                while i < min(len(str_1), len(str_2)):
                    if str_1[i] != str_2[i]:
                        return None
                    i += 1

                if len(str_1) == len(str_2):
                    return str_1

                if i == len(str_1):
                    # "asd*", "asd12456"
                    if str_1[i-1] == "*":
                        return str_2
                    # "asd" "asd*"
                    if str_2[i] == "*":
                        return str_1
                elif i == len(str_2):
                    if str_2[i-1] == "*":
                        return str_1
                    if str_1[i] == "*":
                        return str_2
                else:
                    raise ValueError(str_1, str_2)

                return None

            def intersect_resource_value_regex(self, resource_1, resource_2):
                """
                Regex? What is regex? Split them!

                :param resource_1:
                :param resource_2:
                :return:
                """
                lst_ret = []
                lst_arn_1 = resource_1.split(":")
                lst_arn_2 = resource_2.split(":")
                i = 0

                while i < min(len(lst_arn_1), len(lst_arn_2)):
                    if lst_arn_1[i] == lst_arn_2[i]:
                        lst_ret.append(lst_arn_1[i])
                    elif lst_arn_1[i] == "*":
                        lst_ret.append(lst_arn_2[i])
                    elif lst_arn_2[i] == "*":
                        lst_ret.append(lst_arn_1[i])
                    elif "*" in lst_arn_1[i] or "*" in lst_arn_2[i]:
                        ret =self.tail_position_regexes_intersect(lst_arn_1[i], lst_arn_2[i])
                        if ret is None:
                            return []
                        lst_ret.append(ret)
                    i += 1

                return [":".join(lst_ret)]

            def intersect_resource(self, other):
                """
                Find intersection of two resources.
                :param other:
                :return:
                """
                if other.resource is None or self.resource is None:
                    return []
                lst_ret = []

                # pylint: disable=E1133
                for self_resource in self.resource:
                    if self_resource == "*":
                        # pylint: disable=R1721
                        return [other_resource for other_resource in other.resource]

                    for other_resource in other.resource:
                        if other_resource == "*":
                            # pylint: disable=R1721
                            return [self_resource for self_resource in self.resource]

                        if "*" in self_resource or "*" in other_resource:
                            lst_ret += self.intersect_resource_value_regex(self_resource, other_resource)
                        elif self_resource == other_resource:
                            lst_ret.append(self_resource)

                return lst_ret

            @staticmethod
            def check_service_intersect(service_name_1, service_name_2):
                """
                Check if there is an intersection in 2 resource names

                :param service_name_1:
                :param service_name_2:
                :return:
                """
                if service_name_1 == "*" or service_name_2 == "*":
                    return True

                if service_name_1 == service_name_2:
                    return True

                if "*" not in service_name_1 and "*" not in service_name_2:
                    return False

                raise NotImplementedError("Not yet implemented, replaced pdb.set_trace")

            @staticmethod
            def check_action_intersect(action_1, action_2):
                """
                Check if there is an intersection in 2 actions

                :param action_1:
                :param action_2:
                :return:
                """
                if action_1 == action_2:
                    return True
                raise NotImplementedError("Not yet implemented, replaced pdb.set_trace")

            def action_values_intersect(self, action_1, action_2):
                """
                Check if there is an intersection in 2 actions' values
                :param action_1:
                :param action_2:
                :return:
                """
                if action_1 == "*":
                    return [action_2]

                if action_2 == "*":
                    return [action_1]

                lst_ret = []
                if "*" in action_1 or "*" in action_2:
                    ret = self.tail_position_regexes_intersect(action_1, action_2)
                    if ret is not None:
                        return [ret]
                    return []

                if action_1 == action_2:
                    return [action_1]
                return lst_ret

            def action_lists_values_intersect(self, actions_1, actions_2):
                """
                Find 2 actions' lists intersection

                :param actions_1:
                :param actions_2:
                :return:
                """
                lst_ret = []
                for action_1 in actions_1:
                    for action_2 in actions_2:
                        lst_ret += self.action_values_intersect(action_1, action_2)
                return lst_ret

            def intersect_action(self, other):
                """
                Find an intersection of 2 actions.
                :param other:
                :return:
                """
                lst_ret = []
                for self_service, self_action in self.action.items():
                    for other_service, other_action in other.action.items():
                        if self.check_service_intersect(self_service, other_service):
                            lst_ret += self.action_lists_values_intersect(self_action, other_action)

                return lst_ret

            class Effects(Enum):
                """
                Possible values for effect statement.
                """
                ALLOW = "Allow"
                DENY = "Deny"

            class Resource:
                """
                Class representing a resource record
                ARN built by this specs:
                https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html
                """
                INIT_PARTS = {1: "partition",
                              2: "service",
                              3: "region",
                              4: "account_id",
                              5: "resource_type",
                              6: "resource_id",
                              7: "resource_data_0",  # I want to vomit :(
                              8: "resource_data_1"
                              }

                def __init__(self, str_src):
                    self.str_src = str_src
                    self.init_from_regex_arn(str_src)

                def init_from_regex_arn(self, arn):
                    """
                    #aws s3api list-objects --bucket test-roles

                    arn:partition:service:region:account-id:resource-id
                    arn:partition:service:region:account-id:resource-type/resource-id
                    arn:partition:service:region:account-id:resource-type:resource-id

                    You know what an asshole is? This is the guy which documents specific ARN structure and then
                    uses another one in AWS CLoudWatch LogGroups:Streams This is why this function is an ugly piece of SH.
                    :param arn:
                    :return:
                    """

                    lst_arn = arn.split(":")
                    if lst_arn[0] != "arn":
                        if lst_arn[0] != "*":
                            raise ValueError(lst_arn)

                    part_index = 1
                    while part_index < len(lst_arn):
                        arn_part = lst_arn[part_index]

                        if "*" in arn_part:
                            if lst_arn[part_index] == "*":
                                setattr(self, self.INIT_PARTS[part_index], arn_part)
                            else:
                                raise NotImplementedError("Not yet implemented, replaced pdb.set_trace")
                        else:
                            setattr(self, self.INIT_PARTS[part_index], arn_part)

                        part_index += 1

                    while part_index < 9:
                        setattr(self, self.INIT_PARTS[part_index], "*")
                        part_index += 1

                def intersect(self, other):
                    """
                    Return the intersection of 2 resources.
                    :param other:
                    :return:
                    """
                    lst_ret = []
                    for value in self.INIT_PARTS.values():
                        lst_part = self._intersect_arn_part(getattr(self, value), getattr(other, value))
                        if len(lst_part) == 0:
                            return []
                        if len(lst_part) > 1:
                            raise NotImplementedError(lst_part)
                        lst_ret.append(lst_part[0])
                    raise NotImplementedError("Not yet implemented, replaced pdb.set_trace")

                @staticmethod
                def _intersect_arn_part(self_part, other_part):
                    """
                    Find the intersection of arn_part:330

                    :param self_part:
                    :param other_part:
                    :return:
                    """
                    if other_part == "*":
                        return [self_part]

                    if self_part == "*":
                        return [other_part]

                    if "*" not in self_part and "*" not in other_part:
                        return [self_part] if self_part == other_part else None

                    raise NotImplementedError("Not yet implemented, replaced pdb.set_trace")

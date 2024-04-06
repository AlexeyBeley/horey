"""
Module handling IAM role object
"""
import json

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.aws_services_entities.iam_policy import IamPolicy
from horey.aws_api.base_entities.region import Region


class IamRole(AwsObject):
    """Class representing AWS IAM Role"""

    def __init__(self, dict_src, from_cache=False):
        """
        Init Iam user with boto3 dict

        :param dict_src:
        """
        self.managed_policies_arns = []
        self.inline_policies = []
        self.role_last_used_time = None
        self.role_last_used_region = None
        self.assume_role_policy_document = None
        self.max_session_duration = None
        self.description = None
        self.path = ""

        super().__init__(dict_src)

        if from_cache:
            self._init_iam_role_from_cache(dict_src)
            return

        self.update_from_raw_response(dict_src)

    def _init_iam_role_from_cache(self, dict_src):
        """
        Init the object from saved cache dict
        :param dict_src:
        :return:
        """
        options = {"inline_policies": self.init_inline_policies_from_cache}

        self._init_from_cache(dict_src, options)

    def init_inline_policies_from_cache(self, _, lst_src):
        """
        Standard.

        :param _:
        :param lst_src:
        :return:
        """

        self.inline_policies = [IamPolicy(dict_src, from_cache=True) for dict_src in lst_src]

    def init_role_last_used_attr(self, _, dict_src):
        """
        Init RoleLastUsed - split to time and region

        @param _:
        @param dict_src:
        @return:
        """
        if not dict_src:
            return
        for key in dict_src:
            if key == "LastUsedDate":
                self.role_last_used_time = dict_src.get(key)
                continue
            if key == "Region":
                self.role_last_used_region = Region.get_region(dict_src.get(key))
                continue

            raise NotImplementedError(key)

    def add_policy(self):
        """
        Add single AWS Iam Policy.

        :return:
        """
        raise DeprecationWarning("use attached_policies or inline_policies")

    def init_assume_role_policy_document(self, key, value):
        """
        Init assume role from AWS API response.

        :param key:
        :param value:
        :return:
        """

        raise NotImplementedError("Not yet implemented, replaced set_trace")

    def update_from_raw_response(self, dict_src):
        """
        Update self from raw server response.

        @param dict_src:
        @return:
        """

        init_options = {
            "RoleId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "Path": self.init_default_attr,
            "RoleName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "Arn": self.init_default_attr,
            "CreateDate": self.init_default_attr,
            "AssumeRolePolicyDocument": self.init_default_attr,
            "Description": self.init_default_attr,
            "MaxSessionDuration": self.init_default_attr,
            "RoleLastUsed": self.init_role_last_used_attr,
            "Tags": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Generate create request.

        @return:
        """

        request = {
            "RoleName": self.name,
            "AssumeRolePolicyDocument": json.dumps(self.assume_role_policy_document) if isinstance(
                self.assume_role_policy_document, dict) else self.assume_role_policy_document,
            "MaxSessionDuration": self.max_session_duration,
        }
        if self.path == "":
            raise ValueError(f"Creating role {self.name} without 'path' set")
        self.extend_request_with_required_parameters(request, ["Tags", "Path"])
        self.extend_request_with_optional_parameters(request, ["Description"])
        return request

    def generate_managed_policies_requests(self, desired_role):
        """
        Attach and detach managed policies request.

        @return:
        """

        attach = [
            {"PolicyArn": arn, "RoleName": self.name} for arn in desired_role.managed_policies_arns
            if arn not in self.managed_policies_arns
        ]

        detach = [
            {"PolicyArn": arn, "RoleName": self.name} for arn in self.managed_policies_arns
            if arn not in desired_role.managed_policies_arns
        ]

        return attach, detach

    def generate_inline_policies_requests(self, desired_role):
        """
        Inline policies.

        :param desired_role:
        :return:
        """

        self_inline = {policy.name: policy.document for policy in self.inline_policies}
        desired_inline = {policy.name: policy.document for policy in desired_role.inline_policies}
        put_requests = []
        for policy_name, dict_document in desired_inline.items():
            if policy_name not in self_inline or self_inline[policy_name] != dict_document:
                put_requests.append(
                    {"PolicyName": policy_name, "RoleName": self.name, "PolicyDocument": json.dumps(dict_document)})

        delete_requests = [{"PolicyName": policy_name, "RoleName": self.name} for policy_name in self_inline if
                           policy_name not in desired_inline]

        return put_requests, delete_requests

    def generate_update_assume_role_policy_request(self, desired_role):
        """
        Assume role policy.

        :param desired_role:
        :return:
        """

        dict_self_assume_role_policy_document = self.assume_role_policy_document if isinstance(
            self.assume_role_policy_document, dict) \
            else json.loads(self.assume_role_policy_document)

        dict_desired_assume_role_policy_document = desired_role.assume_role_policy_document if isinstance(
            desired_role.assume_role_policy_document, dict) \
            else json.loads(desired_role.assume_role_policy_document)

        if dict_self_assume_role_policy_document != dict_desired_assume_role_policy_document:
            return {"RoleName": self.name,
                    "PolicyDocument": desired_role.assume_role_policy_document}

        return None

    def get_assume_arn_masks(self):
        """
        Get all arn masks allowed to assume this role.

        :return:
        """
        ret = []
        for statement in self.assume_role_policy_document["Statement"]:
            if statement["Effect"] != "Allow":
                continue
            if statement["Action"] != "sts:AssumeRole":
                continue

            for principal_type, principal_value in statement["Principal"].items():
                if principal_type == "Service":
                    continue

                if principal_type != "AWS":
                    raise ValueError(f"Unsupported principal type code: {principal_type}")

                if isinstance(principal_value, str):
                    ret.append(principal_value)
                    continue

                if isinstance(principal_value, list):
                    ret += principal_value
                    continue

                raise ValueError(f"Unsupported principal value: {principal_value}")
        return ret

"""
AWS Lambda representation
"""
import json

import sys
import os
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class AWSLambda(AwsObject):
    """
    Lambda representation class
    """
    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.vpc_config = None
        self._region = None
        self.code = None
        self.policy = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "FunctionName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "FunctionArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "Runtime": self.init_default_attr,
            "Role": self.init_default_attr,
            "Handler": self.init_default_attr,
            "CodeSize": self.init_default_attr,
            "Description": self.init_default_attr,
            "Timeout": self.init_default_attr,
            "MemorySize": self.init_default_attr,
            "LastModified": lambda attr_name, value: self.init_date_attr_from_formatted_string(attr_name, self.format_last_modified_time(value)),
            "CodeSha256": self.init_default_attr,
            "Version": self.init_default_attr,
            "VpcConfig": self.init_default_attr,
            "Environment": self.init_default_attr,
            "TracingConfig": self.init_default_attr,
            "RevisionId": self.init_default_attr,
            "Layers": self.init_default_attr,
            "DeadLetterConfig": self.init_default_attr,
            "KMSKeyArn": self.init_default_attr,
            "PackageType": self.init_default_attr,
                        }

        self.init_attrs(dict_src, init_options)

    @staticmethod
    def format_last_modified_time(str_value):
        """
        Pretty print of last modified time
        :param str_value:
        :return:
        """
        _date, _time = str_value.split("T")
        _time, _micro_and_zone = _time.split(".")
        _micro_and_zone = "000" + _micro_and_zone
        return f"{_date} {_time}.{_micro_and_zone}"

    def _init_object_from_cache(self, dict_src):
        """
        Init from cache
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def get_assinged_security_group_ids(self):
        lst_ret = []
        if self.vpc_config is not None:
            return self.vpc_config["SecurityGroupIds"]
        return lst_ret

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

    def update_from_raw_response(self, dict_src):
        init_options = {
            "FunctionName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "FunctionArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "Runtime": self.init_default_attr,
            "Role": self.init_default_attr,
            "Handler": self.init_default_attr,
            "CodeSize": self.init_default_attr,
            "Description": self.init_default_attr,
            "Timeout": self.init_default_attr,
            "MemorySize": self.init_default_attr,
            "LastModified": lambda attr_name, value: self.init_date_attr_from_formatted_string(attr_name, self.format_last_modified_time(value)),
            "CodeSha256": self.init_default_attr,
            "Version": self.init_default_attr,
            "VpcConfig": self.init_default_attr,
            "Environment": self.init_default_attr,
            "TracingConfig": self.init_default_attr,
            "RevisionId": self.init_default_attr,
            "Layers": self.init_default_attr,
            "DeadLetterConfig": self.init_default_attr,
            "KMSKeyArn": self.init_default_attr,
            "PackageType": self.init_default_attr,
            "State": self.init_default_attr,
            "LastUpdateStatus": self.init_default_attr,
            "StateReason": self.init_default_attr,
            "StateReasonCode": self.init_default_attr,
                        }

        self.init_attrs(dict_src, init_options)

    def update_from_raw_get_function_response(self, dict_src):
        self.update_from_raw_response(dict_src["Configuration"])
        self.tags = dict_src["Tags"]
        self.code = dict_src["Code"]

    def update_policy_from_get_policy_raw_response(self, dict_src):
        self.policy = dict_src["Policy"]

    def generate_create_request(self):
        request = dict()
        request["Code"] = self.code
        request["FunctionName"] = self.name
        request["Role"] = self.role
        request["Handler"] = self.handler
        request["Runtime"] = self.runtime
        request["Tags"] = self.tags

        return request

    def generate_update_function_code_request(self, desired_code):
        request = dict()

        if desired_code is None:
            return
        pdb.set_trace()
        request["ZipFile"] = desired_code.get("ZipFile")
        request["FunctionName"] = self.name
        request["Publish"] = True
        request["DryRun"] = False
        request["RevisionId"] = self.revision_id

        return request

    def generate_add_permission_request(self, desired_policy):
        """
        response = client.add_permission(
        Action='lambda:InvokeFunction',
        FunctionName='my-function',
        Principal='s3.amazonaws.com',
        SourceAccount='123456789012',
        SourceArn='arn:aws:s3:::my-bucket-1xpuxmplzrlbh/*',
        StatementId='s3',
        )
        @return:
        """
        if desired_policy is None:
            return

        if len(desired_policy["Statement"]) != 1:
            raise NotImplementedError(desired_policy["Statement"])

        desired_policy["Statement"][0]["Resource"] = self.arn

        if self.policy is not None:
            self_policy = json.loads(self.policy)
            if len(self_policy["Statement"]) != 1:
                raise NotImplementedError(self_policy["Statement"])

            for key, value in desired_policy["Statement"][0].items():
                if desired_policy["Statement"][0][key] != self_policy["Statement"][0][key]:
                    break
            else:
                return
        pdb.set_trace()
        request = dict()

        request["FunctionName"] = self.name
        request["StatementId"] = desired_policy["Statement"][0]["Sid"]
        request["Action"] = desired_policy["Statement"][0]["Action"]
        request["Principal"] = desired_policy["Statement"][0]["Principal"]["Service"]
        request["SourceArn"] = desired_policy["Statement"][0]["Condition"]["ArnLike"]["AWS:SourceArn"]

        return request

    def update_from_raw_add_permission_response(self, dict_src):
        pdb.set_trace()
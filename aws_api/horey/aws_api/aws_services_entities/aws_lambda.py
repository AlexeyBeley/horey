"""
AWS Lambda representation
"""
import json
from enum import Enum

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region
from horey.h_logger import get_logger

logger = get_logger()


# pylint: disable=too-many-instance-attributes
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
        self._arn = None
        self.environment = None
        self.timeout = None
        self.memory_size = None
        self.ephemeral_storage = None
        self.role = None
        self.handler = None
        self.runtime = None
        self.last_update_status = None
        self.revision_id = None
        self.state = None
        self.reserved_concurrent_executions = None
        self.package_type = None
        self.file_system_configs = None
        self.request_key_to_attribute_mapping = {"FunctionArn": "arn", "FunctionName": "name"}

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        self.update_from_raw_response(dict_src)

    @property
    def arn(self):
        """
        Object arn.

        @return:
        """

        return self._arn

    @arn.setter
    def arn(self, value):
        """
        Set self arn. If arn ends with version_id, eliminate the version id and save the arn as vanilla.

        @param value:
        @return:
        """

        if value.endswith(self.name):
            self._arn = value
        else:
            self._arn = value[: value.rfind(":")]

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
        """
        Return security group ids.

        @return:
        """

        # pylint: disable=unsubscriptable-object
        lst_ret = []
        if self.vpc_config is not None:
            return self.vpc_config["SecurityGroupIds"]
        return lst_ret

    @property
    def region(self):
        """
        If region was not set explicitly find it out.

        @return:
        """

        if self._region is not None:
            return self._region

        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        """
        Region setter.

        @param value:
        @return:
        """

        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value

    def update_from_raw_response(self, dict_src):
        """
        Update from raw server response.

        @param dict_src:
        @return:
        """
        init_options = {
            "FunctionName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "FunctionArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "Runtime": self.init_default_attr,
            "Role": self.init_default_attr,
            "Handler": self.init_default_attr,
            "CodeSize": self.init_default_attr,
            "Description": self.init_default_attr,
            "Timeout": self.init_default_attr,
            "MemorySize": self.init_default_attr,
            "LastModified": lambda attr_name, value: self.init_date_attr_from_formatted_string(
                attr_name, self.format_last_modified_time(value)
            ),
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
            "Architectures": self.init_default_attr,
            "LastUpdateStatusReason": self.init_default_attr,
            "LastUpdateStatusReasonCode": self.init_default_attr,
            "EphemeralStorage": self.init_default_attr,
            "SnapStart": self.init_default_attr,
            "RuntimeVersionConfig": self.init_default_attr,
            "LoggingConfig": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def update_from_raw_get_function_response(self, dict_src):
        """
        Update from raw server response.

        @param dict_src:
        @return:
        """

        self.update_from_raw_response(dict_src["Configuration"])
        self.tags = dict_src["Tags"]
        self.code = dict_src["Code"]

    def update_policy_from_get_policy_raw_response(self, dict_src):
        """
        Update policy from raw server response.

        @param dict_src:
        @return:
        """

        self.policy = dict_src["Policy"]

    def generate_create_request(self):
        """
        Generate create new lambda request.

        @return:
        """

        if self.code.get("ImageUri") is None:
            if self.runtime is None or self.handler is None:
                raise RuntimeError("Either image or zip should be used")
        elif self.runtime is not None or self.handler is not None:
            raise RuntimeError("Either image or zip should be used")

        request = self.generate_request(["Code", "FunctionName", "Role", "Tags"],
                                     optional=["Tags", "Runtime", "Handler", "PackageType", "Timeout",
                                               "MemorySize", "EphemeralStorage", "VpcConfig", "Environment",
                                               "FileSystemConfigs"],
                                     request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)

        if self.code.get("ImageUri") is not None:
            request["PackageType"] = "Image"
        return request

    def generate_update_function_configuration_request(self, desired_lambda):
        """
        Generate Update configuration request to make this lambda look like desired one.
        must be one of: FunctionName, Role, Handler, Description, Timeout, MemorySize, VpcConfig, Environment, Runtime, DeadLetterConfig, KMSKeyArn, TracingConfig, RevisionId, Layers, FileSystemConfigs, ImageConfig

        @param desired_lambda:
        @return:
        """

        attr_names = [
            "Role",
            "Handler",
            "Description",
            "Timeout",
            "MemorySize",
            "VpcConfig",
            "Environment",
            "Runtime",
            "DeadLetterConfig",
            "KMSKeyArn",
            "TracingConfig",
            "RevisionId",
            "Layers",
            "FileSystemConfigs",
            "ImageConfig"
        ]
        request = {"FunctionName": self.name}
        for attr_name in attr_names:
            formatted_attr_name = self.format_attr_name(attr_name)
            try:
                desired_attr_value = getattr(desired_lambda, formatted_attr_name)
            except AttributeError:
                continue

            if desired_attr_value is None:
                continue

            self_attr_value = getattr(self, formatted_attr_name)
            if self_attr_value != desired_attr_value:
                logger.info(
                    f"Updating lambda '{self.name}' config '{formatted_attr_name}' value from"
                    f" '{self_attr_value}' to '{desired_attr_value}'"
                )
                request[attr_name] = desired_attr_value

        if self.package_type == "Image":
            try:
                del request["Handler"]
            except KeyError:
                pass

            try:
                del request["Runtime"]
            except KeyError:
                pass

        return request

    def generate_update_function_concurrency_requests(self, desired_aws_lambda):
        """
        Generate updating request.
        :param desired_aws_lambda:
        :return:
        """

        if desired_aws_lambda.reserved_concurrent_executions is None:
            return None, {"FunctionName": self.name}

        if desired_aws_lambda.reserved_concurrent_executions != self.reserved_concurrent_executions:
            return {"FunctionName": self.name,
                    "ReservedConcurrentExecutions": desired_aws_lambda.reserved_concurrent_executions}, None

        return None, None

    def generate_update_function_code_request(self, desired_aws_lambda):
        """
        Generate update function request.

        @param desired_aws_lambda:
        @return:
        """

        request = {}

        if desired_aws_lambda.code is None:
            return None

        request["FunctionName"] = self.name
        request["Publish"] = True
        request["DryRun"] = False
        request["RevisionId"] = self.revision_id

        if desired_aws_lambda.code.get("ZipFile") is not None:
            request["ZipFile"] = desired_aws_lambda.code.get("ZipFile")
            return request

        if desired_aws_lambda.code.get("S3Bucket") is not None:
            request["S3Bucket"] = desired_aws_lambda.code.get("S3Bucket")
            request["S3Key"] = desired_aws_lambda.code.get("S3Key")
            return request

        if desired_aws_lambda.code.get("ImageUri") is not None:
            request["ImageUri"] = desired_aws_lambda.code.get("ImageUri")
            return request

        raise RuntimeError(self.name)

    # pylint: disable = too-many-branches
    def generate_modify_permissions_requests(self, desired_aws_lambda):
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

        if desired_aws_lambda.policy is None:
            return [], []

        for statement in desired_aws_lambda.policy["Statement"]:
            statement["Resource"] = self.arn

        if self.policy is None:
            requests = []
            for desired_statement in desired_aws_lambda.policy["Statement"]:
                request = {
                    "FunctionName": self.name,
                    "StatementId": desired_statement["Sid"],
                    "Action": desired_statement["Action"],
                    "Principal": desired_statement["Principal"]["Service"]
                }

                if "Condition" in desired_statement:
                    if "ArnLike" in desired_statement["Condition"]:
                        request["SourceArn"] = desired_statement["Condition"]["ArnLike"]["AWS:SourceArn"]
                    elif "StringEquals" in desired_statement["Condition"]:
                        request["SourceAccount"] = desired_statement["Condition"]["StringEquals"][
                            "AWS:SourceAccount"]
                    else:
                        raise NotImplementedError(desired_statement["Condition"])

                requests.append(request)
            return requests, []

        add_permissions = []
        remove_permissions = []
        self_policy = json.loads(self.policy)
        # pylint: disable=undefined-loop-variable
        for self_statement in self_policy["Statement"]:
            for desired_statement in desired_aws_lambda.policy["Statement"]:
                if desired_statement["Sid"] == self_statement["Sid"]:
                    if desired_statement != self_statement:
                        request = {
                            "FunctionName": self.name,
                            "StatementId": desired_statement["Sid"],
                            "Action": desired_statement["Action"],
                            "Principal": desired_statement["Principal"]["Service"]
                        }
                        if "Condition" in desired_statement:
                            request["SourceArn"] = desired_statement["Condition"]["ArnLike"]["AWS:SourceArn"]

                        add_permissions.append(request)
                        request = {
                            "FunctionName": self.name,
                            "StatementId": self_statement["Sid"],
                        }
                        remove_permissions.append(request)
                    break
            else:
                request = {
                    "FunctionName": self.name,
                    "StatementId": self_statement["Sid"],
                }
                remove_permissions.append(request)
        for desired_statement in desired_aws_lambda.policy["Statement"]:
            for self_statement in self_policy["Statement"]:
                if desired_statement["Sid"] == self_statement["Sid"]:
                    break
            else:
                request = {
                    "FunctionName": self.name,
                    "StatementId": desired_statement["Sid"],
                    "Action": desired_statement["Action"],
                    "Principal": desired_statement["Principal"]["Service"]
                }
                if "Condition" in desired_statement:
                    if "ArnLike" in desired_statement["Condition"]:
                        request["SourceArn"] = desired_statement["Condition"]["ArnLike"]["AWS:SourceArn"]
                    elif "StringEquals" in desired_statement["Condition"]:
                        request["SourceAccount"] = desired_statement["Condition"]["StringEquals"]["AWS:SourceAccount"]
                    else:
                        raise NotImplementedError(desired_statement["Condition"])

                add_permissions.append(request)
        return add_permissions, remove_permissions

    def generate_add_permissions_requests(self):
        """
        Generate add permission request.

        @return:
        """

        ret = []
        for desired_statement in self.policy["Statement"]:
            request = {
                "FunctionName": self.name,
                "StatementId": desired_statement["Sid"],
                "Action": desired_statement["Action"],
                "Principal": desired_statement["Principal"]["Service"]
            }
            if "Condition" in desired_statement:
                if "ArnLike" in desired_statement["Condition"]:
                    request["SourceArn"] = desired_statement["Condition"]["ArnLike"]["AWS:SourceArn"]
                elif "StringEquals" in desired_statement["Condition"]:
                    request["SourceAccount"] = desired_statement["Condition"]["StringEquals"]["AWS:SourceAccount"]
                else:
                    raise NotImplementedError(desired_statement["Condition"])

            ret.append(request)
        return ret

    def get_status(self):
        """
        Enum of possible statuses below.

        @return:
        """
        if self.last_update_status is None:
            raise self.UndefinedStatusError()
        return {
            enum_value.value: enum_value
            for _, enum_value in self.Status.__members__.items()
        }[self.last_update_status]

    class Status(Enum):
        """
        Lambda status enum.

        """

        SUCCESSFUL = "Successful"
        INPROGRESS = "InProgress"
        FAILED = "Failed"

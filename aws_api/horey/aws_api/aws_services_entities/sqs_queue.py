"""
AWS SQS queue representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


# pylint: disable= too-many-instance-attributes

class SQSQueue(AwsObject):
    """
    AWS SQS queue class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.delay_seconds = None
        self.maximum_message_size = None
        self.message_retention_period = None
        self.policy = None
        self.receive_message_wait_time_seconds = None
        self.visibility_timeout = None
        self.redrive_policy = None
        self.redrive_allow_policy = None
        self.source_queue_arns = None
        self.kms_master_key_id = None
        self.kms_data_key_reuse_period_seconds = None
        self.fifo_queue = None
        self.content_based_deduplication = None
        self.deduplication_scope = None
        self.fifo_throughput_limit = None
        self.deduplication_scope = None
        self.fifo_throughput_limit = None
        self.queue_url = None
        self.tags = {}

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
        Standard.

        :param dict_src:
        :return:
        """

        init_options = {
            "QueueUrl": self.init_default_attr,
            "QueueArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "ApproximateNumberOfMessages": self.init_default_attr,
            "ApproximateNumberOfMessagesNotVisible": self.init_default_attr,
            "ApproximateNumberOfMessagesDelayed": self.init_default_attr,
            "CreatedTimestamp": self.init_default_attr,
            "LastModifiedTimestamp": self.init_default_attr,
            "VisibilityTimeout": self.init_default_attr,
            "MaximumMessageSize": self.init_default_attr,
            "MessageRetentionPeriod": self.init_default_attr,
            "DelaySeconds": self.init_default_attr,
            "Policy": self.init_default_attr,
            "ReceiveMessageWaitTimeSeconds": self.init_default_attr,
            "KmsMasterKeyId": self.init_default_attr,
            "KmsDataKeyReusePeriodSeconds": self.init_default_attr,
            "FifoQueue": self.init_default_attr,
            "DeduplicationScope": self.init_default_attr,
            "FifoThroughputLimit": self.init_default_attr,
            "ContentBasedDeduplication": self.init_default_attr,
            "SqsManagedSseEnabled": self.init_default_attr,
            "RedrivePolicy": self.init_default_attr,
            "RedriveAllowPolicy": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_set_attributes_request(self, target_queue):
        """
        Standard.

        :param target_queue:
        :return:
        """
        target_req = target_queue.generate_create_request()
        self_req = self.generate_create_request()

        changed = False
        for target_key, target_value in target_req["Attributes"].items():
            if self_req["Attributes"].get(target_key) != target_value:
                self_req["Attributes"][target_key] = target_value
                changed = True

        to_del = []
        for self_key in self_req["Attributes"]:
            if self_key not in target_req["Attributes"]:
                to_del.append(self_key)
                changed = True

        for key in to_del:
            del self_req["Attributes"][key]

        if not changed:
            return None

        self_req["QueueUrl"] = self.queue_url
        del self_req["QueueName"]
        del self_req["tags"]

        return self_req

    def generate_tag_queue_request(self, desired_queue):
        """
        Standard.

        :param desired_queue:
        :return:
        """

        if self.tags != desired_queue.tags:
            return {"QueueUrl": self.queue_url, "Tags": desired_queue.tags}

        return None

    # pylint: disable= too-many-branches
    def generate_create_request(self):
        """
        Standard.

        :return:
        """

        request = {"QueueName": self.name, "tags": self.tags}

        attributes = {}
        if self.delay_seconds is not None:
            attributes["DelaySeconds"] = self.delay_seconds

        if self.maximum_message_size is not None:
            attributes["MaximumMessageSize"] = self.maximum_message_size

        if self.message_retention_period is not None:
            attributes["MessageRetentionPeriod"] = self.message_retention_period

        if self.policy is not None:
            attributes["Policy"] = self.policy

        if self.receive_message_wait_time_seconds is not None:
            attributes[
                "ReceiveMessageWaitTimeSeconds"
            ] = self.receive_message_wait_time_seconds

        if self.visibility_timeout is not None:
            attributes["VisibilityTimeout"] = self.visibility_timeout

        if self.redrive_policy is not None:
            attributes["RedrivePolicy"] = self.redrive_policy

        if self.redrive_allow_policy is not None:
            attributes["RedriveAllowPolicy"] = self.redrive_allow_policy

        if self.source_queue_arns is not None:
            attributes["sourceQueueArns"] = self.source_queue_arns

        if self.kms_master_key_id is not None:
            attributes["KmsMasterKeyId"] = self.kms_master_key_id

        if self.kms_data_key_reuse_period_seconds is not None:
            attributes[
                "KmsDataKeyReusePeriodSeconds"
            ] = self.kms_data_key_reuse_period_seconds

        if self.fifo_queue is not None:
            attributes["FifoQueue"] = self.fifo_queue

        if self.content_based_deduplication is not None:
            attributes["ContentBasedDeduplication"] = self.content_based_deduplication

        if self.deduplication_scope is not None:
            attributes["DeduplicationScope"] = self.deduplication_scope

        if self.fifo_throughput_limit is not None:
            attributes["FifoThroughputLimit"] = self.fifo_throughput_limit

        if self.deduplication_scope is not None:
            attributes["DeduplicationScope"] = self.deduplication_scope

        if self.fifo_throughput_limit is not None:
            attributes["FifoThroughputLimit"] = self.fifo_throughput_limit

        if attributes:
            request["Attributes"] = attributes

        return request

    # pylint: disable= arguments-differ
    def get_tag(self, key, ignore_missing_tag=False):
        """
        SQS Queue has dict and not list...

        :param key:
        :param ignore_missing_tag:
        :return:
        """
        if self.tags is None:
            if ignore_missing_tag:
                return None
            raise RuntimeError("No tags associated")

        try:
            return self.tags.get(key)
        except KeyError as inst:
            if ignore_missing_tag:
                return None
            raise RuntimeError(f"No tag '{key}' associated") from inst

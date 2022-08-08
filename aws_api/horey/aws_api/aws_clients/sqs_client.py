"""
AWS lambda client to handle lambda service API requests.
"""
import pdb
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.sqs_queue import SQSQueue

from horey.h_logger import get_logger

logger = get_logger()


class SQSClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "sqs"
        super().__init__(client_name)

    def get_all_queues(self, region=None, full_information=True):
        """
        Get all queues in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_queues(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_queues(region, full_information=full_information)

        return final_result

    def get_region_queues(self, region, full_information=True, filters_req=None):
        final_result = list()
        AWSAccount.set_aws_region(region)

        raw_data = list(self.execute(self.client.list_queues, None, raw_data=True, filters_req=filters_req))[0]
        urls = raw_data.get("QueueUrls") or []

        for url in urls:
            dict_src = {"QueueUrl": url}
            obj = SQSQueue(dict_src)
            final_result.append(obj)
            if full_information:
                self.update_queue_information(obj)

        return final_result

    def update_queue_information(self, sqs_queue):
        filters_req = {"QueueUrl": sqs_queue.queue_url, "AttributeNames": ["All"]}
        for dict_attributes in self.execute(self.client.get_queue_attributes, "Attributes", filters_req=filters_req):
            sqs_queue.update_attributes_from_raw_response(dict_attributes)

        filters_req = {"QueueUrl": sqs_queue.queue_url}
        for dict_attributes in self.execute(self.client.list_queue_tags, None, raw_data=True, filters_req=filters_req):
            sqs_queue.update_tags_from_raw_response(dict_attributes)

    def provision_queue(self, queue: SQSQueue, declarative=True):
        """
        Provision object queue.

        @param queue:
        @param declarative:
        @return:
        """

        region_queues = self.get_region_queues(queue.region, filters_req={"QueueNamePrefix": queue.name})
        region_queues = [region_queue for region_queue in region_queues if
                         region_queue.get_tagname(ignore_missing_tag=True) == queue.get_tagname()]

        if len(region_queues) > 1:
            raise RuntimeError(f"len(region_queues) > 1: {len(region_queues)}")
        if len(region_queues) == 0:
            response = self.provision_queue_raw(queue.generate_create_request())
            dict_src = {"QueueUrl": response}
            queue.update_from_raw_response(dict_src)
            self.update_queue_information(queue)
            return

        region_queue = region_queues[0]
        if not declarative:
            queue.update_from_raw_response(region_queue.dict_src)
            self.update_queue_information(queue)
            return

        update_request = region_queue.generate_set_attributes_request(queue)

        if update_request is not None:
            self.set_queue_attributes_raw(update_request)

        queue.update_from_raw_response(region_queue.dict_src)
        self.update_queue_information(queue)

    def set_queue_attributes_raw(self, request_dict):
        logger.info(f"Updating queue: {request_dict}")
        for response in self.execute(self.client.set_queue_attributes, None, raw_data=True, filters_req=request_dict):
            return response

    def provision_queue_raw(self, request_dict):
        logger.info(f"Creating queue: {request_dict}")
        for response in self.execute(self.client.create_queue, "QueueUrl",
                                     filters_req=request_dict):
            return response

    def receive_message(self, queue):
        return self.receive_message_raw({"QueueUrl": queue.queue_url, "MaxNumberOfMessages": 10})

    def receive_message_raw(self, request_dict):
        logger.info(f"Receiving from queue: {request_dict}")
        return list(self.execute(self.client.receive_message, "Messages",
                                 filters_req=request_dict))

    def send_message(self, queue, message):
        return self.send_message_raw({"QueueUrl": queue.queue_url, "MessageBody": message})

    def send_message_raw(self, request_dict):
        logger.info(f"Sending message to queue: {request_dict}")
        return list(self.execute(self.client.send_message, None, raw_data=True,
                                 filters_req=request_dict))

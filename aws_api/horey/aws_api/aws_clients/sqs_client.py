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

    def get_region_queues(self, region, full_information=True):
        final_result = list()
        AWSAccount.set_aws_region(region)

        raw_data = list(self.execute(self.client.list_queues, None, raw_data=True))[0]
        urls = raw_data.get("QueueUrls") or []

        for url in urls:
            dict_src = {"QueueUrl": url}
            obj = SQSQueue(dict_src)
            final_result.append(obj)
            if full_information:
                filters_req = {"QueueUrl": obj.queue_url, "AttributeNames": ['All']}
                for dict_attributes in self.execute(self.client.get_queue_attributes, "Attributes", filters_req=filters_req):
                    obj.update_attributes_from_raw_response(dict_attributes)

                filters_req = {"QueueUrl": obj.queue_url}
                for dict_attributes in self.execute(self.client.list_queue_tags, None, raw_data=True, filters_req=filters_req):
                    obj.update_tags_from_raw_response(dict_attributes)

        return final_result

    def provision_queue(self, queue):
        region_queues = self.get_region_queues(queue.region)
        for region_queue in region_queues:
            if region_queue.get_tagname(ignore_missing_tag=True) == queue.get_tagname():
                queue.update_from_raw_response(region_queue.dict_src)
                return

        AWSAccount.set_aws_region(queue.region)
        response = self.provision_queue_raw(queue.generate_create_request())

        dict_src = {"QueueUrl": response}
        queue.update_from_raw_response(dict_src)

    def provision_queue_raw(self, request_dict):
        logger.info(f"Creating queue: {request_dict}")
        for response in self.execute(self.client.create_queue, "QueueUrl",
                                     filters_req=request_dict):
            return response

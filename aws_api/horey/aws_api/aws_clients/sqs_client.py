"""
AWS lambda client to handle lambda service API requests.
"""
import pdb
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.sqs_queue import SQSQueue

from horey.h_logger import get_logger
logger = get_logger()


class TemplateClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "Template"
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
        for dict_src in self.execute(self.client.describe_queues, "queues"):
            obj = SQSQueue(dict_src)
            final_result.append(obj)
            if full_information:
                #get_queue_attributes
                #list_queue_tags
                raise NotImplementedError()

        return final_result

    def provision_queue(self, queue):
        region_queues = self.get_region_queues(queue.region)
        for region_queue in region_queues:
            if region_queue.get_tagname(ignore_missing_tag=True) == queue.get_tagname():
                queue.update_from_raw_response(region_queue.dict_src)
                return

        AWSAccount.set_aws_region(queue.region)
        response = self.provision_queue_raw(queue.generate_create_request())
        queue.update_from_raw_response(response)

    def provision_queue_raw(self, request_dict):
        logger.info(f"Creating queue: {request_dict}")
        for response in self.execute(self.client.create_queue, "queue",
                                     filters_req=request_dict):
            return response
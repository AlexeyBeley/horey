"""
AWS sqs client

"""

from horey.aws_api.aws_clients.boto3_client import Boto3Client

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

    # pylint: disable= too-many-arguments
    def yield_queues(self, region=None, update_info=False, filters_req=None, get_tags=True):
        """
        Yield queues

        :return:
        """

        regional_fetcher_generator = self.yield_queues_raw
        for obj in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  SQSQueue,
                                                  update_info=update_info,
                                                  get_tags_callback=self.get_queue_tags if get_tags else None,
                                                  regions=[region] if region else None,
                                                  filters_req=filters_req):
            yield obj

    def yield_queues_raw(self, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for queue_url  in self.execute(
                self.client.list_queues, "QueueUrls",
                filters_req=filters_req,
                exception_ignore_callback=lambda error: "RepositoryNotFoundException"
            in repr(error)
        ):
            filters_req = {"QueueUrl": queue_url, "AttributeNames": ["All"]}
            for dict_src in self.execute(
                    self.client.get_queue_attributes, "Attributes", filters_req=filters_req
            ):
                dict_src["QueueUrl"] = queue_url
                yield dict_src

    def get_all_queues(self, region=None):
        """
        Get all queues in all regions.
        :return:
        """


        return list(self.yield_queues(region=region))

    def get_region_queues(self, region, filters_req=None):
        """
        Standard.

        :param region:
        :param filters_req:
        :return:
        """

        return list(self.yield_queues(region=region, filters_req=filters_req))

    def update_queue_information(self, sqs_queue):
        """
        Standard.

        :param sqs_queue:
        :return:
        """
        filters_req = {"QueueUrl": sqs_queue.queue_url, "AttributeNames": ["All"]}
        for dict_attributes in self.execute(
            self.client.get_queue_attributes, "Attributes", filters_req=filters_req
        ):
            sqs_queue.update_from_raw_response(dict_attributes)

    def provision_queue(self, queue: SQSQueue, declarative=True):
        """
        Provision object queue.

        @param queue:
        @param declarative:
        @return:
        """

        region_queues = self.get_region_queues(
            queue.region, filters_req={"QueueNamePrefix": queue.name}
        )
        region_queues = [
            region_queue
            for region_queue in region_queues
            if region_queue.get_tagname(ignore_missing_tag=True) == queue.get_tagname()
        ]

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

        tag_request = region_queue.generate_tag_queue_request(queue)

        if tag_request is not None:
            self.tag_queue_raw(tag_request)

        queue.update_from_raw_response(region_queue.dict_src)
        self.update_queue_information(queue)

    def set_queue_attributes_raw(self, request_dict):
        """
        Update queue

        :param request_dict:
        :return:
        """

        logger.info(f"Updating queue: {request_dict}")
        for response in self.execute(
            self.client.set_queue_attributes,
            None,
            raw_data=True,
            filters_req=request_dict,
        ):
            self.clear_cache(SQSQueue)
            return response

    def provision_queue_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Creating queue: {request_dict}")
        for response in self.execute(
            self.client.create_queue, "QueueUrl", filters_req=request_dict
        ):
            self.clear_cache(SQSQueue)
            return response

    def receive_message(self, queue):
        """
        Get message from queue object.

        :param queue:
        :return:
        """

        return self.receive_message_raw(
            {"QueueUrl": queue.queue_url, "MaxNumberOfMessages": 10}
        )

    def receive_message_raw(self, request_dict):
        """
        Get message request.

        :param request_dict:
        :return:
        """

        logger.info(f"Receiving from queue: {request_dict}")
        return list(
            self.execute(
                self.client.receive_message, "Messages", filters_req=request_dict
            )
        )

    def send_message(self, queue, message):
        """
        Send dict message to queue object.

        :param queue:
        :param message:
        :return:
        """
        return self.send_message_raw(
            {"QueueUrl": queue.queue_url, "MessageBody": message}
        )

    def send_message_raw(self, request_dict):
        """
        Send dict message to queue.

        :param request_dict:
        :return:
        """

        logger.info(f"Sending message to queue: {request_dict}")
        return list(
            self.execute(
                self.client.send_message, None, raw_data=True, filters_req=request_dict
            )
        )

    def get_queue_tags(self, queue):
        """
        Get all tags for queue

        :return:
        """

        filters_req = {"QueueUrl": queue.queue_url}
        for raw_response in self.execute(
                self.client.list_queue_tags, None, raw_data=True, filters_req=filters_req
        ):
            queue.tags = raw_response.get("Tags")

    def tag_queue_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Tag queue: {request_dict}")
        for response in self.execute(
                self.client.tag_queue, None, raw_data=True, filters_req=request_dict
            ):
            self.clear_cache(SQSQueue)
            return response

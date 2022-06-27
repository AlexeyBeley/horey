"""
Base Boto3 client. It provides sessions and client management.
"""
import datetime

import time
from horey.aws_api.aws_clients.sessions_manager import SessionsManager
import pdb
from horey.h_logger import get_logger

logger = get_logger()


class Boto3Client:
    """
    Main class to inherite from, when creating AWS clients.
    """
    EXEC_COUNT = 0
    SESSIONS_MANAGER = SessionsManager()
    EXECUTION_RETRY_COUNT = 1000
    NEXT_PAGE_REQUEST_KEY = "NextToken"
    NEXT_PAGE_RESPONSE_KEY = "NextToken"
    NEXT_PAGE_INITIAL_KEY = None

    def __init__(self, client_name):
        """
        self.client shouldn't be inited, the init should be done on demand if execute is called
        Client is a singleton identified by client_name and region_name

        :param client_name:

        """

        self.client_name = client_name
        self._account_id = None

    @property
    def account_id(self):
        if self._account_id is None:
            sts_client = self.SESSIONS_MANAGER.get_client("sts")
            self._account_id = sts_client.get_caller_identity()["Account"]
        return self._account_id

    @property
    def client(self):
        """
        Returns current sessions AWS client, which executes the base api calls
        :return:
        """
        return self.SESSIONS_MANAGER.get_client(self.client_name)

    @client.setter
    def client(self, _):
        """
        As the clients are managed by session manager they can't be assigned explicitly.
        :param _:
        :return:
        """
        raise RuntimeError(f"Nobody can set a client explicitly in{self}")

    def yield_with_paginator(self, func_command, return_string, filters_req=None, raw_data=False, internal_starting_token=False, exception_ignore_callback=None):
        """
        Function to yeild replies, if there is no need to get all replies.
        It can save API requests if the expected information found before.

        :param func_command: Bound method from _client instance
        :param return_string: string to retrive the infromation from reply dict
        :param filters_req: filters dict passed to the API client to filter the response
        :param exception_ignore_callback: called on exception if returns true - do not retries on exception
        :return: list of replies
        """

        if filters_req is None:
            filters_req = {}

        starting_token = self.NEXT_PAGE_INITIAL_KEY
        retry_counter = 0
        while retry_counter < self.EXECUTION_RETRY_COUNT:
            try:
                logger.info(f"Start paginating with starting_token: '{starting_token}' and args '{filters_req}'")
                for result, new_starting_token in self.unpack_pagination_loop(starting_token, func_command.__name__, return_string, filters_req, raw_data=raw_data, internal_starting_token=internal_starting_token):
                    retry_counter = 0
                    starting_token = new_starting_token
                    yield result
                break
            except self.NoReturnStringError:
                raise
            except Exception as exception_instance:
                logger.warning(f"Exception received in paginator '{func_command.__name__}' Error: {repr(exception_instance)}")
                exception_weight = 10
                time_to_sleep = 1

                if "Throttling" in repr(exception_instance):
                    exception_weight = 1
                    time_to_sleep = retry_counter + exception_weight
                    logger.error(f"Retrying after Throttling '{func_command.__name__}' attempt {retry_counter}/{self.EXECUTION_RETRY_COUNT} Error: {exception_instance}")

                if exception_ignore_callback is not None and exception_ignore_callback(exception_instance):
                    return

                retry_counter += exception_weight
                time.sleep(time_to_sleep)
                logger.warning(f"Retrying '{func_command.__name__}' attempt {retry_counter}/{self.EXECUTION_RETRY_COUNT} Error: {exception_instance}")
        else:
            raise TimeoutError(f"Max attempts reached while executing '{func_command.__name__}': {self.EXECUTION_RETRY_COUNT}")

    def unpack_pagination_loop(self, starting_token, func_command_name, return_string, filters_req, raw_data=False, internal_starting_token=False):
        for _page in self.client.get_paginator(func_command_name).paginate(
                PaginationConfig={self.NEXT_PAGE_REQUEST_KEY: starting_token},
                **filters_req):

            starting_token = self.unpack_pagination_loop_starting_token(_page, return_string, internal_starting_token)
            logger.info(f"Updating '{func_command_name}' {filters_req} pagination starting_token: {starting_token}")

            Boto3Client.EXEC_COUNT += 1

            if raw_data:
                yield _page, starting_token
            else:
                if return_string not in _page:
                    raise self.NoReturnStringError(f"Has no return string '{return_string}'. Return dict: {_page}")
                if isinstance(_page[return_string], list):
                    for response_obj in _page[return_string]:
                        yield response_obj, starting_token
                elif isinstance(_page[return_string], dict):
                    yield _page[return_string], starting_token
                else:
                    raise NotImplementedError(f"Unexpected return type: {type(_page[return_string])}")

            if starting_token is None:
                return

    def unpack_pagination_loop_starting_token(self, _page, return_string, internal_starting_token):
        if internal_starting_token:
            return _page.get(return_string).get(self.NEXT_PAGE_RESPONSE_KEY)
        else:
            return _page.get(self.NEXT_PAGE_RESPONSE_KEY)

    def execute(self, func_command, return_string, filters_req=None, raw_data=False, internal_starting_token=False, exception_ignore_callback=None):
        """
        Command to execute clients bound function- execute with paginator if available.

        :param func_command: Bound method from _client instance
        :param return_string: string to retrive the infromation from reply dict
        :param filters_req: filters dict passed to the API client to filter the response
        :param exception_ignore_callback: called on exception if returns true - do not retries on exception
        :return: list of replies
        """

        if filters_req is None:
            filters_req = {}

        if self.client.can_paginate(func_command.__name__):
            for ret_obj in self.yield_with_paginator(func_command, return_string, filters_req=filters_req, raw_data=raw_data, internal_starting_token=internal_starting_token, exception_ignore_callback=exception_ignore_callback):
                yield ret_obj
            return

        Boto3Client.EXEC_COUNT += 1
        try:
            response = func_command(**filters_req)
        except Exception as exception_instance:
            logger.warning(f"Exception received '{func_command.__name__}' Error: {repr(exception_instance)}")
            if exception_ignore_callback is not None and exception_ignore_callback(exception_instance):
                return
            raise

        if raw_data:
            yield response
            return

        if isinstance(response[return_string], list):
            ret_lst = response[return_string]
        elif type(response[return_string]) in [str, dict, type(None), bool]:
            ret_lst = [response[return_string]]
        else:
            raise NotImplementedError("{} type:{}".format(response[return_string], type(response[return_string])))

        for ret_obj in ret_lst:
            yield ret_obj

    @staticmethod
    def wait_for_status(observed_object, update_function, desired_statuses, permit_statues, error_statuses,
                        timeout=300, sleep_time=5):
        start_time = datetime.datetime.now()
        logger.info(f"Starting waiting loop for {observed_object.id} to become one of {desired_statuses}")

        for i in range(timeout // sleep_time):
            update_function(observed_object)

            object_status = observed_object.get_status()

            if object_status in desired_statuses:
                break

            if object_status in error_statuses:
                raise RuntimeError(f"{observed_object.id} is in error status: {object_status}")

            if permit_statues and object_status not in permit_statues:
                raise RuntimeError(
                    f"Permit statuses were set but {observed_object.id} is in a different status: {object_status}")

            logger.info(
                f"[{i*sleep_time}/{timeout} seconds] Status waiter for {observed_object.id} is going to sleep for {sleep_time}. Status: {object_status}")
            time.sleep(sleep_time)
        else:
            raise TimeoutError(f"Did not reach one of the desired status {desired_statuses} for {timeout} seconds. Current status: {object_status}")

        end_time = datetime.datetime.now()
        logger.info(
            f"Finished waiting loop for {observed_object.id} to become one of {desired_statuses}. Took {end_time - start_time}")

    def get_tags(self, obj):
        logger.info(f"Getting resource tags: {obj.arn}")
        for response in self.execute(self.client.get_tags, "Tags",
                                     filters_req={"ResourceArn": obj.arn}):
            return response

    def tag_resource(self, obj):
        logger.info(f"Tagging resource: {obj.arn}")
        for response in self.execute(self.client.tag_resource, "Tags",
                                     filters_req={"ResourceArn": obj.arn, "TagsToAdd": obj.tags}, raw_data=True):
            return response

    class NoReturnStringError(Exception):
        pass

    class ResourceNotFoundError(ValueError):
        pass

"""
Base Boto3 client. It provides sessions and client management.
"""

import os
import sys
import time
from sessions_manager import SessionsManager
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "base_entities" ))

from h_logger import get_logger

logger = get_logger()


class Boto3Client:
    """
    Main class to inherite from, when creating AWS clients.
    """
    EXEC_COUNT = 0
    SESSIONS_MANAGER = SessionsManager()
    EXECUTION_RETRY_COUNT = 4
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

    def yield_with_paginator(self, func_command, return_string, filters_req=None, raw_data=False):
        """
        Function to yeild replies, if there is no need to get all replies.
        It can save API requests if the expected information found before.

        :param func_command: Bound method from _client instance
        :param return_string: string to retrive the infromation from reply dict
        :param filters_req: filters dict passed to the API client to filter the response
        :return: list of replies
        """
        if raw_data:
            raise NotImplementedError()

        if filters_req is None:
            filters_req = {}

        starting_token = self.NEXT_PAGE_INITIAL_KEY

        for retry_counter in range(self.EXECUTION_RETRY_COUNT):
            try:
                logger.info(f"Start paginating with starting_token: '{starting_token}' and args '{filters_req}'")

                for _page in self.client.get_paginator(func_command.__name__).paginate(
                        PaginationConfig={self.NEXT_PAGE_REQUEST_KEY: starting_token},
                        **filters_req):

                    starting_token = _page.get(self.NEXT_PAGE_RESPONSE_KEY)
                    logger.info(f"Updating '{func_command.__name__}' {filters_req} pagination starting_token: {starting_token}")

                    Boto3Client.EXEC_COUNT += 1

                    if return_string not in _page:
                        raise NotImplementedError("Has no return string")

                    for response_obj in _page[return_string]:
                        yield response_obj
                    if starting_token is None:
                        return
            except Exception as exception_instance:
                time.sleep(1)
                logger.warning(f"Retrying '{func_command.__name__}' attempt {retry_counter}/{self.EXECUTION_RETRY_COUNT} Error: {exception_instance}")

    def execute(self, func_command, return_string, filters_req=None, raw_data=False):
        """
        Command to execute clients bound function- execute with paginator if available.

        :param func_command: Bound method from _client instance
        :param return_string: string to retrive the infromation from reply dict
        :param filters_req: filters dict passed to the API client to filter the response
        :return: list of replies
        """

        if filters_req is None:
            filters_req = {}

        if self.client.can_paginate(func_command.__name__):
            for ret_obj in self.yield_with_paginator(func_command, return_string, filters_req=filters_req, raw_data=raw_data):
                yield ret_obj
            return

        Boto3Client.EXEC_COUNT += 1
        response = func_command(**filters_req)

        if raw_data:
            yield response
            return

        if isinstance(response[return_string], list):
            ret_lst = response[return_string]
        elif type(response[return_string]) in [str, dict]:
            ret_lst = [response[return_string]]
        else:
            raise NotImplementedError("{} type:{}".format(response[return_string], type(response[return_string])))

        for ret_obj in ret_lst:
            yield ret_obj

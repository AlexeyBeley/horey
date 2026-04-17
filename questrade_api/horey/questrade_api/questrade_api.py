"""
Shamelessly stolen from:
https://questrade.com/lukecyca/pyslack
"""
import datetime
import json

import requests
from horey.h_logger import get_logger
from horey.questrade_api.questrade_api_configuration_policy import (
    QuestradeAPIConfigurationPolicy,
)

logger = get_logger()


class QuestradeAPI:
    """
    Main Class.
    https://www.questrade.com/api/documentation/getting-started
    """

    def __init__(self, configuration: QuestradeAPIConfigurationPolicy = None):
        self.configuration = configuration
        self.access_token = self.configuration.token
        self.api_server = configuration.api_server

    def create_request(self, request: str):
        """
        Construct request.

        #request = "https://questrade.com/api/v4/groups/{group_id}/projects"
        @param request:
        @return:
        """

        if request.startswith("/"):
            request = request[1:]

        return f"{self.api_server}/{request}"

    def get(self, request_path):
        """
        Compose and send GET request.

        @param request_path:
        @return:
        """

        request = self.create_request(request_path)

        headers = {"Authorization": f"Bearer {self.access_token}"}
        breakpoint()
        response = requests.get(request, headers=headers)
        response.raise_for_status()
        try:
            return response.json()
        except Exception:
            return response.text


    def post(self, request_path, data):
        """
        Compose and send POST request

        @param request_path:
        @param data:
        @return:
        """

        request = self.create_request(request_path)
        return self.post_raw(request, data)

    def post_raw(self, request, data):
        """
        Send POST request.

        @param request:
        @param data:
        @return:
        """

        headers = {"Authorization": f"Bearer {self.configuration.pat}",
                   "Content-Type": "application/vnd.questrade+json",
                   "Accept": "application/vnd.questrade+json"}

        response = requests.post(request, data=json.dumps(data), headers=headers)

        if response.status_code not in [200, 201]:
            raise RuntimeError(
                f"Request to questrade api returned an error {response.status_code}, the response is:\n{response.text}"
            )
        return response.json()

    def put(self, request_path, data):
        """
        Compose and send POST request

        @param request_path:
        @param data:
        @return:
        """

        request = self.create_request(request_path)
        headers = {"Authorization": f"Bearer {self.configuration.pat}",
                   "Content-Type": "application/vnd.questrade+json",
                   "Accept": "application/vnd.questrade+json"}

        response = requests.put(request, data=json.dumps(data), headers=headers)
        response.raise_for_status()

    def connect(self):
        """
        Connect to the api

        :return:
        """

        response_file_path = self.configuration.data_directory / "response.json"
        if response_file_path.exists():
            with open(response_file_path, encoding="utf-8") as file_handler:
                response = json.load(file_handler)
            timestamp_now = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
            if timestamp_now < response["expires_at"]:
                self.access_token = response["access_token"]
                self.api_server = response['api_server'].rstrip("/")
                return

            response_file_path.unlink()

        auth_url = f"https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token={self.configuration.token}"
        response = requests.get(auth_url).json()
        response["expires_at"] = (datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=response["expires_in"])).timestamp()

        with open(response_file_path, "w", encoding="utf-8") as file_handler:
            json.dump(response, file_handler)
        breakpoint()

        self.access_token = response["access_token"]
        logger.info(f"Connected to Questtrade API, new token: {self.access_token}")

        self.api_server= response['api_server'].rstrip("/")  # e.g., https://api01.iq.questrade.com/
        logger.info(f"Connected to Questtrade API, new server: {self.api_server}")
        return True

    def get_accounts(self):
        """
        Get accounts

        :return:
        """

        accounts = self.get(f"v1/accounts")
        breakpoint()
        return accounts

    def get_positions(self):
        """
        Get accounts

        :return:
        """

        positions = self.get(f"v1/accounts/{self.configuration.account}/positions")
        breakpoint()
        return positions
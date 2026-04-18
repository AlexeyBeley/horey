"""
Shamelessly stolen from:
https://questrade.com/lukecyca/pyslack
"""
from datetime import datetime, timezone, timedelta
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

        refresh_token = self.configuration.token

        response_file_path = self.configuration.data_directory / "response.json"
        if response_file_path.exists():
            with open(response_file_path, encoding="utf-8") as file_handler:
                response = json.load(file_handler)
            timestamp_now = datetime.now(tz=timezone.utc).timestamp()
            if timestamp_now < response["expires_at"] - 5*60:
                self.access_token = response["access_token"]
                self.api_server = response['api_server'].rstrip("/")
                return

            response_file_path.unlink()
            refresh_token = response["refresh_token"]

        auth_url = f"https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token={refresh_token}"
        response = requests.get(auth_url).json()
        response["expires_at"] = (datetime.now(tz=timezone.utc) + timedelta(seconds=response["expires_in"])).timestamp()

        with open(response_file_path, "w", encoding="utf-8") as file_handler:
            json.dump(response, file_handler)

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
        return accounts

    def get_positions(self):
        """
        Get accounts

        :return:
        """

        positions = self.get(f"v1/accounts/{self.configuration.account}/positions")
        return positions

    def get_position_history(self, position_id, time_start, time_end, output_file=None):
        """
        Get position history.

        :return:
        """

        start_time = self.convert_time_to_request_format(time_start)
        end_time = self.convert_time_to_request_format(time_end)

        position_candles = self.get(f"v1/markets/candles/{position_id}?startTime={start_time}&endTime={end_time}&interval=OneMinute")
        if output_file:
            with open(self.configuration.data_directory / output_file, "w", encoding="utf-8") as file_handler:
                json.dump(position_candles, file_handler, indent=2)

        return position_candles

    @staticmethod
    def convert_time_to_request_format(time_src):
        """
        Convert time to request format.
        :param time_src:
        :return:
        """

        formatted = time_src.strftime("%Y-%m-%dT%H:%M:%S%z")
        # Insert colon in timezone: "2014-10-01T00:00:00-0500" -> "2014-10-01T00:00:00-05:00"
        return formatted[:-2] + ':' + formatted[-2:]


    def get_symbols_raw(self, prefix, offset=None):
        """
        Get position history.

        :return:
        """

        symbols = self.get(f"v1/symbols/search?prefix={prefix}&offset={offset}")
        symbols = symbols["symbols"]
        return symbols

    def get_prefix_symbols(self, prefix):
        """
        Get position history.

        :return:
        """

        symbols = []
        offset = 0
        while True:
            logger.info(f"Fetching symbols for prefix: {prefix}" + f" offset: {offset}" if offset else "")
            symbols_tmp = self.get_symbols_raw(prefix, offset=offset)
            if not symbols_tmp:
                break
            symbols += symbols_tmp
            offset = len(symbols)
        with open(self.configuration.data_directory / f"symbols_{prefix}.json", "w", encoding="utf-8") as file_handler:
            json.dump(symbols, file_handler, indent=2)
        return symbols

    def get_all_symbols_from_files(self):
        """
        Get all symbols from files.
        :return:
        """

        files = self.configuration.data_directory.glob("symbols_*.json")
        symbols = {}
        for file in files:
            with open(file, "r", encoding="utf-8") as file_handler:
                symbols.update({symbol["symbolId"]: symbol for symbol in json.load(file_handler)})

        with open(self.configuration.data_directory / "symbols.json", "w", encoding="utf-8") as file_handler:
            json.dump(symbols, file_handler, indent=2)
        logger.info(f"Total symbols: {len(symbols)}")

        return symbols

    def get_tradable_stocks(self):
        """
        Get tradable stocks.

        :return:
        """
        with open(self.configuration.data_directory / "symbols.json" , encoding="utf-8") as file_handler:
            symbols = json.load(file_handler)

        # all_types = {symbol["securityType"] for symbol in symbols.values()}

        ret = []
        for symbol in symbols.values():
            if not symbol["isTradable"]:
                continue
            if symbol["securityType"] != "Stock":
                continue

            ret.append(symbol)

        return ret

    def get_all_stocks_history(self):
        """
        Get all stocks history.
        :return:
        """
        output_file_path = self.configuration.data_directory / "stocks_history.json"
        now = datetime.now(tz=timezone.utc)
        stocks = self.get_tradable_stocks()
        with open(output_file_path, encoding="utf-8") as file_handler:
            stocks_data = json.load(file_handler)
        known_symbol_ids = [symbol["symbol"]["symbolId"] for symbol in stocks_data]
        stocks = [stock for stock in stocks if stock["symbolId"] not in known_symbol_ids]

        for i, stock in enumerate(stocks):
            logger.info(f"Fetching stock history {i}/{len(stocks)} id:{stock['symbolId']} Symbol:{stock['symbol']}")
            res = self.get_position_history(stock["symbolId"], now - timedelta(days=2),
                                          now - timedelta(days=1))
            res["symbol"] = stock
            stocks_data.append(res)
            with open(output_file_path, "w", encoding="utf-8") as file_handler:
                json.dump(stocks_data, file_handler, indent=2)
        return True

    def calculate_median(self):
        breakpoint()
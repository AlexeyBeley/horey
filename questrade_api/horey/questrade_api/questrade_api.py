"""
Shamelessly stolen from:
https://questrade.com/lukecyca/pyslack
"""

# pylint: disable = too-many-lines
import string
import traceback
from collections import defaultdict
import sqlite3
import platform
import time
import threading
from threading import Lock
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
from typing import List
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo


import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, \
                            JavascriptException, ElementNotInteractableException, \
                            ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains


from horey.h_logger import get_logger
from horey.selenium_api.selenium_api import SeleniumAPI
from horey.questrade_api.questrade_api_configuration_policy import (
    QuestradeAPIConfigurationPolicy,
)
from horey.questrade_api.items import Symbol, Candle, Position, Order, PurchasePlan, PurchasePlanItem
from horey.questrade_api.selenium_states.login import Login, SeleniumState
from horey.questrade_api.selenium_states.order_details_filled import OrderDetailsFilled
from horey.questrade_api.selenium_states.order_placed import OrderPlaced
#from horey.telegram_api.telegram_api import TelegramAPI

logger = get_logger()


class QuestradeAPI:
    """
    Main Class.
    https://www.questrade.com/api/documentation/getting-started
    """

    THREADING_LOCK = Lock()
    ACTIVE_PLANNING_THREADING_LOCK = Lock()

    def __init__(self, configuration: QuestradeAPIConfigurationPolicy = None):
        self.stopped = False
        self.configuration = configuration
        self.access_token = self.configuration.token
        self.api_server = configuration.api_server
        self._db_connection = None
        self._db_cursor = None
        self._db_historical_data_connection = None
        self._db_historical_data_cursor = None
        self._selenium_api = None
        self.skip_symbols = ["SLQT.30632238", "SPWR", "TOPP.59353293"]
        self.clicked_on_ignore_night_sales = False
        self._active_purchase_planning = False
        self.trading_hours_by_day = {"Sunday": [(20, 23)],
                                    "Monday": [(0, 1), (4, 23)],
                                    "Tuesday": [(0, 1), (4, 23)],
                                    "Wednesday": [(0, 1), (4, 23)],
                                    "Thursday":[(0, 1), (4, 23)],
                                    "Friday": [(0, 1), (4, 19)],
                                    "Saturday": []}

        self.interesting_symbols = {}
        self.server_time = None
        self.server_update_time = None
        self.pause = False

        # used to continue execution from specific chunk after a failure
        self.populate_db_with_all_symbols_candles_chunk_start = 242757
        #self.telegram_api = TelegramAPI()

    @property
    def active_purchase_planning(self):
        return self._active_purchase_planning

    @active_purchase_planning.setter
    def active_purchase_planning(self, value):
        assert type(value) is bool
        with QuestradeAPI.ACTIVE_PLANNING_THREADING_LOCK:
            self._active_purchase_planning = value
            logger.info(f"Setting {self._active_purchase_planning=}")

    @property
    def selenium_api(self) -> SeleniumAPI:
        """
        Getter for selenium_api

        :return:
        """

        if self._selenium_api is None:
            self._selenium_api = SeleniumAPI()
            self._selenium_api.connect()
        return self._selenium_api

    @staticmethod
    def connected(func):
        """
        Connected to DB decorator.
        """

        def wrapper(self, *args, **kwargs):
            """
            Wrapper for underlying function.
            """
            self.connect_api()
            return func(self, *args, **kwargs)
        return wrapper

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

    def _get(self, request_path, params=None):
        """
        Compose and send GET request.

        @param request_path:
        @return:
        """

        request = self.create_request(request_path)

        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(request, headers=headers, params=params, timeout=60)

        # handle "Server Error: Gateway Timeout for url"
        if response.status_code == 504:
            for _ in range(10):
                time.sleep(1)
                response = requests.get(request, headers=headers, params=params, timeout=60)
                if response.status_code != 504:
                    break

        response.raise_for_status()

        try:
            return response.json()
        except Exception:
            return response.text

    def get(self, request_path, params=None, retries=5, auth_reties=5):
        """
        Compose and send GET request.

        :param request_path:
        :return:
        """

        if not retries:
            raise RuntimeError(f"Failed GET {request_path=}")

        try:
            return self._get(request_path, params=params)
        except Exception as inst:
            if "Unauthorized" in repr(inst):
                if not auth_reties:
                    raise
                time.sleep(1)
                self.connect_api(reconnect=True)
                return self.get(request_path, params=params, retries=retries, auth_reties=auth_reties-1)
            elif "404 Client Error: Not Found for url" in repr(inst):
                raise self.ResourceNotFoundError() from inst
            elif "504 Server Error: Gateway Timeout for url" in repr(inst):
                time.sleep(5)
                return self.get(request_path, params=params, retries=retries, auth_reties=auth_reties)
            elif "429 Client Error: Too Many Requests for url" in repr(inst):
                time.sleep(5)
                return self.get(request_path, params=params, retries=retries, auth_reties=auth_reties)
            else:
                # ConnectionError(ProtocolError('Connection aborted.', ConnectionResetError(54, 'Connection reset by peer')))
                raise self.UnknownServerError() from inst


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

        response = requests.post(request, data=json.dumps(data), headers=headers, timeout=60)

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

        response = requests.put(request, data=json.dumps(data), headers=headers, timeout=60)
        response.raise_for_status()

    def connect_api(self, reconnect=False):
        """
        Connect to the api

        :return:
        """

        response_file_path = self.configuration.data_directory / "response.json"

        if response_file_path.exists():
            new_connection_credentials = self.connect_from_cache(response_file_path, reconnect=reconnect)
            if new_connection_credentials is None:
                return True
        else:
            base_url = "https://login.questrade.com/oauth2/token"
            params = {
                "grant_type": "refresh_token",
                "refresh_token": self.configuration.token
            }

            auth_response = requests.get(base_url, params=params, timeout=60)
            auth_response.raise_for_status()
            new_connection_credentials = auth_response.json()

        new_connection_credentials["expires_at"] = (datetime.now(tz=timezone.utc) + timedelta(seconds=new_connection_credentials["expires_in"])).timestamp()

        with open(response_file_path, "w", encoding="utf-8") as file_handler:
            json.dump(new_connection_credentials, file_handler)

        self.access_token = new_connection_credentials["access_token"]
        logger.info(f"Connected to Questtrade API, new token: {self.access_token}")

        self.api_server = new_connection_credentials['api_server'].rstrip("/")  # e.g., https://api01.iq.questrade.com/
        logger.info(f"Connected to Questtrade API, new server: {self.api_server}")

        try:
            time_response = self._get("v1/time", params=tuple())
            self.server_time = datetime.fromisoformat(time_response["time"]).astimezone(ZoneInfo("America/New_York"))
            self.server_update_time = datetime.now(timezone.utc).astimezone(ZoneInfo("America/New_York"))
        except Exception:
            breakpoint()

        return True

    def connect_from_cache(self, response_file_path:Path, reconnect:bool=False):
        """

        :param response_file_path:
        :return:
        """

        with open(response_file_path, encoding="utf-8") as file_handler:
            response = json.load(file_handler)
        timestamp_now = datetime.now(tz=timezone.utc).timestamp()
        if not reconnect and timestamp_now < response["expires_at"] - 5 * 60:
            self.access_token = response["access_token"]
            self.api_server = response['api_server'].rstrip("/")
            return None

        logger.info(f"Reconnecting to api: {reconnect=}, {timestamp_now=}, expires_at - 5min = {response['expires_at'] - 5 * 60}")

        refresh_token = response["refresh_token"]
        auth_url = f"https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token={refresh_token}"
        for _ in range(5):
            try:
                response = requests.get(auth_url, timeout=60)
                break
            except requests.exceptions.ReadTimeout:
                time.sleep(10)

        response.raise_for_status()
        response_file_path.unlink()
        return response.json()

    def get_accounts(self):
        """
        Get accounts

        :return:
        """

        accounts = self.get("v1/accounts")
        return accounts

    def get_position_history(self, position_id, time_start, time_end, output_file=None):
        """
        Get position history.

        :return:
        """

        start_time = self.convert_time_to_request_format(time_start)
        end_time = self.convert_time_to_request_format(time_end)

        position_candles = self.get(
            f"v1/markets/candles/{position_id}?startTime={start_time}&endTime={end_time}&interval=OneMinute")
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

        offset= offset or 0
        try:
            symbols = self.get(f"v1/symbols/search?prefix={prefix}&offset={offset}")
        except Exception:
            symbols = []
            raise NotImplementedError("Was breakpoint")
            return symbols
        symbols = symbols["symbols"]
        return symbols

    def populate_db_with_all_symbols_candles(self):
        """
        Check all the symbols without candles
        """

        chunk_size = 999
        symbols = self.db_get_symbols()
        for i in range(0, len(symbols), chunk_size):
            if i < self.populate_db_with_all_symbols_candles_chunk_start:
                continue
            logger.info(f"Finished 999 chunks: {i}/{int(len(symbols))}")
            self.interesting_symbols = {symbol.symbol_id: symbol for symbol in symbols[i:i + chunk_size]}
            self.db_update_interesting_symbols_candles()
            self.api_update_interesting_symbols_candles()
            self.populate_db_with_all_symbols_candles_chunk_start = i
        return True

    def populate_db_with_new_symbols(self):
        """
        Fetch and update in db.
        """

        for letter in string.ascii_uppercase:
            self.populate_db_with_new_symbols_by_prefix(letter)
        return True

    @connected
    def populate_db_with_new_symbols_by_prefix(self, prefix):
        """
        Get position history.

        :return:
        """

        symbol_dicts = []
        offset = 0
        symbols = []

        all_db_symbol_names = [symbol.symbol for symbol in self.db_get_symbols()]

        while True:
            logger.info(f"Fetching symbols for prefix: {prefix}" + f" offset: {offset}" if offset else "")
            symbol_dicts_tmp = self.get_symbols_raw(prefix, offset=offset)
            if not symbol_dicts_tmp:
                break

            offset += len(symbol_dicts_tmp)

            symbols_tmp_filtered = [Symbol(symbol_dict) for symbol_dict in symbol_dicts_tmp if symbol_dict["isTradable"] and symbol_dict["symbol"] not in all_db_symbol_names]
            for symbol in symbols_tmp_filtered:
                self.db_upsert_symbol(symbol)

            symbols += symbols_tmp_filtered

        return symbols

    def get_all_symbols_from_files(self):
        """
        Get all symbols from files.
        :return:
        """

        files = self.configuration.data_directory.glob("symbols_*.json")
        with sqlite3.connect(self.configuration.db_file_path) as conn:
            cursor = conn.cursor()

            for file in files:
                logger.info(f"Processing file: {file.name}")
                with open(file, "r", encoding="utf-8") as file_handler:
                    ret = json.load(file_handler)

                for dict_src in ret:
                    self.db_upsert_symbol(Symbol(dict_src), cursor=cursor)
                    conn.commit()
        return True

    def get_tradable_stocks(self):
        """
        Get tradable stocks.

        :return:
        """
        with open(self.configuration.data_directory / "symbols.json", encoding="utf-8") as file_handler:
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

    def fetch_symbols_by_price_range(self, min_price, max_price):
        """
        Sort symbols by transactions count.
        0.0035*100

        :return:
        """

        today = datetime.now(timezone.utc)
        start_time = today.replace(hour=3, minute=0, second=0, microsecond=0)  - timedelta(days=10)

        start_timestamp = start_time.timestamp() if start_time else None
        response = self.db_execute(
                    f"select symbol_id from candles where vwap <= {max_price} and vwap >= {min_price} AND start >= {start_timestamp} group by symbol_id"
                )

        symbols = []
        for line in response:
            symbol = self.db_get_symbol(line[0])
            if not symbol:
                logger.error(f"Symbol {line[0]} not found in DB")
                continue
            symbol.candles = self.db_get_symbol_candles([symbol])
            if len(symbol.candles) < 5:
                continue
            symbols.append(symbol)
            logger.info(f"Added {symbol.symbol} to {len(symbols)} symbols")

        ret = [[symbol.symbol, symbol.symbol_id, len(symbol.candles), symbol.candles[0].vwap] for symbol in symbols]
        with open(self.configuration.data_directory / "symbols_sorted_by_transaction_count.json", "w",
                  encoding="utf-8") as file_handler:
            json.dump(ret, file_handler, indent=2)
        return True

    def sort_cheapest_by_price(self):
        """
        Sort symbols by price.
        :return:
        """
        with open(self.configuration.data_directory / "symbols_sorted_by_transaction_count.json",
                  encoding="utf-8") as file_handler:
            ret = json.load(file_handler)

        ret.sort(key=lambda val: val[3])
        return ret

    def load_symbols_history_data(self, max_price=None):
        """
        Load data from files

        :return:
        """

        where_string = ""
        if max_price:
            where_string = f" WHERE high<={max_price}"

            response = self.db_execute(
                    f"select * from candles{where_string}"
                )

        return [Candle({
            "id": row[0],
            "symbol_id": row[1],
            "start": row[2],
            "end": row[3],
            "low": row[4],
            "high": row[5],
            "open": row[6],
            "close": row[7],
            "volume": row[8],
            "vwap": row[9]
        }) for row in response]

    def provision_db_symbols_table(self):
        """
        Create table
        :return:
        """

        self.db_execute('''
                    CREATE TABLE IF NOT EXISTS symbols (
                        id INTEGER PRIMARY KEY,
                        symbol_id INTEGER NOT NULL UNIQUE,
                        symbol TEXT NOT NULL UNIQUE,
                        description TEXT,
                        security_type TEXT,
                        listing_exchange TEXT,
                        is_tradable BOOLEAN,
                        is_quotable BOOLEAN,
                        currency TEXT
                    )
                ''')
        logger.info(f"Table symbols created in {self.configuration.db_file_path}' database")
        return True

    def provision_db_candles_table(self):
        """
        Create table

        :return:
        """

        self.db_execute('''
                    CREATE TABLE IF NOT EXISTS candles(
                        id INTEGER PRIMARY KEY,
                        symbol_id INTEGER REFERENCES symbols(symbol_id) NOT NULL,
                        start REAL NOT NULL,
                        end REAL NOT NULL,
                        low REAL NOT NULL,
                        high REAL NOT NULL,
                        open REAL NOT NULL,
                        close REAL NOT NULL,
                        volume INTEGER NOT NULL,
                        vwap REAL NOT NULL
                    )
                ''')
        logger.info(f"Table candles created in {self.configuration.db_file_path}' database")
        return True

    def db_upsert_symbol(self, symbol: Symbol, db_execute=None, keep_db_id=False):
        """
        Update or insert symbol into DB
        :param symbol:
        :return:
        """

        db_execute = db_execute or self.db_execute
        logger.info(f"Upserting symbol {symbol.symbol} into {self.configuration.db_file_path}' database")
        if keep_db_id:
            request = '''
                        INSERT OR REPLACE INTO symbols (id, symbol_id, symbol, description, security_type, listing_exchange, is_tradable, is_quotable, currency)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''
            params = (symbol.id, symbol.symbol_id, symbol.symbol, symbol.description, symbol.security_type,
                        symbol.listing_exchange, symbol.is_tradable, symbol.is_quotable, symbol.currency)
        else:
            request = '''
                        INSERT OR REPLACE INTO symbols (symbol_id, symbol, description, security_type, listing_exchange, is_tradable, is_quotable, currency)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    '''
            params = (symbol.symbol_id, symbol.symbol, symbol.description, symbol.security_type,
                        symbol.listing_exchange, symbol.is_tradable, symbol.is_quotable, symbol.currency)


        db_execute(request, params)

        logger.info(f"Symbol {symbol.symbol} upserted into {self.configuration.db_file_path}' database")
        return True

    def db_historical_data_execute(self, query, args, db_connection=None, db_cursor: sqlite3.Cursor=None):
        """
        Execute query
        :param query:
        :param args:
        :return:
        """

        db_connection = db_connection or self.db_historical_data_connection
        db_cursor = db_cursor or self.db_historical_data_cursor
        return self.db_execute(query, args, db_connection=db_connection, db_cursor=db_cursor)

    def db_execute(self, query, args, db_connection=None, db_cursor: sqlite3.Cursor=None):
        """
        Execute query
        :param query:
        :param args:
        :return:
        """

        db_connection = db_connection or self.db_connection
        db_cursor = db_cursor or self.db_cursor

        with QuestradeAPI.THREADING_LOCK:
            db_cursor.execute(query, args)
            if query.lower().startswith("select"):
                return db_cursor.fetchall()
            db_connection.commit()
        return True

    @property
    def db_connection(self):
        """
        Get DB connection
        :param self:
        :return:
        """

        if self._db_connection is None:
            self._db_connection = sqlite3.connect(self.configuration.db_file_path)
        return self._db_connection

    @property
    def db_historical_data_connection(self):
        """
        Get DB connection
        :param self:
        :return:
        """

        if self._db_historical_data_connection is None:
            self._db_historical_data_connection = sqlite3.connect(self.configuration.historical_data_db_file_path)
        return self._db_historical_data_connection

    @property
    def db_cursor(self):
        """
        Get DB cursor
        :param self:
        :return:
        """

        if self._db_cursor is None:
            self._db_cursor = self.db_connection.cursor()
        return self._db_cursor

    @property
    def db_historical_data_cursor(self):
        """
        Get DB cursor
        :param self:
        :return:
        """

        if self._db_historical_data_cursor is None:
            self._db_historical_data_cursor = self.db_historical_data_connection.cursor()
        return self._db_historical_data_cursor

    def db_upsert_candle(self, symbol_id, candle: Candle, db_execute=None, keep_db_id=False):
        """
        Update or insert candle into DB
        :param cursor:
        :param symbol_id:
        :param candle:
        :return:
        """

        db_execute = db_execute or self.db_execute
        if keep_db_id:
            request = '''
                    INSERT OR REPLACE INTO candles (id, symbol_id, start, end, low, high, open, close, volume, vwap)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''
            params = (candle.id, symbol_id, candle.float_start, candle.float_end, candle.low, candle.high, candle.open,
                          candle.close, candle.volume, candle.vwap)
        else:
            request = '''
                    INSERT OR REPLACE INTO candles (symbol_id, start, end, low, high, open, close, volume, vwap)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''
            params = (symbol_id, candle.float_start, candle.float_end, candle.low, candle.high, candle.open,
                          candle.close, candle.volume, candle.vwap)
        return db_execute(request, params)

    def db_get_symbol(self, symbol_id=None, db_execute=None, symbol_symbol=None):
        """
        Get symbol from DB
        :param db_execute:
        :param symbol_id:
        :return:
        """

        logger.debug(f"Fetching symbol {symbol_id or symbol_symbol} from {self.configuration.db_file_path}' database")
        db_execute = db_execute or self.db_execute

        return self.db_get_symbol_raw(symbol_id, db_execute, symbol_symbol=symbol_symbol)

    def db_get_symbols(self, symbol_ids=None, db_execute=None, symbol_symbols=None):
        """
        Get symbols from DB

        :param db_execute:
        :param symbol_id:
        :return:
        """

        db_execute = db_execute or self.db_execute

        if symbol_symbols is not None:
            logger.debug(f"Fetching symbols {symbol_symbols} from {self.configuration.db_file_path}' database")
            placeholders = ', '.join(['?'] * len(symbol_symbols))
            query = f'SELECT * FROM symbols WHERE symbol IN ({placeholders})'
            rows = db_execute(query, tuple(symbol_symbols))
        elif symbol_ids is not None:
            logger.debug(f"Fetching symbols {symbol_ids} from {self.configuration.db_file_path}' database")
            placeholders = ', '.join(['?'] * len(symbol_ids))
            query = f'SELECT * FROM symbols WHERE symbol_id IN ({placeholders})'
            rows = db_execute(query, tuple(symbol_ids))
        else:
            logger.debug(f"Fetching all symbols from {self.configuration.db_file_path}' database")
            query = 'SELECT * FROM symbols'
            rows = db_execute(query, tuple())

        symbols = [Symbol({
            "id": row[0],
            "symbolId": row[1],
            "symbol": row[2],
            "description": row[3],
            "securityType": row[4],
            "listingExchange": row[5],
            "isTradable": row[6],
            "isQuotable": row[7],
            "currency": row[8]
        }) for row in rows]

        return symbols

    def db_get_symbol_raw(self, symbol_id, db_execute, symbol_symbol=None):
        """
        Get symbol from DB
        :param cursor:
        :param symbol_id:
        :return:
        """

        if symbol_symbol:
            rows = db_execute('SELECT * FROM symbols WHERE symbol = ?', (symbol_symbol,))
        else:
            rows = db_execute('SELECT * FROM symbols WHERE symbol_id = ?', (symbol_id,))

        if len(rows) == 0:
            return None
        if len(rows) > 1:
            raise NotImplementedError("Implement me")
        row = rows[0]
        return Symbol({
            "id": row[0],
            "symbolId": row[1],
            "symbol": row[2],
            "description": row[3],
            "securityType": row[4],
            "listingExchange": row[5],
            "isTradable": row[6],
            "isQuotable": row[7],
            "currency": row[8]
        })

    def db_get_symbol_candles(self, symbols, limit=None, start_time:datetime=None, end_time:datetime=None, db_execute=None):
        """
        Get symbol candles from DB

        :param end_time:
        :param start_time:
        :param db_execute:
        :param limit:
        :param symbols:
        :return:
        """

        end_timestamp = end_time.timestamp() if end_time else None

        start_timestamp = start_time.timestamp() if start_time else None

        return self.db_get_symbol_candles_raw([symbol.symbol_id for symbol in symbols], db_execute=db_execute, limit=limit, start_timestamp=start_timestamp, end_timestamp=end_timestamp)

    def db_get_symbol_candles_raw(self, symbol_ids, db_execute=None, limit=None, start_timestamp:float=None, end_timestamp:float=None):
        """
        Get symbol candles from DB
        :param end_timestamp:
        :param start_timestamp:
        :param symbol_id:
        :param db_execute:
        :param limit:
        :return:
        """

        db_execute = db_execute or self.db_execute

        values = tuple(symbol_ids)
        placeholders = ', '.join(['?'] * len(symbol_ids))

        if limit is not None:
            limit_string = " LIMIT ?"
            values += (limit,)
        else:
            limit_string = ""

        where_string = ""
        if start_timestamp:
            where_string += " AND start >= ?"
            values += (start_timestamp,)
            where_string += " AND end <= ?"
            values += (end_timestamp,)

        rows = db_execute(f'SELECT * FROM candles WHERE symbol_id IN ({placeholders}){where_string}{limit_string}', values)

        if rows is None:
            return None
        ret = []
        for row in rows:
            ret.append(Candle({
                "id": row[0],
                "symbol_id": row[1],
                "start": row[2],
                "end": row[3],
                "low": row[4],
                "high": row[5],
                "open": row[6],
                "close": row[7],
                "volume": row[8],
                "vwap": row[9]
            }))
        return ret

    def api_update_symbol_candles(self, symbol: Symbol, db_execute=None):
        """
        Update symbols today candles
        :param symbol:
        :return:
        """

        existing_pairs = [(candle.float_start, candle.float_end) for candle in symbol.get_candles()]
        # todo: Need to reduce one hour because exact time raises 401 - unauthorized.
        utc_dt = datetime.now(timezone.utc)
        fetching_end_time = utc_dt.astimezone(ZoneInfo("America/New_York"))

        if candles:=symbol.get_candles():
            fetching_start_time = max(candle.start for candle in candles)
        else:
            fetching_start_time = fetching_end_time - timedelta(days=14)

        if fetching_start_time.day == fetching_end_time.day:
            time_pairs = [(fetching_start_time, fetching_end_time)]
        else:
            frame_start_time = PurchasePlanItem.get_recent_market_frame_start()
            time_pairs = [(fetching_start_time, frame_start_time), (frame_start_time, fetching_end_time)]

        total_added_candles = 0
        error_counter = 0
        for time_start, time_end in time_pairs:
            try:
                candles = self.api_get_symbol_candles(symbol, time_start, time_end)
            except Exception:
                error_counter += 1
                continue

            logger.info(f"Fetched {symbol.symbol} {len(candles)} candles from API")
            added_candles = symbol.add_candles(candles)
            total_added_candles += len(added_candles)
            for candle in added_candles:
                self.db_upsert_candle(symbol.symbol_id, candle, db_execute=db_execute)

        logger.debug(f"Sybol {symbol.symbol} {total_added_candles} candles added")
        return error_counter == 0

    def db_get_recent_candles(self, symbol:Symbol, trading_timedelta=timedelta(seconds=24*60*60), db_execute=None) -> List[Candle]:
        """
        Fetch from DB

        :param symbol:
        :return:
        """

        db_execute = db_execute or self.db_execute

        utc_dt = datetime.now(timezone.utc)
        end_time = utc_dt.astimezone(ZoneInfo("America/New_York"))
        start_time = self.get_trading_start_time_by_timedelta(end_time, trading_timedelta)
        candles = self.db_get_symbol_candles([symbol], start_time=start_time, end_time=end_time, db_execute=db_execute)
        return candles

    def get_trading_start_time_by_timedelta(self, end_time, trading_timedelta):
        """
        Find start and end time.
        Pre-Market	4:00 AM – 9:30 AM	Monday – Friday
        Regular Market	9:30 AM – 4:00 PM	Monday – Friday
        Post-Market (After-Hours)	4:00 PM – 8:00 PM	Monday – Friday
        Overnight Trading	8:00 PM – 2:00 AM	Sunday – Friday
        """

        trading_time_frames = self.trading_hours_by_day[end_time.strftime("%A")]

        for trading_frame_start_hour, trading_frame_end_hour in reversed(trading_time_frames):
            # the interesting time is before the tested time frame
            if end_time.hour < trading_frame_start_hour:
                continue

            # the interesting time is after the trade frame finished - go to end of the time frame
            if end_time.hour > trading_frame_end_hour:
                return self.get_trading_start_time_by_timedelta(end_time.replace(hour=trading_frame_end_hour, minute=59, second=59), trading_timedelta)

            # time available in the frame to trade till end_time
            frame_start_dt = end_time.replace(hour=trading_frame_start_hour, minute=0, second=0)
            available_frame_trading_time = end_time - frame_start_dt
            # available time frame larger than the requested timedelta
            if available_frame_trading_time > trading_timedelta:
                return end_time - trading_timedelta

            # 'spent' all the available time in the frame, the leftover is taken to previous trading frame
            end_time = end_time.replace(hour=trading_frame_start_hour, minute=0, second=0) - timedelta(seconds=1)
            trading_timedelta -= available_frame_trading_time
            break
        else:
            end_time -= timedelta(days=1)
            end_time = end_time.replace(hour=23, minute=59, second=59)

        return self.get_trading_start_time_by_timedelta(end_time, trading_timedelta)

    def api_get_symbol_candles(self, symbol: Symbol, start_time: datetime, end_time: datetime):
        """
        Get symbols candles
        :param symbol:
        :param start_time:
        :param end_time:
        :return:
        """

        start_time_str = self.convert_time_to_request_format(start_time)
        end_time_str = self.convert_time_to_request_format(end_time)

        logger.debug(f"Fetching Symbol's {symbol.symbol} candles from API")
        try:
            position_candles = self.get(
            f"v1/markets/candles/{symbol.symbol_id}?startTime={start_time_str}&endTime={end_time_str}&interval=OneMinute", retries=1)
        except (self.UnknownServerError, self.ResourceNotFoundError) as inst:
            start_time_str = self.convert_time_to_request_format(start_time-timedelta(hours=1))
            try:
                logger.debug(f"Retry with minus one hour: Fetching Symbol's {symbol.symbol} candles from API")

                position_candles = self.get(
                f"v1/markets/candles/{symbol.symbol_id}?startTime={start_time_str}&endTime={end_time_str}&interval=OneMinute", retries=1)
            except self.ResourceNotFoundError:
                return []

        logger.debug(f"Fetched Symbol's {symbol.symbol} candles from API")

        return [Candle(dict_src) for dict_src in position_candles["candles"]]

    def update_ineresting_symbols_market_data(self, symbol_names=None, db_execute=None):
        """
        Update cheap symbols with today data
        :return:
        """

        logger.info("Start updating the interestimg symbols based on market data")
        self.update_interesting_symbols_in_ram(symbol_names=symbol_names, db_execute=db_execute)
        self.db_update_interesting_symbols_candles(symbol_names=symbol_names, db_execute=db_execute)
        self.api_update_interesting_symbols_candles(symbol_names=symbol_names, db_execute=db_execute)
        return True

    def db_update_interesting_symbols_candles(self, symbol_names=None, db_execute=None):
        """
        Fetch candles from db and add the to the objects in RAM
        """

        logger.info("Start updating interestimg symbols Candles from local DB")

        utc_dt = datetime.now(timezone.utc)
        dt_now_new_yourk = utc_dt.astimezone(ZoneInfo("America/New_York"))
        start_time_db = dt_now_new_yourk - timedelta(days=30)
        if symbol_names:
            requested_symbols = [symbol for symbol in self.interesting_symbols.values() if symbol.symbol in symbol_names]
        else:
            requested_symbols = self.interesting_symbols.values()

        all_candles = self.db_get_symbol_candles(requested_symbols, db_execute=db_execute, start_time=start_time_db, end_time=dt_now_new_yourk)
        requested_symbols_new_candles_by_symbol_id = defaultdict(list)
        for candle in all_candles:
            requested_symbols_new_candles_by_symbol_id[candle.symbol_id].append(candle)
        for symbol_id in requested_symbols_new_candles_by_symbol_id:
            self.interesting_symbols[symbol_id].add_candles(requested_symbols_new_candles_by_symbol_id[symbol_id])

    @connected
    def api_update_interesting_symbols_candles(self, symbol_names=None, db_execute=None):
        """
        Update candles from API
        """

        if symbol_names:
            interesting_symbols = [symbol for symbol in self.interesting_symbols.values() if symbol.symbol in symbol_names]
        else:
            interesting_symbols = self.interesting_symbols.values()

        logger.info("Start updating interestimg symbols market history")
        error_counter = 0
        for i, symbol in enumerate(interesting_symbols):
            while self.pause:
                time.sleep(5)
            if self.stopped:
                raise self.StoppedException("Stopping")

            logger.info(f"Fetching symbol's {symbol.symbol} market history {i}/{len(interesting_symbols)}")
            if self.stopped:
                raise RuntimeError("Stopped execution")
            try:
                logger.debug(f"Updating Symbol {i}/{len(interesting_symbols)} {symbol.symbol}")
                if not self.api_update_symbol_candles(symbol, db_execute=db_execute):
                    error_counter += 1
            except Exception as inst:
                breakpoint()
                logger.exception(inst)
                error_counter += 1
            if error_counter > len(interesting_symbols)/2:
                raise ValueError(f"Too many errors {error_counter} out of {len(interesting_symbols)}")
        return True

    def update_interesting_symbols_in_ram(self, symbol_names=None, db_execute=None):
        """
        Update the symbols in RAM from db/api
        """

        if symbol_names:
            logger.info(f"Start updating interestimg symbols {symbol_names=} in RAM")
            existing_names = [symbol.name for symbol in self.interesting_symbols.values()]
            missing_symbol_names = [symbol_name for symbol_name in symbol_names if symbol_name not in existing_names]
            if not missing_symbol_names:
                return True
            for symbol in self.db_get_symbols(symbol_symbols=missing_symbol_names, db_execute=db_execute):
                self.interesting_symbols[symbol.symbol_id] = symbol
            return True

        logger.info("Start updating interestimg symbols in RAM")

        new_interesting_symbol_ids = [symbol.symbol_id for symbol in self.db_get_interesting_symbols(db_execute=db_execute)]

        to_del = []
        for symbol_id in self.interesting_symbols:
            if symbol_id not in new_interesting_symbol_ids:
                to_del.append(symbol_id)
        for to_del_symbol_id in to_del:
            del self.interesting_symbols[to_del_symbol_id]

        missing_new_symbol_ids = [symbol_id for symbol_id in new_interesting_symbol_ids if symbol_id not in self.interesting_symbols]

        if not missing_new_symbol_ids:
            return True

        for symbol in self.db_get_symbols(symbol_ids=missing_new_symbol_ids, db_execute=db_execute):
            self.interesting_symbols[symbol.symbol_id] = symbol
        logger.info(f"Added Missing {len(missing_new_symbol_ids)} symbols from DB into RAM")
        return True

    def db_get_interesting_symbols(self, db_execute=None):
        """
        Fetch new symbols
        """

        db_execute = db_execute or self.db_execute

        request = """
        SELECT DISTINCT s.*
        FROM symbols s
        JOIN candles c ON s.symbol_id = c.symbol_id
        WHERE c.start >= strftime('%s', 'now', '-14 days')
        AND c.close > 0.001
        AND c.close < 10.0;
        """

        rows = db_execute(request.strip("\n "), tuple())
        symbols = [Symbol({
            "id": row[0],
            "symbolId": row[1],
            "symbol": row[2],
            "description": row[3],
            "securityType": row[4],
            "listingExchange": row[5],
            "isTradable": row[6],
            "isQuotable": row[7],
            "currency": row[8]
        }) for row in rows]
        return symbols

    # pylint: disable = too-many-locals
    def make_purchase_plan(self, db_execute=None):
        """
        Plan purchase

        :return:
        """

        purchase_plan = PurchasePlan()

        logger.info("Making new purchase plan")

        orders = self.api_get_orders()
        order_symbol_ids = [order.symbol_id for order in orders]
        filtered_symbol_ids = [symbol_id for symbol_id in self.interesting_symbols if symbol_id not in order_symbol_ids]

        pp_items = []
        for symbol_id, symbol in self.interesting_symbols.items():
            if symbol_id not in filtered_symbol_ids:
                # there is an order with this symbol id
                continue
            pp_item = PurchasePlanItem(symbol=symbol)
            pp_item.init_score()
            pp_items.append(pp_item)

        pp_items = sorted(pp_items, key=lambda _item: _item._score, reverse=True)
        for pp_item in pp_items[:100]:
            purchase_plan.add_item(pp_item)

        try:
            json_data = purchase_plan.generate_json()
        except Exception as inst:
            self.pause = True
            breakpoint()
        return json_data

    @staticmethod
    def calculate_vwap_change(candles):
        """
        Calculate vwap change
        :param candles:
        :return:
        """

        candles_vwaps = [candle.vwap for candle in candles]
        min_vwap = min(candles_vwaps)
        max_vwap = max(candles_vwaps)
        if min_vwap == max_vwap:
            return 0
        vwap_change = min_vwap / max_vwap * 100
        return QuestradeAPI.calculate_price_incline(candles, lambda x: x.vwap) * vwap_change

    @connected
    def get_positions(self):
        """
        Plan purchase

        :return:
        """

        response = self.get(f"v1/accounts/{self.configuration.account}/positions")
        return [Position(dict_src) for dict_src in response["positions"] if dict_src["currentMarketValue"] is not None]

    @connected
    def get_balances(self):
        """
        Plan purchase

        :return:
        """

        response = self.get(f"v1/accounts/{self.configuration.account}/balances")
        return response

    @connected
    def api_get_orders(self, state_filter="Open", start_time=None, end_time=None):
        """
        Plan purchase

        state_filter: All, Open, Closed

        :return:
        """

        params = {"stateFilter": state_filter}
        start_time = start_time or datetime(2026, 4, 1, 0, 0, 0, tzinfo=timezone.utc)
        if start_time:
            params["startTime"] = start_time.isoformat()
        if end_time:
            params["endTime"] = end_time.isoformat()
        response = self.get(f"v1/accounts/{self.configuration.account}/orders", params=params)
        return [Order(dict_src) for dict_src in response["orders"]]

    def get_positions_without_sell_orders(self):
        """
        Plan purchase

        :return:
        """

        ret = []
        lines = []
        balances = self.get_balances()
        buying_power = balances["combinedBalances"][0]["buyingPower"]
        if buying_power > 1.0:
            lines.append(f">Time to buy! Buying power: {buying_power}")

        positions = self.get_positions()
        orders = self.api_get_orders()

        #closed_orders = self.api_get_orders(state_filter="Closed")
        #executed_sell_orders = [order for order in closed_orders if order.side == "Sell" and order.state == "Executed"]
        #ret = self.db_get_symbol(63320693)

        order_by_symbol_id = {order.symbol_id: order for order in orders if order.side == "Sell"}
        for position in positions:
            if position.symbol in self.skip_symbols:
                continue

            if position.symbol_id not in order_by_symbol_id:
                ret.append(position)
                if position.average_entry_price is None:
                    lines.append(f">Time to sell! {position.symbol} {position.open_quantity} {position.average_entry_price}")
                    continue
                sell_calculated = position.average_entry_price * 1.05
                sell_calculated = Decimal(str(sell_calculated))

                # Round to 2 decimal places
                sell_calculated_round = sell_calculated.quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

                if sell_calculated_round < sell_calculated:
                    sell_calculated_round += Decimal("0.01")

                symbol = self.db_get_symbol(symbol_symbol=position.symbol)
                if symbol is not None:
                    symbol.candles = self.db_get_recent_candles(symbol)
                    if symbol.candles:
                        today_max = max(candle.high for candle in symbol.candles)
                    else:
                        today_max = "no_trades_yet"
                else:
                    today_max = "todo"

                lines.append(f"Sell {position.symbol} count={position.open_quantity} price={sell_calculated_round}, today_max={today_max} revenue={int(sell_calculated/( Decimal(str(position.average_entry_price))/100))}%")
        if lines:
            #self.telegram_api.send(lines)
            lines = (["#################################","#################################"] + lines +
                     ["#################################", "#################################"])
        for line in lines:
            logger.info(line)
        return True

    @connected
    def cleanup_candles(self):
        """
        Cleanup candles, with duplicate times

        :return:
        """

        rows = self.db_execute('SELECT * FROM candles group by symbol_id')

        for row in rows:
            symbol = Symbol()
            symbol.symbol_id = row[1]
            candles = self.db_get_symbol_candles([symbol])
            del_candles = []
            for i, candle_a in enumerate(candles):
                for candle_b in candles[i+1:]:
                    if candle_a.start == candle_b.start and candle_a.end == candle_b.end:
                        del_candles.append(candle_b)
            for candle in del_candles:
                logger.info(f"Deleting duplicate: for symbol: {candle.symbol_id}, candle_id: {candle.id}")
                self.db_delete_candle(candle)

    def db_delete_candle(self, candle:Candle):
        """
        Delete candle

        :param candle:
        :return:
        """

        self.db_execute('DELETE FROM candles WHERE id = ?', (candle.dict_src["id"],))

    def db_delete_candles(self, candles:list[Candle]):
        """
        Delete candles

        :param candle:
        :return:
        """

        candle_ids_place_holder = ", ".join([str(candle.dict_src["id"]) for candle in candles])
        self.db_execute(f"DELETE FROM candles WHERE id IN ({candle_ids_place_holder})", tuple())

    def db_delete_symbol(self, symbol:Symbol):
        """
        Delete symbol

        :param candle:
        :return:
        """
        self.db_execute('DELETE FROM symbols WHERE symbol = ?', (symbol.symbol,))

    @connected
    def api_get_activities(self, time_start=None, time_end=None):
        """
        Fetch account activities
        :return:
        """
        if time_start is None:
            today = datetime.now(timezone.utc)
            if today.hour < 3:
                today -= timedelta(days=1)
            time_start = today.replace(hour=3, minute=0, second=0, microsecond=0)
            time_end = today.replace(hour=20, minute=0, second=0, microsecond=0)

        start_time = self.convert_time_to_request_format(time_start)
        end_time = self.convert_time_to_request_format(time_end)

        response = self.get(f"v1/accounts/{self.configuration.account}/activities?startTime={start_time}&endTime={end_time}")
        activities = response["activities"]
        return activities

    def selenium_login(self):
        """
        login via selenium
        :return:
        """

        self.selenium_api.get("https://login.questrade.com/Account/Login")
        self.selenium_api.fill_input("userId", self.configuration.user)
        time.sleep(1)
        self.selenium_api.fill_input("password", self.configuration.password)
        time.sleep(2)
        btn_container = self.selenium_api.get_element(By.CLASS_NAME, "container-action")
        btn = btn_container.find_element(By.NAME ,"button")
        btn.click()
        breakpoint()

    def selenium_open_symbol_page(self, symbol):
        """
        Open sybol page
        """

        self.selenium_api.throttled_get(f"https://myportal.questrade.com/investing/summary/quote/{symbol}")

    def selenium_sell_symbol(self, symbol:str, price:float):
        """
        Open symbol page
        :param symbol_name:
        :return:
        """

        self.selenium_open_symbol_page(symbol)
        self.selenium_press_sell_button()

        div_input = self.get_limit_price_input_div()
        if not div_input:
            raise RuntimeError("Can not find div input")

        try:
            self.selenium_fill_limit_price_input(div_input, price)
        except TimeoutError as inst_err:
            breakpoint()
            if "Limit Price" not in repr(inst_err):
                raise

        if not self.select_gtem():
            self.select_night_option()

        btn = self.selenium_api.get_shadowed_element_by_css_selector('button[data-qt*="order-entry-next-button"]')
        if not btn:
            btn = self.selenium_api.get_shadowed_element_by_text("button", "Review Order")
        try:
            btn.click()
        except ElementClickInterceptedException:
            breakpoint()
        #breakpoint()
        #btn = self.selenium_api.get_shadowed_element_by_css_selector('button[data-qt*="order-entry-sm-screen-sell-button"]')
        #if not btn:
        btn = self.selenium_api.get_shadowed_element_by_text("button", "Send order")
        btn.click()
        time.sleep(2)
        btn = self.selenium_api.get_shadowed_element_by_text("button", "Send order")
        if btn:
            btn.click()

        btn = self.selenium_api.get_shadowed_element_by_text("button", "Done")
        if not btn:
            time.sleep(2)
            btn = self.selenium_api.get_shadowed_element_by_text("button", "Done")
            if not btn:
                breakpoint()
                logger.info("Expected to find 'Done' button")

    def selenium_press_sell_button(self):
        """
        Fallback that works 50% of the time:
        if not btn:
            btn = self.selenium_api.get_shadowed_element_by_text("button", "Sell")
        """

        for _ in range(5*10):
            time.sleep(0.1)
            if self.get_limit_price_input_div():
                return True
            btn = self.selenium_api.get_shadowed_element_by_css_selector('button[data-qt*="sell-button"]')

            if not btn:
                logger.info("No Sell button found")
                if self.get_limit_price_input_div():
                    return True
                time.sleep(1)
                continue

            try:
                btn.click()
            except ElementNotInteractableException:
                logger.info("Sell button click: ElementNotInteractableException")
                btn = self.selenium_api.get_shadowed_element_by_css_selector('button[data-qt*="order-entry-next-button"]')
                breakpoint()
                continue
            except StaleElementReferenceException:
                logger.info("Sell button click: StaleElementReferenceException")
                continue

            accepted_agreement = self.check_and_dismiss_otc_popup()
            if accepted_agreement:
                continue

            if not self.clicked_on_ignore_night_sales:
                body = self.selenium_api.driver.find_element(By.TAG_NAME, "body")
                x_coord = 600  # pixels right from the element's top-left
                y_coord = 300   # pixels down from the element's top-left

                ActionChains(self.selenium_api.driver)\
                .move_to_element_with_offset(body, 0, 0)\
                .move_by_offset(x_coord, y_coord)\
                .click()\
                .perform()
                time.sleep(2)
                self.clicked_on_ignore_night_sales = True
                if self.get_limit_price_input_div():
                    return True
            else:
                time.sleep(1)
                if self.get_limit_price_input_div():
                    return True
                logger.info("todo:")
                btn = self.selenium_api.get_shadowed_element_by_css_selector('button[data-qt*="sell-button"]')

                if btn:
                    time.sleep(1)
                    continue

            logger.info("todo: Unknown state")

        div_input = self.get_limit_price_input_div()
        if not div_input:
            raise RuntimeError("Can not find div input")


    def check_and_dismiss_otc_popup(self, timeout=3):
        """
        Checks if the OTC/PINK sheet confirmation popup is present inside shadow roots.
        If found, returns True and clicks the 'OK' button.
        """

        script = """
        const searchTarget = "confirm otc/pink sheet order";

    function findAndHandlePopup(root) {
        if (!root) return false;

        // Check all elements inside the current root for matching header text
        const elements = root.querySelectorAll('*');
        for (let el of elements) {
            const text = (el.textContent || '').toLowerCase();

            // Check if this container holds the OTC popup title
            if (text.includes(searchTarget)) {
                // Look for the OK button inside the active shadow root level
                const okBtn = root.querySelector('button.ok, button[data-qt*="ok"], button');

                // Fine-tune search for the specific 'OK' text button
                const allButtons = Array.from(root.querySelectorAll('button, [role="button"]'));
                const targetBtn = allButtons.find(b => b.textContent.trim().toUpperCase() === 'OK');

                if (targetBtn) {
                    targetBtn.click();
                    return true;
                }
            }

            // Recursively traverse open shadow roots
            if (el.shadowRoot) {
                const found = findAndHandlePopup(el.shadowRoot);
                if (found) return true;
            }
        }
        return false;
    }

    return findAndHandlePopup(document);
    """
        start_time = time.time()

        while time.time() - start_time < timeout:
            popup_handled = self.selenium_api.driver.execute_script(script)
            if popup_handled:
                return True
            time.sleep(0.1)

        return False

    def get_shadow_button_by_text(self, target_text="Place a night order", timeout=5):
        """
        Get shadow button
        """

        driver = self.selenium_api.driver
        script = """
        const targetText = arguments[0];

        // Recursive function to search standard DOM and nested Shadow DOMs
        function findInShadow(root) {
            const elements = root.querySelectorAll('button, [role="button"], a, input[type="button"], input[type="submit"]');

            // 1. Check direct button elements matching the target text
            for (let el of elements) {
                if (el.textContent && el.textContent.includes(targetText)) {
                    return el;
                }
            }

            // 2. Deeply traverse all child elements to search nested shadow roots
            const allElements = root.querySelectorAll('*');
            for (let el of allElements) {
                if (el.shadowRoot) {
                    const found = findInShadow(el.shadowRoot);
                    if (found) return found;
                }
            }
            return null;
        }

        return findInShadow(document);
        """

        import time
        start_time = time.time()

        # Poll until the element renders or timeout is reached
        while time.time() - start_time < timeout:
            element = driver.execute_script(script, target_text)
            if element:
                return element
            time.sleep(0.5)

        return None

    # Usage Example:
    #btn = get_shadow_button_by_text(driver, "Place a night order")

    #if btn:
        # Perform standard Selenium interactions on the returned element
    #    btn.click()
    #else:
    #    print("Button not found within Shadow DOM.")

    def get_limit_price_input_div(self):
        """
        Get div input
        """

        for _ in range(50):
            div_input = self.get_div_input_by_label("Limit Price")
            if div_input:
                return div_input
            time.sleep(0.1)
        return None


    def selenium_fill_limit_price_input(self, div_input, price:float):
        """
        Find the input and fill the price
        """

        select_all_key = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL

        actions = ActionChains(self.selenium_api.driver)
        actions.click(div_input)  # Focus the element
        actions.key_down(select_all_key).send_keys("a").key_up(select_all_key)
        actions.send_keys(Keys.BACKSPACE)
        actions.perform()

        # Force hard clearance of value via JS to override pre-filled values/masks
        for _ in range(50):
            try:
                self.selenium_api.driver.execute_script("arguments[0].value = '';", div_input)
                break
            except JavascriptException:
                time.sleep(0.1)
        else:
            logger.warning("Was not able to hard delete contents of input")

        formatted_price = f"{price:.4f}".rstrip('0').rstrip('.') if isinstance(price, float) else str(price)
        # 4. Input the new float price
        div_input.send_keys(formatted_price)

        # 5. Dispatch UI events so Angular updates validation & recalculates "Estimated order total"
        self.selenium_api.driver.execute_script("""
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
        """, div_input)

    def select_gtem(self):
        """
        Do it using JS
        """
        self.selenium_api.driver.execute_script("""
function clickChip(root) {
    if (!root) return false;

    // Look for q-chip or label containing "Day"
    const labels = Array.from(root.querySelectorAll('q-chip, label, .q-chip-label'));
    for (let el of labels) {
        if (el.textContent && el.textContent.trim() === 'Day') {
            const chip = el.closest('q-chip') || el;
            chip.click();
            return true;
        }
    }

    // Search inside shadow roots
    for (let child of root.querySelectorAll('*')) {
        if (child.shadowRoot) {
            if (clickChip(child.shadowRoot)) return true;
        }
    }
    return false;
}
return clickChip(document);
""")

        return self.selenium_api.driver.execute_script("""
function selectGTEMOption(root) {
    if (!root) return false;

    // Find all elements containing GTEM text
    const allNodes = Array.from(root.querySelectorAll('*'));
    for (let el of allNodes) {
        if (el.children.length === 0 && el.textContent && el.textContent.includes('GTEM')) {

            // Walk up the DOM to find the clickable list item wrapper
            let target = el;
            while (target && target !== document.body) {
                // Look for common Angular dropdown item roles or classes
                if (target.getAttribute('role') === 'option' ||
                    target.classList.contains('q-dropmenu-item') ||
                    target.tagName.toLowerCase().includes('item') ||
                    target.tagName.toLowerCase().includes('option')) {
                    break;
                }
                target = target.parentElement;
            }

            // If no wrapper found, fallback to element 3 levels up
            if (!target || target === document.body) {
                target = el.parentElement?.parentElement || el;
            }

            // Fire full event chain so Angular registers the click
            ['pointerdown', 'mousedown', 'mouseup', 'click'].forEach(eventType => {
                target.dispatchEvent(new MouseEvent(eventType, {
                    bubbles: true,
                    cancelable: true,
                    view: window
                }));
            });

            return true;
        }
    }

    // Pierce Shadow DOM
    for (let child of root.querySelectorAll('*')) {
        if (child.shadowRoot) {
            if (selectGTEMOption(child.shadowRoot)) return true;
        }
    }
    return false;
}

return selectGTEMOption(document);
""")

    def select_night_option(self):
        """
        Select if exists
        """
        logger.info("Todo: change time limit selection by time.")
        pass

    def get_div_input_by_label(self, label_text):
        """
        Find using JS
        """
        js_script = """
function findInShadow(root = document) {
    // 1. Try finding input relative to the label
    let labels = Array.from(root.querySelectorAll('label'));
    for (let label of labels) {
        if (label.textContent.trim() === 'STRING_REPLACEMENT_LABEL_TEXT') {
            let container = label.closest('.oe-input-container');
            if (container) return container.querySelector('input');
        }
    }

    // 2. Direct fallback using container classes
    let el = root.querySelector('div.oe-input input');
    if (el) return el;

    // 3. Recurse down Shadow Roots
    for (let child of root.querySelectorAll('*')) {
        if (child.shadowRoot) {
            let found = findInShadow(child.shadowRoot);
            if (found) return found;
        }
    }
    return null;
}

return findInShadow();
"""
        js_script = js_script.replace("STRING_REPLACEMENT_LABEL_TEXT", label_text)
        div_input = self.selenium_api.driver.execute_script(js_script)
        return div_input


    def write_to_cache(self, lst_obj):
        """
        Write list of objects to cache
        :param lst_obj:
        :return:
        """
        ret = [obj.dict_src for obj in lst_obj]
        file_name = lst_obj[0].__class__.__name__.lower() + "s_cache.json"
        with open(self.configuration.data_directory / file_name, "w", encoding="utf-8") as file:
            json.dump(ret, file, indent=2)

    def load_from_cache(self, obj_class):
        """
        Write list of objects to cache
        :param obj_class:
        :return:
        """
        file_name = obj_class.__name__.lower() + "s_cache.json"
        with open(self.configuration.data_directory / file_name, encoding="utf-8") as file:
            order_dicts = json.load(file)
        return [obj_class(dict_src) for dict_src in order_dicts]

    # pylint: disable = too-many-locals
    def generate_profit_review(self, start_time, end_time):
        """
        Analise profit
        :return:
        """

        total_profit = 0.0
        orders = self.api_get_orders(state_filter="Closed", start_time=start_time, end_time=end_time)
        self.write_to_cache(orders)
        base_orders = self.load_from_cache(Order)
        orders = [order for order in base_orders if order.state == "Executed"]
        symbol_to_orders =  self.split_orders_by_symbol(orders)

        for symbol_id, symbol_to_orders in symbol_to_orders.items():
            symbol_buy_price = 0
            symbol_owned_quantity = 0
            commission = 0

            for order in symbol_to_orders:
                if order.placement_commission:
                    raise NotImplementedError()
                    # logger.info(f"{order.symbol_id} {order.placement_commission}")

                if order.commission_charged:
                    commission += order.commission_charged

                if order.side == "Buy":
                    buy_quantity = order.filled_quantity or order.total_quantity
                    if buy_quantity is None:
                        raise NotImplementedError()
                    buy_price_unit = order.limit_price or order.avg_exec_price
                    if buy_price_unit is None:
                        raise NotImplementedError()

                    new_quantity = symbol_owned_quantity + buy_quantity
                    symbol_buy_price =  (symbol_buy_price*symbol_owned_quantity + buy_price_unit * buy_quantity) / new_quantity
                    symbol_owned_quantity = new_quantity
                    continue

                if symbol_owned_quantity == 0:
                    # did not acquire in this time range.
                    continue

                sell_quantity = order.total_quantity
                if sell_quantity is None:
                    raise NotImplementedError()

                if symbol_owned_quantity < sell_quantity:
                    raise NotImplementedError()

                symbol_owned_quantity -= sell_quantity

                sell_price_unit = order.avg_exec_price or order.limit_price
                if sell_price_unit is None:
                    raise NotImplementedError()
                sell_price = sell_price_unit * sell_quantity
                buy_price = symbol_buy_price * sell_quantity

                profit = sell_price - buy_price - commission
                commission = 0
                total_profit += profit
                print(f"{symbol_id} {profit=} {sell_quantity=} {symbol_owned_quantity=}")
        print(f"Total profit: {total_profit}")
        return True

    @staticmethod
    def split_orders_by_symbol(orders: List[Order]):
        """
        Split orders by symbol_id
        Keep order sequence
        :param orders:
        :return:
        """

        symbol_to_orders = {}
        for order in orders:
            if order.symbol_id not in symbol_to_orders:
                symbol_to_orders[order.symbol_id] = []
            symbol_to_orders[order.symbol_id].append(order)
        return symbol_to_orders

    @connected
    def get_idle_positions(self):
        """
        Positions in huge price drop.
        """

        positions = self.get_positions()
        for position in positions:
            if position.average_entry_price*0.6 > position.current_price:
                print(position.symbol, position.average_entry_price, position.current_price)
        return True

    @connected
    def run_selenium_sell_routine(self):
        """
        Perform automatic acquiring
        """

        ret = []
        lines = []

        positions = self.get_positions()
        existing_orders = self.api_get_orders()
        orders_to_place = []

        sell_order_by_symbol_id = {order.symbol_id: order for order in existing_orders if order.side == "Sell"}
        for position in positions:
            if position.symbol in self.skip_symbols:
                continue

            if position.symbol_id not in sell_order_by_symbol_id:
                ret.append(position)

                if position.average_entry_price is None:
                    lines.append(f">Time to sell! {position.symbol} {position.open_quantity} {position.average_entry_price=}")
                    continue

                if order:=self.get_sell_order(position):
                    orders_to_place.append(order)
                # lines.append(f"Sell {position.symbol} count={position.open_quantity} price={sell_calculated_round}, today_max={today_max} revenue={int(sell_calculated/( Decimal(str(position.average_entry_price))/100))}%")

        self.selenium_login()
        for i, order_to_place in enumerate(orders_to_place):
            # https://www.questrade.com/api/documentation/rest-operations/market-calls/markets-quotes-options
            logger.info(f"Selling symbol {order_to_place.symbol} {i}/{len(orders_to_place)}")
            self.selenium_sell_symbol(order_to_place.symbol, order_to_place.limit_price)

        return True
    
    def get_sell_order(self, position):
        """
        Get the order 
        """

        sell_calculated = position.average_entry_price * 1.05
        sell_calculated = Decimal(str(sell_calculated))

        # Round to 2 decimal places
        sell_calculated_round = sell_calculated.quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

        if sell_calculated_round < sell_calculated:
            sell_calculated_round += Decimal("0.01")
                
        # default in case there are no candles
        today_max = sell_calculated_round
        symbol = self.db_get_symbol(symbol_symbol=position.symbol)
        if symbol is not None:
            symbol.candles = self.db_get_recent_candles(symbol)
            if symbol.candles:
                today_max = max(candle.high for candle in symbol.candles) 
            else:
                return None 
                # todo: Check how to handle the problem when there are no candles during last day
                #symbol.candles = self.db_get_recent_candles(symbol, trading_timedelta=timedelta(seconds=24*60*60*7))
                #raise NotImplementedError()
            
        if today_max < sell_calculated_round * Decimal("0.6"):
            sell_calculated_round = today_max 

        order = Order({})
        order.symbol = position.symbol
        order.symbol_id = position.symbol_id
        order.limit_price = sell_calculated_round
        return order

    @connected
    def run_selenium_sell_routine_ng(self):
        """
        Perform automatic acquiring
        """

        ret = []
        lines = []

        positions = self.get_positions()
        existing_orders = self.api_get_orders()
        orders_to_place = []

        sell_order_by_symbol_id = {order.symbol_id: order for order in existing_orders if order.side == "Sell"}
        for position in positions:
            if position.symbol in self.skip_symbols:
                continue

            if position.symbol_id not in sell_order_by_symbol_id:
                ret.append(position)

                if position.average_entry_price is None:
                    lines.append(f">Time to sell! {position.symbol} {position.open_quantity} {position.average_entry_price=}")
                    continue
                if order:=self.get_sell_order(position):
                    orders_to_place.append(order)
                # lines.append(f"Sell {position.symbol} count={position.open_quantity} price={sell_calculated_round}, today_max={today_max} revenue={int(sell_calculated/( Decimal(str(position.average_entry_price))/100))}%")

        for i, order_to_place in enumerate(orders_to_place):
            # https://www.questrade.com/api/documentation/rest-operations/market-calls/markets-quotes-options
            logger.info(f"Selling symbol {order_to_place.symbol} {i}/{len(orders_to_place)}")
            self.selenium_sell_symbol_ng(order_to_place.symbol, order_to_place.limit_price)

        return True

    @connected
    def run_the_main_loop(self):
        """
        Run the main loop
        """

        sleep_time = 30
        refresh_time = 4*60
        try:
            for _ in range(int(60*60*16 / refresh_time)):
                if self.stopped:
                    break
                while self.pause:
                    time.sleep(5)
                self.async_make_purchase_plan()

                for _ in range(int(refresh_time/sleep_time)):
                    while self.pause:
                        time.sleep(5)
                    if self.stopped:
                        break
                    self.get_positions_without_sell_orders()
                    logger.info(f"Sleeping {sleep_time} seconds...")
                    time.sleep(sleep_time)
        finally:
            self.stop()

    @connected
    def async_make_purchase_plan(self):
        """
        Run the purchase plan async
        """

        if self.active_purchase_planning:
            return True

        thread = threading.Thread(target=self.make_purchase_plan_helper)
        thread.start()
        return True

    def make_purchase_plan_helper(self):
        """
        Thread task
        """

        self.active_purchase_planning = True
        logger.info("Start working on Purchase Plan")
        try:
            connection = sqlite3.connect(self.configuration.db_file_path)
            cursor = connection.cursor()

            def db_execute(*args, **kwargs):
                return (self.db_execute(*args, db_connection=connection, db_cursor=cursor, **kwargs))

            self.update_ineresting_symbols_market_data(db_execute=db_execute)
            ret = self.make_purchase_plan(db_execute=db_execute)
            if ret:
                now = datetime.now()
                ret = [now.strftime("%Y-%m-%d %H:%M:%S")] + ret
                with open(self.configuration.purchase_plan_file_path, "w", encoding="utf-8") as file_handler:
                    json.dump(ret, file_handler, indent=4)
        except Exception as inst_err:
            tb_str = "".join(traceback.format_exception(type(inst_err), inst_err, inst_err.__traceback__))
            logger.error(f"An error occurred: {inst_err}\nTraceback:\n{tb_str}")
            return False
        finally:
            self.active_purchase_planning = False
            cursor.close()
            connection.close()
        return True

    def get_db_statistics(self):
        """
        Get some data to see the state
        """
        lst_ret = []
        response = self.db_execute(
                    "select count(symbol_id) from candles", tuple()
                )
        all_candles = response[0][0]
        assert all_candles
        ##########
        now = datetime.now(timezone.utc).astimezone(ZoneInfo("America/New_York"))
        start_time = now - timedelta(days=30)
        start_timestamp = start_time.timestamp()
        response = self.db_execute(
                    f"select count(id) from candles where start < {start_timestamp}", tuple()
                )
        over_month_candles = response[0][0]
        assert over_month_candles
        ##############
        missing_candles = self.db_execute('''SELECT s.symbol_id
            FROM symbols s
            LEFT JOIN candles c ON s.symbol_id = c.symbol_id
            WHERE c.symbol_id IS NULL
            ''', tuple())
        missing_candles_len = len(missing_candles)
        assert missing_candles_len

        return ret

    def stop(self):
        """
        Stop self
        """

        self.stopped = True

    def db_move_candles_to_historical_data(self):
        """
        Copy candles from new to historical data.
        """

        one_week_limit = datetime.now(timezone.utc) - timedelta(days=7)
        query = 'SELECT * FROM symbols'
        rows = self.db_historical_data_execute(query, tuple())
        historical_symbols_by_symbols = {row[2]: row for row in rows}

        new_symbols = self.db_get_symbols()
        len_new_symbols = len(new_symbols)
        for i, symbol in enumerate(new_symbols):
            logger.info(f"Moving candles for symbol {symbol.symbol}. {i}/{len_new_symbols}")

            if symbol.symbol not in historical_symbols_by_symbols:
                self.db_upsert_symbol(symbol, db_execute=self.db_historical_data_execute)
            new_candles = self.db_get_symbol_candles([symbol])
            if not new_candles:
                self.db_delete_symbol(symbol)
                continue

            if max(new_candle.start for new_candle in new_candles) < one_week_limit:
                self.db_delete_candles(new_candles)
                self.db_delete_symbol(symbol)
                continue

            logger.info(f"Fetched {len(new_candles)} candles for symbol {symbol.symbol}")
            historical_candles = self.db_get_symbol_candles([symbol], db_execute=self.db_historical_data_execute)
            logger.info(f"Fetched {len(historical_candles)} historical candles for symbol {symbol.symbol}")

            historical_candles_start_dates = [historical_candle.start for historical_candle in historical_candles]
            candles_added_to_historical_data = 0
            for new_candle in new_candles:
                if new_candle.start in historical_candles_start_dates:
                    continue
                candles_added_to_historical_data += 1
                self.db_upsert_candle(symbol.symbol_id, new_candle, db_execute=self.db_historical_data_execute)
            if candles_added_to_historical_data > 0:
                logger.info(f"Added symbol '{symbol.symbol}' {candles_added_to_historical_data} candles to historical_data")

            self.db_delete_candles(new_candles)
            self.db_delete_symbol(symbol)
            self.db_execute("VACUUM", tuple())

    def db_move_candles_from_historical_data(self):
        """
        Copy candles from new to historical data.
        self.db_execute("DELETE from candles", tuple())
        self.db_execute("DELETE from symbols", tuple())

        """

        utc_dt = datetime.now(timezone.utc)
        end_time = utc_dt.astimezone(ZoneInfo("America/New_York"))
        start_time = end_time - timedelta(days=31)
        week_limit = end_time - timedelta(days=7)
        chunk_size = 1000

        all_symbols = self.db_get_symbols(db_execute=self.db_historical_data_execute)
        for i in range(0, len(all_symbols), chunk_size):
            symbols = all_symbols[i:i+chunk_size]
            logger.info(f"Moving {chunk_size} historical data symbols. {i}/{len(all_symbols)}")

            candles = self.db_get_symbol_candles(symbols, db_execute=self.db_historical_data_execute, start_time=start_time, end_time=end_time)
            if not candles:
                continue

            if max(candle.start for candle in candles) < week_limit:
                continue

            by_symbol_id = defaultdict(list)
            for candle in candles:
                by_symbol_id[candle.symbol_id].append(candle)

            len_symbols = len(symbols)
            for indx, symbol in enumerate(symbols):
                logger.info(f"From chunk: {indx}/{len_symbols}")
                symbol_candles = by_symbol_id[symbol.symbol_id]
                if not symbol_candles:
                    continue
                if max(candle.start for candle in symbol_candles) < week_limit:
                    continue
                if min(candle.low for candle in symbol_candles) > self.configuration.max_trading_value:
                    continue
                if max(candle.high for candle in symbol_candles) < self.configuration.min_trading_value:
                    continue

                self.db_upsert_symbol(symbol, keep_db_id=True)
                logger.info(f"Adding symbol {symbol.symbol}")
                for candle in candles:
                    self.db_upsert_candle(symbol.symbol_id, candle, keep_db_id=True)
                logger.info(f"Adding symbol {symbol.symbol} candles")

    def selenium_sell_symbol_ng(self, symbol:str, price:float):
        """
        Open symbol page
        :param symbol_name:
        :return:
        """
        
        login = Login(self.selenium_api, self.configuration.user, self.configuration.password)

        sell_state_order_details = OrderDetailsFilled(self.selenium_api, f"Sell {symbol=}, {price=}", OrderDetailsFilled.Order.SELL, symbol, price, parent=login)

        desired_state = OrderPlaced(self.selenium_api, f"Sell {symbol=}, {price=}", symbol, price, parent=sell_state_order_details)

        desired_state.reach_state()

    class UnknownServerError(RuntimeError):
        """
        API/UI Server Returned error which can not be identified during runtime
        """

    class ResourceNotFoundError(RuntimeError):
        """
        Raised when a requested resource does not exist
        """

    class StoppedException(RuntimeError):
        """
        Excution Stopped
        """
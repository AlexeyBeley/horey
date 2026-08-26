"""
Shamelessly stolen from:
https://questrade.com/lukecyca/pyslack
"""

# pylint: disable = too-many-lines

import sqlite3
import platform
import time
import threading
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
from typing import List
from decimal import Decimal, ROUND_HALF_UP
from scipy import stats

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import  StaleElementReferenceException, JavascriptException
from selenium.webdriver.common.action_chains import ActionChains


from horey.h_logger import get_logger
from horey.selenium_api.selenium_api import SeleniumAPI
from horey.questrade_api.questrade_api_configuration_policy import (
    QuestradeAPIConfigurationPolicy,
)
from horey.questrade_api.items import Symbol, Candle, Position, Order

logger = get_logger(level="DEBUG")


class QuestradeAPI:
    """
    Main Class.
    https://www.questrade.com/api/documentation/getting-started
    """

    def __init__(self, configuration: QuestradeAPIConfigurationPolicy = None):
        self.configuration = configuration
        self.access_token = self.configuration.token
        self.api_server = configuration.api_server
        self._db_connection = None
        self._db_cursor = None
        self._selenium_api = None
        self.skip_symbols = []
        self.clicked_on_ignore_night_sales = False

    @property
    def selenium_api(self):
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

        response.raise_for_status()

        try:
            return response.json()
        except Exception:
            return response.text

    def get(self, request_path, params=None):
        """
        Compose and send GET request.

        :param request_path:
        :return:
        """
        try:
            return self._get(request_path, params=params)
        except Exception as inst:
            if "401" not in repr(inst):
                raise
            self.connect_api(reconnect=True)
            return self._get(request_path, params=params)

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
            response = self.connect_from_cache(response_file_path, reconnect=reconnect)
            if response is None:
                return True
        else:
            base_url = "https://login.questrade.com/oauth2/token"
            params = {
                "grant_type": "refresh_token",
                "refresh_token": self.configuration.token
            }

            response = requests.get(base_url, params=params, timeout=60)
            response.raise_for_status()
            response = response.json()

        response["expires_at"] = (datetime.now(tz=timezone.utc) + timedelta(seconds=response["expires_in"])).timestamp()

        with open(response_file_path, "w", encoding="utf-8") as file_handler:
            json.dump(response, file_handler)

        self.access_token = response["access_token"]
        logger.info(f"Connected to Questtrade API, new token: {self.access_token}")

        self.api_server = response['api_server'].rstrip("/")  # e.g., https://api01.iq.questrade.com/
        logger.info(f"Connected to Questtrade API, new server: {self.api_server}")
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

        response_file_path.unlink()
        refresh_token = response["refresh_token"]
        auth_url = f"https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token={refresh_token}"
        response = requests.get(auth_url, timeout=60).json()
        return response

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
        self.db_cursor.execute(
                f"select symbol_id from candles where vwap <= {max_price} and vwap >= {min_price} AND start >= {start_timestamp}  group by symbol_id"
            )
        response = self.db_cursor.fetchall()

        symbols = []
        for line in response:
            symbol = self.db_get_symbol(line[0])
            if not symbol:
                logger.error(f"Symbol {line[0]} not found in DB")
                continue
            symbol.candles = self.db_get_symbol_candles(symbol.symbol_id)
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

        with sqlite3.connect(self.configuration.db_file_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"select * from candles{where_string}"
            )
            response = cursor.fetchall()

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

        with sqlite3.connect(self.configuration.db_file_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
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
            conn.commit()
        logger.info(f"Table symbols created in {self.configuration.db_file_path}' database")
        return True

    def provision_db_candles_table(self):
        """
        Create table

        :return:
        """

        with sqlite3.connect(self.configuration.db_file_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
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
            conn.commit()
        logger.info(f"Table candles created in {self.configuration.db_file_path}' database")
        return True

    def db_upsert_symbol(self, symbol: Symbol, cursor=None):
        """
        Update or insert symbol into DB
        :param symbol:
        :return:
        """

        logger.info(f"Upserting symbol {symbol.symbol} into {self.configuration.db_file_path}' database")
        if not cursor:
            with sqlite3.connect(self.configuration.db_file_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO symbols (symbol_id, symbol, description, security_type, listing_exchange, is_tradable, is_quotable, currency)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (symbol.symbol_id, symbol.symbol, symbol.description, symbol.security_type,
                      symbol.listing_exchange, symbol.is_tradable, symbol.is_quotable, symbol.currency))
                conn.commit()
        else:
            cursor.execute('''
                               INSERT OR REPLACE INTO symbols (symbol_id, symbol, description, security_type, listing_exchange, is_tradable, is_quotable, currency)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                           ''', (symbol.symbol_id, symbol.symbol, symbol.description, symbol.security_type,
                                 symbol.listing_exchange, symbol.is_tradable, symbol.is_quotable, symbol.currency))

        logger.info(f"Symbol {symbol.symbol} upserted into {self.configuration.db_file_path}' database")
        return True

    def db_execute(self, query, args):
        """
        Execute query
        :param query:
        :param args:
        :return:
        """

        self.db_cursor.execute(query, args)
        self.db_connection.commit()
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
    def db_cursor(self):
        """
        Get DB cursor
        :param self:
        :return:
        """
        if self._db_cursor is None:
            self._db_cursor = self.db_connection.cursor()
        return self._db_cursor

    def db_upsert_candle(self, symbol_id, candle: Candle, db_cursor=None):
        """
        Update or insert candle into DB
        :param cursor:
        :param symbol_id:
        :param candle:
        :return:
        """

        if not db_cursor:
            self.db_execute('''
                    INSERT OR REPLACE INTO candles (symbol_id, start, end, low, high, open, close, volume, vwap)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (symbol_id, candle.float_start, candle.float_end, candle.low, candle.high, candle.open,
                          candle.close, candle.volume, candle.vwap))
        else:
            db_cursor.execute('''
                INSERT OR REPLACE INTO candles (symbol_id, start, end, low, high, open, close, volume, vwap)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (symbol_id, candle.float_start, candle.float_end, candle.low, candle.high, candle.open, candle.close,
                  candle.volume,
                  candle.vwap))

        return True

    def db_get_symbol(self, symbol_id=None, db_cursor=None, symbol_symbol=None):
        """
        Get symbol from DB
        :param db_cursor:
        :param symbol_id:
        :return:
        """

        logger.debug(f"Fetching symbol {symbol_id} from {self.configuration.db_file_path}' database")
        db_cursor = db_cursor or self.db_cursor

        return self.db_get_symbol_raw(symbol_id, db_cursor, symbol_symbol=symbol_symbol)

    def db_get_symbol_raw(self, symbol_id, cursor, symbol_symbol=None):
        """
        Get symbol from DB
        :param cursor:
        :param symbol_id:
        :return:
        """

        if symbol_symbol:
            cursor.execute('SELECT * FROM symbols WHERE symbol = ?', (symbol_symbol,))

        else:
            cursor.execute('SELECT * FROM symbols WHERE symbol_id = ?', (symbol_id,))
        rows = cursor.fetchall()
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

    def db_get_symbol_candles(self, symbol_id, limit=None, start_time:datetime=None, end_time:datetime=None, db_cursor=None):
        """
        Get symbol candles from DB

        :param end_time:
        :param start_time:
        :param cursor:
        :param limit:
        :param symbol_id:
        :return:
        """

        db_cursor = db_cursor or self.db_cursor

        end_timestamp = end_time.timestamp() if end_time else None

        start_timestamp = start_time.timestamp() if start_time else None

        return self.db_get_symbol_candles_raw(symbol_id, db_cursor, limit=limit, start_timestamp=start_timestamp, end_timestamp=end_timestamp)

    def db_get_symbol_candles_raw(self, symbol_id, cursor, limit=None, start_timestamp:float=None, end_timestamp:float=None):
        """
        Get symbol candles from DB
        :param end_timestamp:
        :param start_timestamp:
        :param symbol_id:
        :param cursor:
        :param limit:
        :return:
        """

        if limit is not None:
            limit_string = f" LIMIT {limit}"
        else:
            limit_string = ""

        where_string = ""
        if start_timestamp:
            where_string += f" AND start >= {start_timestamp}"
            where_string += f" AND end <= {end_timestamp}"

        cursor.execute(f'SELECT * FROM candles WHERE symbol_id = ?{where_string}{limit_string}', (symbol_id,))
        rows = cursor.fetchall()
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

    def update_symbol_today_candles(self, symbol: Symbol, db_cursor=None):
        """
        Update symbols today candles
        :param symbol:
        :return:
        """

        db_cursor = db_cursor or self.db_cursor

        existing_candles = self.db_get_today_candles(symbol, db_cursor=db_cursor)
        existing_pairs = [(candle.float_start, candle.float_end) for candle in existing_candles]
        today = datetime.now(timezone.utc)
        if today.hour < 3:
            today -= timedelta(days=1)

        utc_today_3am = today.replace(hour=3, minute=0, second=0, microsecond=0)
        utc_today_8pm = today.replace(hour=20, minute=0, second=0, microsecond=0)

        candles = self.api_get_symbol_candles(symbol, utc_today_3am, utc_today_8pm)
        upserted = 0
        for candle in candles:
            if (candle.float_start, candle.float_end) in existing_pairs:
                continue
            upserted += 1 
            self.db_upsert_candle(symbol.symbol_id, candle, db_cursor=db_cursor)
        
        logger.debug(f"Sybol {symbol.symbol_id} {upserted} candles updated")
        return candles

    def db_get_today_candles(self, symbol:Symbol, db_cursor=None) -> List[Candle]:
        """
        Fetch from DB

        :param symbol:
        :return:
        """

        db_cursor = db_cursor or self.db_cursor
        today = datetime.now(timezone.utc)

        if today.hour < 5:
            today -= timedelta(days=1)

        # todo:
        #today -= timedelta(days=2)

        utc_today_3am = today.replace(hour=3, minute=0, second=0, microsecond=0)
        utc_today_8pm = today.replace(hour=20, minute=0, second=0, microsecond=0)


        candles = self.db_get_symbol_candles(symbol.symbol_id, start_time=utc_today_3am, end_time=utc_today_8pm, db_cursor=db_cursor)
        return candles

    def api_get_symbol_candles(self, symbol: Symbol, start_time: datetime, end_time: datetime):
        """
        Get symbols candles
        :param symbol:
        :param start_time:
        :param end_time:
        :return:
        """


        start_time = self.convert_time_to_request_format(start_time)
        end_time = self.convert_time_to_request_format(end_time)

        logger.debug(f"Fetching Symbol's {symbol.symbol} candles from API")
        try:
            position_candles = self.get(
            f"v1/markets/candles/{symbol.symbol_id}?startTime={start_time}&endTime={end_time}&interval=OneMinute")
        except Exception as inst:
            if "Not Found for url" in repr(inst):
                logger.error(f"Failed to fetch candles for symbol {symbol.symbol}")
                return []
            raise
        logger.debug(f"Fetched Symbol's {symbol.symbol} candles from API")

        return [Candle(dict_src) for dict_src in position_candles["candles"]]

    @connected
    def update_cheap_candles_with_today_data(self, symbol_name=None, db_cursor=None):
        """
        Update cheap symbols with today data
        :return:
        """

        db_cursor = db_cursor or self.db_cursor

        error_counter = 0
        cheapest_stocks = self.sort_cheapest_by_price()
        symbol_ids = [symbol[1] for symbol in cheapest_stocks if (symbol_name is None) or (symbol[0] == symbol_name)]
        for i, symbol_id in enumerate(symbol_ids):
            symbol = self.db_get_symbol(symbol_id, db_cursor=db_cursor)
            try:
                logger.debug(f"Updating Symbol {i}/{len(symbol_ids)} {symbol.symbol}")
                self.update_symbol_today_candles(symbol, db_cursor=db_cursor)
            except Exception:
                self.connect_api(reconnect =True)
                error_counter += 1
        if error_counter > len(symbol_ids)/2:
            raise ValueError(f"Too many errors {error_counter} out of {len(symbol_ids)}")
        return True

    # pylint: disable = too-many-locals
    def make_purchase_plan(self, symbol_name=None, db_cursor=None):
        """
        Plan purchase

        :return:
        """
        
        logger.info("Making new purchase plan")

        db_cursor = db_cursor or self.db_cursor
        position_symbol_ids = [position.symbol_id for position in self.get_positions()]

        cheapest_stocks = self.sort_cheapest_by_price()
        symbol_ids = [symbol[1] for symbol in cheapest_stocks if symbol[1] not in position_symbol_ids and
                      ((symbol_name is None) or (symbol[0] == symbol_name))]
        orders = self.api_get_orders()
        order_symbol_ids = [order.symbol_id for order in orders]
        symbol_ids = [symbol_id for symbol_id in symbol_ids if symbol_id not in order_symbol_ids]

        symbols = []

        len_symbol_ids = len(symbol_ids)
        for i, symbol_id in enumerate(symbol_ids):
            logger.debug(f"Fetching {i}/{len_symbol_ids}")

            symbol = self.db_get_symbol(symbol_id, db_cursor=db_cursor)
            symbol.candles = self.db_get_today_candles(symbol, db_cursor=db_cursor)
            if not symbol.candles:
                continue
            symbols.append(symbol)

        filtered_symbols = []
        for symbol in symbols:
            # todo: Check low and high instead vwap
            #symbol.price_change = self.calculate_vwap_change(symbol.candles)
            symbol.price_change = self.calculate_low_change(symbol.candles)
            symbol.slope = self.calculate_price_slope(symbol.candles, lambda x: x.low)


            symbol.absolute_low = min(candle.low for candle in symbol.candles)
            symbol.absolute_high = max(candle.high for candle in symbol.candles)
            if symbol.price_change <= 0:
                continue
            if len(symbol.candles) < 10:
                continue
            filtered_symbols.append(symbol)

        str_ret = ""
        # todo: old
        #for i, symbol in enumerate(sorted(filtered_symbols, key=lambda x: abs(x.price_change))):
        for i, symbol in enumerate(sorted(filtered_symbols, key=lambda x: abs(x.slope), reverse=True)):
            str_ret += f"[{i+1}] {symbol.symbol}, abs_low={symbol.absolute_low}, price_change={symbol.price_change}, deals={len(symbol.candles)}\n"

        with open(self.configuration.data_directory/ "purchase_plan.txt", "w", encoding="utf-8") as file:
            file.write(str_ret)
        print(f"Purchase_plan is ready: {self.configuration.data_directory/ 'purchase_plan.txt'}")
        return True

    @staticmethod
    def calculate_low_change(candles):
        """
        Calculate vwap change
        :param candles:
        :return:
        """
        candles_lows = [candle.low for candle in candles]
        min_price = min(candles_lows)
        max_price = max(candles_lows)
        if min_price == max_price:
            return 0
        price_change = min_price / max_price * 100
        return QuestradeAPI.calculate_price_incline(candles, lambda x: x.low) * price_change

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

    @staticmethod
    def calculate_price_incline(candles, callback_price):
        """
        Create a line on the vwap change and calculate incline.
        :param callback_price:
        :param candles:
        :return:
        """

        slope = QuestradeAPI.calculate_price_slope(candles, callback_price)
        return 1 if (slope > 0) else -1

    @staticmethod
    def calculate_price_slope(candles, callback_price):
        """
        Create a line on the vwap change and calculate incline.
        :param callback_price:
        :param candles:
        :return:
        """

        x_data = [(candle.float_end + candle.float_start) / 2 for candle in candles]
        y_data = [callback_price(candle) for candle in candles]
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
        if (intercept, r_value, p_value, std_err):
            pass
        return slope

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
                    symbol.candles = self.db_get_today_candles(symbol)
                    if symbol.candles:
                        today_max = max(candle.high for candle in symbol.candles)
                    else:
                        today_max = "no_trades_yet"
                else:
                    today_max = "todo"

                lines.append(f"Sell {position.symbol} count={position.open_quantity} price={sell_calculated_round}, today_max={today_max} revenue={int(sell_calculated/( Decimal(str(position.average_entry_price))/100))}%")
        if lines:
            lines = (["#################################","#################################"] + lines +
                     ["#################################", "#################################"])
        for line in lines:
            logger.info(line)
        return True

    @connected
    def db_get_all_symbols(self):
        """
        Fetch all symbols from DB
        :return:
        """

        self.db_cursor.execute('SELECT * FROM candles')
        rows = self.db_cursor.fetchall()
        if rows is None:
            return None
        ret = []
        for row in rows:
            ret.append(Symbol({
                "symbol": row[1],
                "symbolId": row[2],
                "securityType": row[3],
                "isTradable": row[4],
                "isQuotable": row[5],
                "currency": row[6],
                "listingExchange": row[7],
                "description": row[8],
                "id": row[0]
            }))
        return ret

    @connected
    def cleanup_candles(self):
        """
        Cleanup candles, with duplicate times

        :return:
        """

        self.db_cursor.execute('SELECT * FROM candles group by symbol_id')
        rows = self.db_cursor.fetchall()

        for row in rows:
            candles = self.db_get_symbol_candles(row[1])
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
        self.db_cursor.execute('DELETE FROM candles WHERE id = ?', (candle.dict_src["id"],))
        self.db_connection.commit()

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

        for _ in range(5*10):
            time.sleep(0.1)
            btn = self.selenium_api.get_shadowed_element_by_css_selector('button[data-qt*="sell-button"]')
            #if not btn:
            #    btn = self.selenium_api.get_shadowed_element_by_text("button", "Sell")
            if not btn:
                continue

            try:
                btn.click()
            except StaleElementReferenceException:
                continue

            div_input = self.get_limit_price_input_div()
            if not div_input:
                btn = self.selenium_api.get_shadowed_element_by_css_selector('button[data-qt*="sell-button"]')
                if btn:
                    btn.click()
                if not self.clicked_on_ignore_night_sales:
                    breakpoint()
                    body = self.selenium_api.driver.find_element(By.TAG_NAME, "body")
                    x_coord = 600  # pixels right from the element's top-left
                    y_coord = 300   # pixels down from the element's top-left

                    ActionChains(self.selenium_api.driver)\
                    .move_to_element_with_offset(body, 0, 0)\
                    .move_by_offset(x_coord, y_coord)\
                    .click()\
                    .perform()

                    self.clicked_on_ignore_night_sales = True

                div_input = self.get_limit_price_input_div()
                if not div_input:
                    raise RuntimeError("Can not find div input")

            try:
                self.selenium_fill_limit_price_input(div_input, price)
            except TimeoutError as inst_err:
                if "Limit Price" not in repr(inst_err):
                    raise
                continue

            break

        else:
            raise TimeoutError("Reached timeout waiting for 'Sell' button to appear")

        self.select_gtem()

        btn = self.selenium_api.get_shadowed_element_by_css_selector('button[data-qt*="order-entry-next-button"]')
        if not btn:
            btn = self.selenium_api.get_shadowed_element_by_text("button", "Review Order")
        btn.click()
        #breakpoint()
        #btn = self.selenium_api.get_shadowed_element_by_css_selector('button[data-qt*="order-entry-sm-screen-sell-button"]')
        #if not btn:
        btn = self.selenium_api.get_shadowed_element_by_text("button", "Send order")
        btn.click()
        time.sleep(2)

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

        self.selenium_api.driver.execute_script("""
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
                    breakpoint()
                    logger.info(f"{order.symbol_id} {order.placement_commission}")

                if order.commission_charged:
                    commission += order.commission_charged

                if order.side == "Buy":
                    buy_quantity = order.filled_quantity or order.total_quantity
                    if buy_quantity is None:
                        breakpoint()
                    buy_price_unit = order.limit_price or order.avg_exec_price
                    if buy_price_unit is None:
                        breakpoint()

                    new_quantity = symbol_owned_quantity + buy_quantity
                    symbol_buy_price =  (symbol_buy_price*symbol_owned_quantity + buy_price_unit * buy_quantity) / new_quantity
                    symbol_owned_quantity = new_quantity
                    continue

                if symbol_owned_quantity == 0:
                    # did not acquire in this time range.
                    continue

                sell_quantity = order.total_quantity
                if sell_quantity is None:
                    breakpoint()

                if symbol_owned_quantity < sell_quantity:
                    breakpoint()

                symbol_owned_quantity -= sell_quantity

                sell_price_unit = order.avg_exec_price or order.limit_price
                if sell_price_unit is None:
                    breakpoint()
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

        self.selenium_login()
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
                sell_calculated = position.average_entry_price * 1.05
                sell_calculated = Decimal(str(sell_calculated))

                # Round to 2 decimal places
                sell_calculated_round = sell_calculated.quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

                if sell_calculated_round < sell_calculated:
                    sell_calculated_round += Decimal("0.01")

                symbol = self.db_get_symbol(symbol_symbol=position.symbol)
                if symbol is not None:
                    symbol.candles = self.db_get_today_candles(symbol)
                    today_max = max(candle.high for candle in symbol.candles) if symbol.candles else "no_trades_yet"
                else:
                    today_max = "todo"

                order = Order({})
                order.symbol = position.symbol
                order.symbol_id = position.symbol_id
                order.limit_price = sell_calculated_round
                orders_to_place.append(order)
                lines.append(f"Sell {position.symbol} count={position.open_quantity} price={sell_calculated_round}, today_max={today_max} revenue={int(sell_calculated/( Decimal(str(position.average_entry_price))/100))}%")

        for order_to_place in orders_to_place:
            # https://www.questrade.com/api/documentation/rest-operations/market-calls/markets-quotes-options
            self.selenium_sell_symbol(order_to_place.symbol, order_to_place.limit_price)

        return True

    @connected
    def run_the_main_loop(self):
        """
        Run the main loop
        """

        sleep_time = 30
        refresh_time = 5*60

        for _ in range(int(60*60*16 / refresh_time)):
            self.async_make_purchase_plan()

            for _ in range(int(refresh_time/sleep_time)):
                self.get_positions_without_sell_orders()
                logger.info(f"Sleeping {sleep_time} seconds...")
                time.sleep(sleep_time)

    @connected
    def async_make_purchase_plan(self):
        """
        Run the purchase plan async
        """

        def async_make_purchase_plan_helper():
            """
            Thread task
            """

            logger.info("Start working on Purchase Plan")
            connection = sqlite3.connect(self.configuration.db_file_path)
            cursor = connection.cursor()
            self.update_cheap_candles_with_today_data(db_cursor=cursor)
            self.make_purchase_plan(db_cursor=cursor)
            cursor.close()
            connection.close()

        thread = threading.Thread(target=async_make_purchase_plan_helper)
        thread.start()

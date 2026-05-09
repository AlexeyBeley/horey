"""
Shamelessly stolen from:
https://questrade.com/lukecyca/pyslack
"""
import sqlite3
import time
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
from typing import List
from scipy import stats
from decimal import Decimal, ROUND_HALF_UP

import requests
from selenium.webdriver.common.by import By

from horey.h_logger import get_logger
from horey.questrade_api.questrade_api_configuration_policy import (
    QuestradeAPIConfigurationPolicy,
)
from horey.questrade_api.items import Symbol, Candle, Position, Order

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
        self._db_connection = None
        self._db_cursor = None
        self._selenium_api = None

    @property
    def selenium_api(self):
        """
        Getter for selenium_api

        :return:
        """

        if self._selenium_api is None:
            from horey.selenium_api.selenium_api import SeleniumAPI
            self._selenium_api = SeleniumAPI()
            self._selenium_api.connect()
        return self._selenium_api

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
        response = requests.get(request, headers=headers, params=params)

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
            self.connect(reconnect=True)
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

    def connect(self, reconnect=False):
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

            response = requests.get(base_url, params=params).json()

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
        response = requests.get(auth_url).json()
        return response

    def get_accounts(self):
        """
        Get accounts

        :return:
        """

        accounts = self.get(f"v1/accounts")
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

    def get_all_stocks_daily_history(self):
        """
        Get all stocks history.
        :return:
        """
        raise NotImplementedError("This is a heavy operation, use with care")
        start_time = datetime(year=2026, month=4, day=13, hour=3, minute=0, second=0, tzinfo=timezone.utc)
        end_time = datetime(year=2026, month=4, day=13, hour=21, minute=2, second=0, tzinfo=timezone.utc)
        data_directory = self.configuration.data_directory / "daily_history_data" / f"{end_time.year}_{end_time.month}_{end_time.day}"
        data_directory.mkdir(parents=True, exist_ok=True)
        stocks_data = []

        files = data_directory.glob("stocks_history_*.json")
        known_symbol_ids = []
        file_counter = 0
        with sqlite3.connect(self.configuration.db_file_path) as conn:
            cursor = conn.cursor()
            for file in files:
                file_counter = max(file_counter, int(file.name.replace("stocks_history_", "").replace(".json", "")))
                with open(file, encoding="utf-8") as file_handler:
                    stocks_data = json.load(file_handler)
                for dict_src in stocks_data:
                    for candle_dict in dict_src["candles"]:
                        self.db_upsert_candle(Symbol(dict_src["symbol"]).symbol_id, Candle(candle_dict), cursor=cursor)
        breakpoint()
        output_file_path = data_directory / f"stocks_history_{file_counter}.json"

        stocks = self.get_tradable_stocks()

        stocks = [stock for stock in stocks if stock["symbolId"] not in known_symbol_ids]

        for i, stock in enumerate(stocks):
            if len(stocks_data) > 1000:
                file_counter += 1
                output_file_path = data_directory / f"stocks_history_{file_counter}.json"
                stocks_data = []
                logger.info(f"Opening new file: {output_file_path}")

            logger.info(f"Fetching stock history {i}/{len(stocks)} id:{stock['symbolId']} Symbol:{stock['symbol']}")
            res = self.get_position_history(stock["symbolId"], start_time,
                                            end_time)
            res["symbol"] = stock
            stocks_data.append(res)

            with open(output_file_path, "w", encoding="utf-8") as file_handler:
                json.dump(stocks_data, file_handler, indent=2)
        return True

    def check_strategy_one_persent_below_current(self, symbol_id):
        """
        Check dispersion.
        candle = {'start': '2026-04-16T16:06:00.000000-04:00',
        'end': '2026-04-16T16:07:00.000000-04:00',
        'low': 3.1501,
        'high': 3.1501,
        'open': 3.1501,
        'close': 3.1501,
        'volume': 193,
        'VWAP': 3.402387}

        :param symbol_id:
        :return:
        """

        percent = 1.0
        symbol = self.db_get_symbol(symbol_id)
        if symbol is None:
            raise NotImplementedError(f"Symbol {symbol_id} not found")
        candles = self.db_get_symbol_candles(symbol_id)
        breakpoint()
        averages = [(candle["high"] + candle["low"]) / 2 for candle in symbol_data["candles"]]

        success_sells = []
        for current_price_index, current_price in enumerate(averages):
            buy_price_limit = current_price * (100 - percent) / 100
            sell_price_limit = current_price * (100 + percent) / 100
            sell_price_limit = current_price
            for buy_price_index, buy_price in enumerate(averages[current_price_index + 1:]):
                if buy_price > buy_price_limit:
                    continue

                for sell_price_index, sell_price in enumerate(averages[current_price_index + 1:]):
                    if sell_price >= sell_price_limit:
                        success_sells.append(buy_price)
                        break
                else:
                    continue
                break
        print(f"{len(success_sells)=} out of {len(averages)}")

        return True

    def fetch_symbols_by_max_price(self, max_price):
        """
        Sort symbols by transactions count.
        0.0035*100

        :return:
        """

        one_percent_ecn_fee_limit = 0.0035*100
        if max_price:
            self.db_cursor.execute(
                f"select symbol_id from candles where vwap <= {max_price} and vwap >= {one_percent_ecn_fee_limit} group by symbol_id"
            )
            response = self.db_cursor.fetchall()
        else:
            self.db_cursor.execute(
                "select symbol_id from candles group by symbol_id"
            )
            response = self.db_cursor.fetchall()

        symbols = []
        for line in response:
            symbol = self.db_get_symbol(line[0])
            if not symbol:
                logger.error(f"Symbol {line[0]} not found in DB")
                continue
            try:
                symbol.candles = self.db_get_symbol_candles(symbol.symbol_id)
            except Exception as ex:
                raise
            if len(symbol.candles) < 5:
                continue
            symbols.append(symbol)
            logger.info(f"Added {symbol.symbol} to {len(symbols)} symbols")

        ret = [[symbol.symbol, symbol.symbol_id, len(symbol.candles), symbol.candles[0].vwap] for symbol in symbols]
        with open(self.configuration.data_directory / "symbols_sorted_by_transaction_count.json", "w",
                  encoding="utf-8") as file_handler:
            json.dump(ret, file_handler, indent=2)
        return True

    def sort_and_print_cheapest_by_price(self):
        """
        Sort symbols by price.
        :return:
        """
        with open(self.configuration.data_directory / "symbols_sorted_by_transaction_count.json",
                  encoding="utf-8") as file_handler:
            ret = json.load(file_handler)

        ret.sort(key=lambda val: val[3])
        for x in ret:
            print(x)
        return ret

    def load_symbols_history_data(self, max_price=None):
        """
        Load data from files

        :return:
        """

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

    def db_upsert_candle(self, symbol_id, candle: Candle, cursor=None):
        """
        Update or insert candle into DB
        :param cursor:
        :param symbol_id:
        :param candle:
        :return:
        """

        if not cursor:
            self.db_execute('''
                    INSERT OR REPLACE INTO candles (symbol_id, start, end, low, high, open, close, volume, vwap)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (symbol_id, candle.float_start, candle.float_end, candle.low, candle.high, candle.open,
                          candle.close, candle.volume, candle.vwap))
        else:
            cursor.execute('''
                INSERT OR REPLACE INTO candles (symbol_id, start, end, low, high, open, close, volume, vwap)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (symbol_id, candle.float_start, candle.float_end, candle.low, candle.high, candle.open, candle.close,
                  candle.volume,
                  candle.vwap))

        logger.info(f"Candle for symbol {symbol_id} upserted into {self.configuration.db_file_path}' database")
        return True

    def db_get_symbol(self, symbol_id=None, cursor=None, symbol_symbol=None):
        """
        Get symbol from DB
        :param cursor:
        :param symbol_id:
        :return:
        """

        logger.info(f"Fetching symbol {symbol_id} from {self.configuration.db_file_path}' database")

        if cursor:
            return self.db_get_symbol_raw(symbol_id, cursor, symbol_symbol=symbol_symbol)

        return self.db_get_symbol_raw(symbol_id, self.db_cursor, symbol_symbol=symbol_symbol)

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

    def db_get_symbol_candles(self, symbol_id, limit=None, cursor=None, start_time:datetime=None, end_time:datetime=None):
        """
        Get symbol candles from DB

        :param end_time:
        :param start_time:
        :param cursor:
        :param limit:
        :param symbol_id:
        :return:
        """


        end_timestamp = end_time.timestamp() if end_time else None

        start_timestamp = start_time.timestamp() if start_time else None
        if cursor:
            return self.db_get_symbol_candles_raw(symbol_id, cursor, limit=limit, start_timestamp=start_timestamp, end_timestamp=end_timestamp)

        return self.db_get_symbol_candles_raw(symbol_id, self.db_cursor, limit=limit, start_timestamp=start_timestamp, end_timestamp=end_timestamp)

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

    def update_symbol_today_candles(self, symbol: Symbol):
        """
        Update symbols today candles
        :param symbol:
        :return:
        """

        existing_candles = self.db_get_today_candles(symbol)
        existing_pairs = [(candle.float_start, candle.float_end) for candle in existing_candles]
        today = datetime.now(timezone.utc)
        if today.hour < 3:
            today -= timedelta(days=1)

        utc_today_3am = today.replace(hour=3, minute=0, second=0, microsecond=0)
        utc_today_8pm = today.replace(hour=20, minute=0, second=0, microsecond=0)


        candles = self.get_symbol_candles(symbol, utc_today_3am, utc_today_8pm)
        for candle in candles:
            if (candle.float_start, candle.float_end) in existing_pairs:
                continue
            self.db_upsert_candle(symbol.symbol_id, candle)
        return candles

    def db_get_today_candles(self, symbol:Symbol) -> List[Candle]:
        """
        Fetch from DB

        :param symbol:
        :return:
        """

        today = datetime.now(timezone.utc)
        if today.hour < 5:
            today -= timedelta(days=1)
        utc_today_3am = today.replace(hour=3, minute=0, second=0, microsecond=0)
        utc_today_8pm = today.replace(hour=20, minute=0, second=0, microsecond=0)


        candles = self.db_get_symbol_candles(symbol.symbol_id, start_time=utc_today_3am, end_time=utc_today_8pm)
        return candles

    def get_symbol_candles(self, symbol: Symbol, start_time: datetime, end_time: datetime):
        """
        Get symbols candles
        :param symbol:
        :param start_time:
        :param end_time:
        :return:
        """


        start_time = self.convert_time_to_request_format(start_time)
        end_time = self.convert_time_to_request_format(end_time)

        logger.info("Fetching Symbol's candles from API")
        try:
            position_candles = self.get(
            f"v1/markets/candles/{symbol.symbol_id}?startTime={start_time}&endTime={end_time}&interval=OneMinute")
        except Exception as inst:
            logger.exception(inst)
            if "Not Found for url" in repr(inst):
                return []
            raise

        return [Candle(dict_src) for dict_src in position_candles["candles"]]

    def update_cheap_candles_with_today_data(self, symbol_name=None):
        """
        Update cheap symbols with today data
        :return:
        """
        error_counter = 0
        cheapest_stocks = self.sort_and_print_cheapest_by_price()
        symbol_ids = [symbol[1] for symbol in cheapest_stocks if (symbol_name is None) or (symbol[0] == symbol_name)]
        self.connect()
        for i, symbol_id in enumerate(symbol_ids):
            symbol = self.db_get_symbol(symbol_id)
            try:
                logger.info(f"Updating Symbol {i}/{len(symbol_ids)} {symbol.symbol}")
                self.update_symbol_today_candles(symbol)
            except Exception:
                self.connect(reconnect =True)
                error_counter += 1
        if error_counter > len(symbol_ids)/2:
            raise ValueError(f"Too many errors {error_counter} out of {len(symbol_ids)}")
        return True

    def make_purchase_plan(self, symbol_name=None):
        """
        Plan purchase

        :return:
        """

        position_symbol_ids = [position.symbol_id for position in self.get_positions()]

        cheapest_stocks = self.sort_and_print_cheapest_by_price()
        symbol_ids = [symbol[1] for symbol in cheapest_stocks if symbol[1] not in position_symbol_ids and
                      ((symbol_name is None) or (symbol[0] == symbol_name))]
        orders = self.api_get_orders()
        order_symbol_ids = [order.symbol_id for order in orders]
        symbol_ids = [symbol_id for symbol_id in symbol_ids if symbol_id not in order_symbol_ids]

        symbols = []

        len_symbol_ids = len(symbol_ids)
        for i, symbol_id in enumerate(symbol_ids):
            logger.info(f"Fetching {i}/{len_symbol_ids}")

            symbol = self.db_get_symbol(symbol_id)
            symbol.candles = self.db_get_today_candles(symbol)
            if not symbol.candles:
                continue
            symbols.append(symbol)

        for symbol in symbols:

            symbol.vwap_change = self.calculate_vwap_change(symbol.candles)
            symbol.absolute_low = min([candle.low for candle in symbol.candles])
            symbol.absolute_high = max([candle.high for candle in symbol.candles])

        str_ret = ""
        for i, symbol in enumerate(sorted(symbols, key=lambda x: abs(x.vwap_change))):
            str_ret += f"[{i+1}] {symbol.symbol}, abs_low={symbol.absolute_low}, vwap_change={symbol.vwap_change}, deals={len(symbol.candles)}\n"

        with open(self.configuration.data_directory/ "purchase_plan.txt", "w") as file:
            file.write(str_ret)
        print(f"Purchase_plan is ready: {self.configuration.data_directory/ 'purchase_plan.txt'}")
        return True
    
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
        return QuestradeAPI.calculate_vwap_incline(candles) * vwap_change
    
    @staticmethod
    def calculate_vwap_incline(candles):
        """
        Create a line on the vwap change and calculate incline.
        :param candles:
        :return:
        """

        x_data = [(candle.float_end + candle.float_start)/2 for candle in candles]
        y_data = [candle.vwap for candle in candles]
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
        return 1 if (slope > 0) else -1

    @staticmethod
    def connected(func):
        def wrapper(self, *args, **kwargs):
            self.connect()
            return func(self, *args, **kwargs)
        return wrapper

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
        order_by_symbol_id = {order.symbol_id: order for order in orders if order.side == "Sell"}
        for position in positions:
            # todo: fix
            if position.symbol in []:
                continue


            if position.symbol_id not in order_by_symbol_id:
                ret.append(position)
                candles = self.db_get_today_candles(position)
                if position.average_entry_price is None:
                    lines.append(f">Time to sell! {position.symbol} {position.open_quantity} {position.average_entry_price}")
                    continue
                percent_105 =  position.average_entry_price * 1.05
                percent_110 =  position.average_entry_price * 1.1
                if candles:
                    sell_high = max(candle.high for candle in candles)
                    sell_calculated = percent_110 if sell_high > percent_110 else percent_105
                else:
                    sell_calculated = percent_105

                sell_calculated = Decimal(str(sell_calculated))

                # Round to 2 decimal places
                sell_calculated_round = sell_calculated.quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

                if sell_calculated_round < sell_calculated:
                    sell_calculated_round += Decimal("0.01")

                lines.append(f"Sell {position.symbol} count={position.open_quantity} price={sell_calculated_round}, revenue={int(sell_calculated/( Decimal(str(position.average_entry_price))/100))}%")
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

        ret = self.db_cursor.execute('SELECT * FROM candles group by symbol_id')
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

    def open_symbol_page(self, symbol_name):
        """
        Open symbol page
        :param symbol_name:
        :return:
        """

        raise NotImplementedError()
    
    def write_to_cache(self, lst_obj):
        """
        Write list of objects to cache
        :param lst_obj:
        :return:
        """
        ret = [obj.dict_src for obj in lst_obj]
        file_name = lst_obj[0].__class__.__name__.lower() + "s_cache.json"
        with open(self.configuration.data_directory / file_name, "w") as file:
            json.dump(ret, file, indent=2)

    def load_from_cache(self, obj_class):
        """
        Write list of objects to cache
        :param obj_class:
        :return:
        """
        file_name = obj_class.__name__.lower() + "s_cache.json"
        with open(self.configuration.data_directory / file_name) as file:
            order_dicts = json.load(file)
        return [obj_class(dict_src) for dict_src in order_dicts]

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

"""
Shamelessly stolen from:
https://questrade.com/lukecyca/pyslack
"""
import sqlite3
from datetime import datetime, timezone, timedelta
import json
from sys import flags

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
        with sqlite3.connect(self.configuration.db_file_path) as conn:
            cursor = conn.cursor()

            for file in files:
                logger.info(f"Processing file: {file.name}")
                with open(file, "r", encoding="utf-8") as file_handler:
                    ret=json.load(file_handler)

                for dict_src in ret:
                    self.db_upsert_symbol(Symbol(dict_src), cursor=cursor)
                    conn.commit()
        return True

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

    def get_all_stocks_daily_history(self):
        """
        Get all stocks history.
        :return:
        """

        start_time = datetime(year=2026, month=4, day=13, hour=3, minute=0, second=0,  tzinfo=timezone.utc)
        end_time = datetime(year=2026, month=4, day=13, hour=21, minute=2, second=0,  tzinfo=timezone.utc)
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
        averages = [(candle["high"] + candle["low"])/2 for candle in symbol_data["candles"]]

        success_sells = []
        for current_price_index, current_price in enumerate(averages):
            buy_price_limit = current_price * (100 - percent)/100
            sell_price_limit = current_price * (100 + percent) / 100
            sell_price_limit = current_price
            for buy_price_index, buy_price in enumerate(averages[current_price_index+1:]):
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
        :return:
        """

        with sqlite3.connect(self.configuration.db_file_path) as conn:
            cursor = conn.cursor()

            if max_price:
                cursor.execute(
                    f"select symbol_id from candles where vwap <= {max_price} group by symbol_id"
                )
                response = cursor.fetchall()
            else:
                cursor.execute(
                    "select symbol_id from candles group by symbol_id"
                )
                response = cursor.fetchall()

            symbols = []
            for line in response:
                symbol = self.db_get_symbol(line[0], cursor=cursor)
                if not symbol:
                    logger.error(f"Symbol {line[0]} not found in DB")
                    continue
                try:
                    symbol.candles = self.db_get_symbol_candles(symbol.symbol_id, cursor=cursor)
                except Exception as ex:
                    breakpoint()
                    continue
                if len(symbol.candles) < 50:
                    continue
                symbols.append(symbol)
                logger.info(f"Added {symbol.symbol} to {len(symbols)} symbols")

        ret = [[symbol.symbol, symbol.symbol_id,len(symbol.candles), symbol.candles[0].vwap] for symbol in symbols]
        with open(self.configuration.data_directory / "symbols_sorted_by_transaction_count.json", "w", encoding="utf-8") as file_handler:
            json.dump(ret, file_handler, indent=2)

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
        breakpoint()

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

    def db_upsert_symbol(self, symbol: Symbol, cursor=None ):
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
                ''', (symbol.symbol_id, symbol.symbol, symbol.description, symbol.security_type, symbol.listing_exchange, symbol.is_tradable, symbol.is_quotable, symbol.currency))
                conn.commit()
        else:
            cursor.execute('''
                               INSERT OR REPLACE INTO symbols (symbol_id, symbol, description, security_type, listing_exchange, is_tradable, is_quotable, currency)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                           ''', (symbol.symbol_id, symbol.symbol, symbol.description, symbol.security_type,
                                 symbol.listing_exchange, symbol.is_tradable, symbol.is_quotable, symbol.currency))

        logger.info(f"Symbol {symbol.symbol} upserted into {self.configuration.db_file_path}' database")
        return True

    def db_upsert_candle(self, symbol_id, candle: Candle, cursor=None):
        """
        Update or insert candle into DB
        :param cursor:
        :param symbol_id:
        :param candle:
        :return:
        """

        if not cursor:
            with sqlite3.connect(self.configuration.db_file_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO candles (symbol_id, start, end, low, high, open, close, volume, vwap)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (symbol_id, candle.float_start, candle.float_end, candle.low, candle.high, candle.open, candle.close, candle.volume, candle.vwap))
                conn.commit()
        else:
            cursor.execute('''
                INSERT OR REPLACE INTO candles (symbol_id, start, end, low, high, open, close, volume, vwap)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (symbol_id, candle.float_start, candle.float_end, candle.low, candle.high, candle.open, candle.close, candle.volume,
              candle.vwap))

        logger.info(f"Candle for symbol {symbol_id} upserted into {self.configuration.db_file_path}' database")
        return True

    def db_get_symbol(self, symbol_id, cursor=None):
        """
        Get symbol from DB
        :param cursor:
        :param symbol_id:
        :return:
        """

        if cursor:
            return self.db_get_symbol_raw(symbol_id,cursor)

        with sqlite3.connect(self.configuration.db_file_path) as conn:
            cursor = conn.cursor()
            return self.db_get_symbol_raw(symbol_id, cursor)


    def db_get_symbol_raw(self, symbol_id, cursor):
        """
        Get symbol from DB
        :param cursor:
        :param symbol_id:
        :return:
        """

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

    def db_get_symbol_candles(self, symbol_id, limit=None, cursor=None):
        """
        Get symbol candles from DB
        :param cursor:
        :param limit:
        :param symbol_id:
        :return:
        """

        if cursor:
            return self.db_get_symbol_candles_raw(symbol_id, cursor, limit=limit)

        with sqlite3.connect(self.configuration.db_file_path) as conn:
            cursor = conn.cursor()
            return self.db_get_symbol_candles_raw(symbol_id, cursor, limit=limit)

    def db_get_symbol_candles_raw(self, symbol_id, cursor, limit=None):
        """
        Get symbol candles from DB
        :param symbol_id:
        :param cursor:
        :param limit:
        :return:
        """
        if limit is not None:
            limit_string = f" LIMIT {limit}"
        else:
            limit_string = ""

        cursor.execute(f'SELECT * FROM candles WHERE symbol_id = ?{limit_string}', (symbol_id, ))
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


class Candle:
    def __init__(self, dict_src):
        self.dict_src = dict_src
        self._end = None
        self._start = None
        self._float_start = None
        self._float_end = None

        self.start = dict_src["start"]
        self.end = dict_src["end"]
        self.low = dict_src["low"]
        self.high = dict_src["high"]
        self.open = dict_src["open"]
        self.close = dict_src["close"]
        self.volume = dict_src["volume"]
        self.vwap = dict_src["VWAP"] if "VWAP" in dict_src else dict_src["vwap"]

        self.symbol_id = None
        if "symbol_id" in dict_src:
            self.symbol_id = dict_src["symbol_id"]

    @property
    def start(self):
        """
        Get start
        :return:
        """
        return self._start

    @start.setter
    def start(self, value):
        """
        Set start
        :param value:
        :return:
        """

        if isinstance(value, str):
            _date = datetime.fromisoformat(value.replace("Z", "+00:00"))
            _date = _date.replace(tzinfo=timezone.utc)
            self._start = _date
        elif isinstance(value, datetime):
            self._start = value
        elif isinstance(value, float):
            self._start = datetime.fromtimestamp(value)
        else:

            raise NotImplementedError("Implement me")

    @property
    def end(self):
        """
        Get end
        :return:
        """
        return self._end

    @end.setter
    def end(self, value):
        """
        Set start
        :param value:
        :return:
        """

        if isinstance(value, str):
            _date = datetime.fromisoformat(value.replace("Z", "+00:00"))
            _date = _date.replace(tzinfo=timezone.utc)
            self._end = _date
        elif isinstance(value, datetime):
            self._end = value
        elif isinstance(value, float):
            self._end = datetime.fromtimestamp(value)
        else:

            raise NotImplementedError("Implement me")
    @property
    def float_start(self):
        """
        Convert date to float timestamp
        :return:
        """

        if isinstance(self.start, datetime):
            return self.start.timestamp()
        raise NotImplementedError("Implement me")

    @property
    def float_end(self):
        """
        Convert date to float timestamp
        :return:
        """

        if isinstance(self.end, datetime):
            return self.end.timestamp()
        raise NotImplementedError("Implement me")


class Symbol:
    def __init__(self, dict_src):
        self.symbol = dict_src["symbol"]
        self.symbol_id = dict_src["symbolId"]
        self.security_type = dict_src["securityType"]
        self.is_tradable = dict_src["isTradable"]
        self.is_quotable = dict_src["isQuotable"]
        self.currency = dict_src["currency"]
        self.listing_exchange = dict_src["listingExchange"]
        self.description = dict_src["description"]

        self.id = dict_src["id"] if "id" in dict_src else None

        self.candles = []

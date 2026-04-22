from datetime import datetime, timezone

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
        self.dict_src = dict_src
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

class Position:
    def __init__(self, dict_src):
        """
        {'symbol': 'ITRMF',
        'symbolId': 43721559,
        'openQuantity': 81,
        'closedQuantity': 0,
        'currentMarketValue': 1.4094,
        'currentPrice': 0.0174,
        'averageEntryPrice': 0.0124,
        'dayPnl': 0,
        'closedPnl': 0,
        'openPnl': 0.405,
        'totalCost': 1.0044,
        'isRealTime': False,
        'isUnderReorg': False}

        :param dict_src:
        """
        self.dict_src = dict_src

        self.symbol = dict_src["symbol"]
        self.symbol_id = dict_src["symbolId"]
        self.open_quantity = dict_src["openQuantity"]
        self.closed_quantity = dict_src["closedQuantity"]
        self.current_market_value = dict_src["currentMarketValue"]
        self.current_price = dict_src["currentPrice"]
        self.average_entry_price = dict_src["averageEntryPrice"]
        self.day_pnl = dict_src["dayPnl"]
        self.closed_pnl = dict_src["closedPnl"]
        self.open_pnl = dict_src["openPnl"]
        self.total_cost = dict_src["totalCost"]
        self.is_real_time = dict_src["isRealTime"]
        self.is_under_reorg = dict_src["isUnderReorg"]


class Order:
    def __init__(self, dict_src):
        """
        dict_src = {'id': 1750935419, 'symbol': 'ZSPC', 'symbolId': 73637676, 'totalQuantity': 21, 'openQuantity': 21, 'filledQuantity': 0, 'canceledQuantity': 0, 'side': 'Buy', 'orderType': 'Limit', 'limitPrice': 0.0488, 'stopPrice': None, 'isAllOrNone': False, 'isAnonymous': False, 'icebergQuantity': None, 'minQuantity': None, 'avgExecPrice': 0, 'lastExecPrice': None, 'source': 'Undefined', 'timeInForce': 'GoodTillExtendedDay', 'gtdDate': None, 'state': 'Accepted', 'rejectionReason': '', 'chainId': 1750935419, 'creationTime': '2026-04-21T07:52:19.088000-04:00', 'updateTime': '2026-04-21T07:52:19.139000-04:00', 'notes': '', 'primaryRoute': 'AUTO', 'secondaryRoute': 'AUTO', 'orderRoute': 'CTDLBN', 'venueHoldingOrder': 'CTDLBN', 'comissionCharged': 0, 'exchangeOrderId': '260421-115219-1', 'isSignificantShareHolder': False, 'isInsider': False, 'isLimitOffsetInDollar': False, 'userId': 2932875, 'placementCommission': None, 'legs': [], 'strategyType': 'SingleLeg', 'triggerStopPrice': None, 'orderGroupId': 0, 'orderClass': None, 'isCrossZero': False}

        :param dict_src:
        """
        self.dict_src = dict_src
        self.order_id = dict_src["id"]
        self.symbol_id = dict_src["symbolId"]
        self.total_quantity = dict_src["totalQuantity"]
        self.open_quantity = dict_src["openQuantity"]
        self.filled_quantity = dict_src["filledQuantity"]
        self.canceled_quantity = dict_src["canceledQuantity"]
        self.side = dict_src["side"]
        self.order_type = dict_src["orderType"]
        self.limit_price = dict_src["limitPrice"]
        self.state = dict_src["state"]
        self.creation_time = dict_src["creationTime"]
        self.update_time = dict_src["updateTime"]
        self.notes = dict_src["notes"]
        self.exchange_order_id = dict_src["exchangeOrderId"]
        self.is_limit_offset_in_dollar = dict_src["isLimitOffsetInDollar"]
        self.legs = dict_src["legs"]
        self.strategy_type = dict_src["strategyType"]
        self.order_class = dict_src["orderClass"]
        self.is_cross_zero = dict_src["isCrossZero"]





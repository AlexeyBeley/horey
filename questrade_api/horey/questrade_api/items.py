from datetime import datetime, timezone
from horey.common_utils.common_utils import CommonUtils

class Base:
    def __init__(self, dict_src):
        self.dict_src = dict_src
        self.id = dict_src["id"] if "id" in dict_src else None

    def print(self):
        """
        Print object params
        :return:
        """
        for x, y in self.__dict__.items():
            if not x.startswith("_"):
                print(f"{x}: {y}")

class Candle(Base):
    def __init__(self, dict_src):
        super().__init__(dict_src)
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
            self._end = _date
        elif isinstance(value, datetime):
            breakpoint()
            self._end = value
        elif isinstance(value, float):
            self._end = datetime.fromtimestamp(value)
        else:

            raise NotImplementedError("Implement me")

    @property
    def float_start(self):
        """
        Convert date to float timestamp
        dt = datetime.fromtimestamp(timestamp, tz=ZoneInfo("America/New_York"))
        :return:
        """

        if isinstance(self.start, datetime):
            return self.start.timestamp()
        raise NotImplementedError("Implement me")

    @property
    def float_end(self):
        """
        Convert date to float timestamp
        dt = datetime.fromtimestamp(timestamp, tz=ZoneInfo("America/New_York"))
        :return:
        """

        if isinstance(self.end, datetime):
            return self.end.timestamp()
        raise NotImplementedError("Implement me")


class Symbol(Base):
    def __init__(self, dict_src):
        super().__init__(dict_src)
        self.symbol = dict_src["symbol"]
        self.symbol_id = dict_src["symbolId"]
        self.security_type = dict_src["securityType"]
        self.is_tradable = dict_src["isTradable"]
        self.is_quotable = dict_src["isQuotable"]
        self.currency = dict_src["currency"]
        self.listing_exchange = dict_src["listingExchange"]
        self.description = dict_src["description"]

        self.candles = []

class Position(Base):
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
        super().__init__(dict_src)

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


class Order(Base):
    def __init__(self, dict_src):
        """
        dict_src = {'id': 1750935419, 'symbol': 'ZSPC', 'symbolId': 73637676, 'totalQuantity': 21, 'openQuantity': 21, 'filledQuantity': 0, 'canceledQuantity': 0, 'side': 'Buy', 'orderType': 'Limit', 'limitPrice': 0.0488, 'stopPrice': None, 'isAllOrNone': False, 'isAnonymous': False, 'icebergQuantity': None, 'minQuantity': None, 'avgExecPrice': 0, 'lastExecPrice': None, 'source': 'Undefined', 'timeInForce': 'GoodTillExtendedDay', 'gtdDate': None, 'state': 'Accepted', 'rejectionReason': '', 'chainId': 1750935419, 'creationTime': '2026-04-21T07:52:19.088000-04:00', 'updateTime': '2026-04-21T07:52:19.139000-04:00', 'notes': '', 'primaryRoute': 'AUTO', 'secondaryRoute': 'AUTO', 'orderRoute': 'CTDLBN', 'venueHoldingOrder': 'CTDLBN', 'comissionCharged': 0, 'exchangeOrderId': '260421-115219-1', 'isSignificantShareHolder': False, 'isInsider': False, 'isLimitOffsetInDollar': False, 'userId': 2932875, 'placementCommission': None, 'legs': [], 'strategyType': 'SingleLeg', 'triggerStopPrice': None, 'orderGroupId': 0, 'orderClass': None, 'isCrossZero': False}

        :param dict_src:
        """
        
        super().__init__(dict_src)
        self._order_id = None 
        self._symbol_id = None
        self._total_quantity = None
        self._open_quantity = None
        self._filled_quantity = None
        self._canceled_quantity = None
        self._side = None
        self._order_type = None
        self._limit_price = None
        self._state = None
        self._creation_time = None
        self._update_time = None
        self._notes = None
        self._exchange_order_id = None
        self._is_limit_offset_in_dollar = None
        self._legs = None
        self._strategy_type = None
        self._order_class = None
        self._is_cross_zero = None
        self._commission_charged = None
        self._placement_commission = None 
        self._stop_price = None 
        self._avg_exec_price = None 
        self._symbol = None
        self._is_all_or_none = None
        self._is_anonymous = None
        self._iceberg_quantity = None
        self._min_quantity = None
        self._last_exec_price = None
        self._source = None
        self._time_in_force = None
        self._gtd_date = None
        self._rejection_reason = None
        self._chain_id = None
        self._primary_route = None
        self._secondary_route = None
        self._order_route = None
        self._venue_holding_order = None
        self._comission_charged = None
        self._is_significant_share_holder = None
        self._is_insider = None
        self._user_id = None
        self._trigger_stop_price = None
        self._order_group_id = None        

        if not CommonUtils.init_from_api_dict(self, dict_src):
            breakpoint()
            logger.info("todo:")

    @property
    def order_id(self):
        return self._order_id

    @order_id.setter
    def order_id(self, value):
        self._order_id = value

    @property
    def symbol_id(self):
        return self._symbol_id

    @symbol_id.setter
    def symbol_id(self, value):
        self._symbol_id = value

    @property
    def total_quantity(self):
        return self._total_quantity

    @total_quantity.setter
    def total_quantity(self, value):
        self._total_quantity = value

    @property
    def open_quantity(self):
        return self._open_quantity

    @open_quantity.setter
    def open_quantity(self, value):
        self._open_quantity = value

    @property
    def filled_quantity(self):
        return self._filled_quantity

    @filled_quantity.setter
    def filled_quantity(self, value):
        self._filled_quantity = value

    @property
    def canceled_quantity(self):
        return self._canceled_quantity

    @canceled_quantity.setter
    def canceled_quantity(self, value):
        self._canceled_quantity = value

    @property
    def side(self):
        return self._side

    @side.setter
    def side(self, value):
        self._side = value

    @property
    def order_type(self):
        return self._order_type

    @order_type.setter
    def order_type(self, value):
        self._order_type = value

    @property
    def limit_price(self):
        return self._limit_price

    @limit_price.setter
    def limit_price(self, value):
        self._limit_price = value

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def creation_time(self):
        return self._creation_time

    @creation_time.setter
    def creation_time(self, value):
        self._creation_time = value

    @property
    def update_time(self):
        return self._update_time

    @update_time.setter
    def update_time(self, value):
        self._update_time = value

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, value):
        self._notes = value

    @property
    def exchange_order_id(self):
        return self._exchange_order_id

    @exchange_order_id.setter
    def exchange_order_id(self, value):
        self._exchange_order_id = value

    @property
    def is_limit_offset_in_dollar(self):
        return self._is_limit_offset_in_dollar

    @is_limit_offset_in_dollar.setter
    def is_limit_offset_in_dollar(self, value):
        self._is_limit_offset_in_dollar = value

    @property
    def legs(self):
        return self._legs

    @legs.setter
    def legs(self, value):
        self._legs = value

    @property
    def strategy_type(self):
        return self._strategy_type

    @strategy_type.setter
    def strategy_type(self, value):
        self._strategy_type = value

    @property
    def order_class(self):
        return self._order_class

    @order_class.setter
    def order_class(self, value):
        self._order_class = value

    @property
    def is_cross_zero(self):
        return self._is_cross_zero

    @is_cross_zero.setter
    def is_cross_zero(self, value):
        self._is_cross_zero = value

    @property
    def commission_charged(self):
        return self._commission_charged

    @commission_charged.setter
    def commission_charged(self, value):
        self._commission_charged = value

    @property
    def placement_commission(self):
        return self._placement_commission

    @placement_commission.setter
    def placement_commission(self, value):
        self._placement_commission = value

    @property
    def stop_price(self):
        return self._stop_price

    @stop_price.setter
    def stop_price(self, value):
        self._stop_price = value

    @property
    def avg_exec_price(self):
        return self._avg_exec_price

    @avg_exec_price.setter
    def avg_exec_price(self, value):
        self._avg_exec_price = value
    
    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, value):
        self._symbol = value

    @property
    def is_all_or_none(self):
        return self._is_all_or_none

    @is_all_or_none.setter
    def is_all_or_none(self, value):
        self._is_all_or_none = value

    @property
    def is_anonymous(self):
        return self._is_anonymous

    @is_anonymous.setter
    def is_anonymous(self, value):
        self._is_anonymous = value

    @property
    def iceberg_quantity(self):
        return self._iceberg_quantity

    @iceberg_quantity.setter
    def iceberg_quantity(self, value):
        self._iceberg_quantity = value

    @property
    def min_quantity(self):
        return self._min_quantity

    @min_quantity.setter
    def min_quantity(self, value):
        self._min_quantity = value

    @property
    def last_exec_price(self):
        return self._last_exec_price

    @last_exec_price.setter
    def last_exec_price(self, value):
        self._last_exec_price = value

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value

    @property
    def time_in_force(self):
        return self._time_in_force

    @time_in_force.setter
    def time_in_force(self, value):
        self._time_in_force = value

    @property
    def gtd_date(self):
        return self._gtd_date

    @gtd_date.setter
    def gtd_date(self, value):
        self._gtd_date = value

    @property
    def rejection_reason(self):
        return self._rejection_reason

    @rejection_reason.setter
    def rejection_reason(self, value):
        self._rejection_reason = value

    @property
    def chain_id(self):
        return self._chain_id

    @chain_id.setter
    def chain_id(self, value):
        self._chain_id = value

    @property
    def primary_route(self):
        return self._primary_route

    @primary_route.setter
    def primary_route(self, value):
        self._primary_route = value

    @property
    def secondary_route(self):
        return self._secondary_route

    @secondary_route.setter
    def secondary_route(self, value):
        self._secondary_route = value

    @property
    def order_route(self):
        return self._order_route

    @order_route.setter
    def order_route(self, value):
        self._order_route = value

    @property
    def venue_holding_order(self):
        return self._venue_holding_order

    @venue_holding_order.setter
    def venue_holding_order(self, value):
        self._venue_holding_order = value

    @property
    def comission_charged(self):
        return self._comission_charged

    @comission_charged.setter
    def comission_charged(self, value):
        self._comission_charged = value

    @property
    def is_significant_share_holder(self):
        return self._is_significant_share_holder

    @is_significant_share_holder.setter
    def is_significant_share_holder(self, value):
        self._is_significant_share_holder = value

    @property
    def is_insider(self):
        return self._is_insider

    @is_insider.setter
    def is_insider(self, value):
        self._is_insider = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    @property
    def trigger_stop_price(self):
        return self._trigger_stop_price

    @trigger_stop_price.setter
    def trigger_stop_price(self, value):
        self._trigger_stop_price = value

    @property
    def order_group_id(self):
        return self._order_group_id

    @order_group_id.setter
    def order_group_id(self, value):
        self._order_group_id = value
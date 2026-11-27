"""
Purchase plan item

"""
from decimal import Decimal
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from horey.h_logger import get_logger
logger = get_logger()

class PurchasePlanItem:
    def __init__(self, symbol:Symbol):
        self.symbol = symbol
        self._daily_slope = None
        self._weekly_slope = None
        self._monthly_slope = None
        self._score = 0
        self.candles_by_trading_time_range = []
        self.trading_frame_start_hour_by_day = {"Sunday": [20], 
                                    "Monday": [4, 20], 
                                    "Tuesday": [4, 20],
                                    "Wednesday": [4, 20], 
                                    "Thursday":[4, 20], 
                                    "Friday": [4]}
        self._desired_purchase_price = None
        self._desired_purchase_price_evaluation_start = None
        self._desired_purchase_price_evaluation_end = None

    @property
    def desired_purchase_price(self):
        """
        Calc the price

        """

        _candles = self.symbol.get_candles()
        now_evaluation_start = min(candle.start for candle in _candles)
        now_evaluation_end = max(candle.end for candle in _candles)
        
        if self._desired_purchase_price is not None:
            if self._desired_purchase_price_evaluation_start == now_evaluation_start and \
                self._desired_purchase_price_evaluation_end == now_evaluation_end:
                return self._desired_purchase_price

        last_trading_frame_candles = self.get_candles_last_trading_time_range() 
        recent_trading_frame_low_prices = [candle.low for candle in last_trading_frame_candles] 
        if not recent_trading_frame_low_prices:
            raise NotImplementedError("Should not be here- the filtering by last day trading should be done before.")
        desired_purchase_price = max(recent_trading_frame_low_prices) * 0.85
        if recent_trading_frame_low_prices[-1] < desired_purchase_price:
            float_last_trading_price = recent_trading_frame_low_prices[-1]
            
            if self.symbol.currency.lower() == "usd":
                limit_pice = 1
            else:
                limit_pice = 0.5

            if float_last_trading_price >= limit_pice:
                decimal_last_trading_price = Decimal(str(float_last_trading_price)[:4])
                desired_purchase_price = float((decimal_last_trading_price - Decimal("0.01")))
            else:
                decimal_last_trading_price = Decimal(str(float_last_trading_price)[:6])
                desired_purchase_price = float(( decimal_last_trading_price - Decimal("0.0001")))
        
        if desired_purchase_price <= 0.001:
            # raise ValueError(f"Purchase Price is too low: {purchase_price} for symbol '{self.symbol.symbol}'")
            desired_purchase_price = -1 
        self._desired_purchase_price = desired_purchase_price
        self._desired_purchase_price_evaluation_start = now_evaluation_start 
        self._desired_purchase_price_evaluation_end = now_evaluation_end

        return self._desired_purchase_price

    def get_candles_last_trading_time_range(self):
        """
        Get the candled in the last trading range.

        """

        return max(self.candles_by_trading_time_range, key=lambda _triplet: _triplet[0])[2]

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
        return round(min_price / max_price * 100)
    
    @staticmethod
    def calculate_price_incline(candles, callback_price):
        """
        Create a line on the vwap change and calculate incline.
        :param callback_price:
        :param candles:
        :return:
        """

        slope = PurchasePlanItem.calculate_price_slope(candles, callback_price)
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

    def show_graph(self):
        """
        Show graph locally
        """

        candles = self.symbol.get_candles()
        #candles = candles[:100]
        xlabels = ["."] * len(candles)
        low_prices = np.array([candle.low for candle in candles])
        high_prices = np.array([candle.high for candle in candles])
        symbols_data = [(xlabels, low_prices, high_prices)]

        now_utc_dt = datetime.now(timezone.utc)
        now_ny_dt = now_utc_dt.astimezone(ZoneInfo("America/New_York"))
        time_week = now_ny_dt - timedelta(days=7)
        time_recent_frame = self.get_recent_market_frame_start()
        week_candles = []
        recent_frame_candled = []
        for candle in candles:
            if candle.start < time_week:
                # todo: change to break after changing the get_candles function to return ordered response 
                continue
            week_candles.append(candle)
            if candle.start >= time_recent_frame:
                recent_frame_candled.append(candle)
        
        symbols_data.append((["."] * len(week_candles), 
        np.array([candle.low for candle in week_candles]),
        np.array([candle.high for candle in week_candles])
        ))

        symbols_data.append((["."] * len(recent_frame_candled), 
        np.array([candle.low for candle in recent_frame_candled]),
        np.array([candle.high for candle in recent_frame_candled])
        ))

        lowest_price = min(candle.low for candle in candles)
        highest_price = max(candle.high for candle in candles)
        fig, axes = plt.subplots(3, 1, figsize=(10, 12), layout='constrained')
        for ax, (xlabels, low_prices, high_prices) in zip(axes, symbols_data):
            self.hat_graph(ax, xlabels, [low_prices, high_prices], ['Min', 'Max'])

            # Add some text for labels, title and custom x-axis tick labels, etc.
            ax.set_xlabel('Minute')
            ax.set_ylabel('Price')
            ax.set_ylim(lowest_price, highest_price)
            ax.set_title(f"{self.symbol.symbol} price range by minute")
            ax.legend()
        breakpoint()
        plt.show()
    
    @staticmethod
    def get_recent_market_frame_start():
        """
        Pre-Market	4:00 AM – 9:30 AM	Monday – Friday
        Regular Market	9:30 AM – 4:00 PM	Monday – Friday
        Post-Market (After-Hours)	4:00 PM – 8:00 PM	Monday – Friday
        Overnight Trading	8:00 PM – 2:00 AM	Sunday – Friday
        """

        trading_frames = {"Sunday": [(20, 6)], 
                                    "Monday": [(4, 16), (20, 6)], 
                                    "Tuesday": [(4, 16), (20, 6)],
                                    "Wednesday": [(4, 16), (20, 6)], 
                                    "Thursday":[(4, 16), (20, 6)], 
                                    "Friday": [(4, 16)]}
        now_utc_dt = datetime.now(timezone.utc)
        now = now_utc_dt.astimezone(ZoneInfo("America/New_York"))
        week_day_now = now.strftime("%A")
        if week_day_now not in trading_frames:
            ret =  now - timedelta(hours=24)
            return ret.replace(hour=4, minute=0, second=0, microsecond=0)

        for frame_start_hour, frame_duration_hours in trading_frames[week_day_now]:
            frame_start = now.replace(hour=frame_start_hour, minute=0, second=0, microsecond=0)
            frame_end = frame_start + timedelta(hours=frame_duration_hours) 
            if now > frame_start and now < frame_end:
                return frame_start
        
        min_frame_start_hour = min(frame_start_hour for frame_start_hour, _ in trading_frames[week_day_now])
        if now.hour < min_frame_start_hour:
            keys = list(trading_frames.keys())
            for i, key in enumerate(keys):
                if key == week_day_now:
                    prev_day_frames = trading_frames[keys[i-1]] 
            
            prev_day_max_start_hour = max(hour for hour, duration in prev_day_frames) 
            ret = (now - timedelta(days=1)).replace(hour=prev_day_max_start_hour, minute=0, second=0, microsecond=0)
            return ret

        raise NotImplementedError("Need to handle case when now is before/after all trading frames.")

    @staticmethod
    def hat_graph(ax, xlabels, values, group_labels):
        """
        Create a hat graph.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The Axes to plot into.
        xlabels : list of str
            The category names to be displayed on the x-axis.
        values : (M, N) array-like
            The data values.
            Rows are the groups (len(group_labels) == M).
            Columns are the categories (len(xlabels) == N).
        group_labels : list of str
            The group labels displayed in the legend.
        """

        values = np.asarray(values)
        color_cycle_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

        # Draw the hats
        xs = [i for i in range(len(values[1]))]
        bars = ax.bar(xs,
            (values[1]- values[0]).T, bottom=values[0],
            edgecolor='black')

    def init_score(self) -> int: 
        """
        Maybe check high instead vwap and low. Vwap was checked, worked worse then low.
        symbol.price_change = self.calculate_vwap_change(symbol.candles)

        """

        self._score = 0

        now = datetime.now(timezone.utc).astimezone(ZoneInfo("America/New_York")) 
        
        self.candles_by_trading_time_range = self.split_candles_for_planning(now)
        last_trading_frame_candles = self.get_candles_last_trading_time_range()
        if not last_trading_frame_candles:
            logger.debug(f"There was no trading for {self.symbol.symbol}")
            return -1
        
        last_trading_frame_candles_low = [candle.low for candle in last_trading_frame_candles]
        last_trading_frame_candles_lowest = min(last_trading_frame_candles_low)
        last_trading_frame_candles_highest =  max(last_trading_frame_candles_low)
        price_change = (last_trading_frame_candles_lowest / last_trading_frame_candles_highest) * 100
        if price_change < 95:
            self._score += 1

        for (start_time, end_time, candles) in self.candles_by_trading_time_range:
            if len(candles) > 10:
                self._score += 1
            if self.calculate_price_incline(candles, lambda x: x.low) > 0:
                self._score += 1
        return self._score

    def split_candles_for_planning(self, now: datetime):
        """
        Filter anomalies and split to day, week, month
        """

        # Planning is done in a vacation day, calculations must move to 
        # previous active trading day.
        if now.strftime("%A") == "Sunday":
            now = now - timedelta(days=2)
            now = now.replace(hour=19, minute=59, second=59)
        
        if now.strftime("%A") == "Saturday":
            now = now - timedelta(days=1)
            now = now.replace(hour=19, minute=59, second=59)
        
        # Planning is done during trading opening time (45 min from trading start)
        # affects the planning because there are many anomalies during this time

        today_trading_frames_start_hours = self.trading_frame_start_hour_by_day[now.strftime("%A")]

        if now.hour in today_trading_frames_start_hours and now.minute < 45:
            # move now to the begining of the frame
            now = now.replace(minute=0, second=0, microsecond=0)

        two_days_ago = now - timedelta(days=2)  
        time_bound_aggregator = [(now - timedelta(days=30), now, []),
                        (now - timedelta(days=7), now, []),
                        (now.replace(hour=0, minute=0, second=0, microsecond=0), now, []),
                        (two_days_ago - timedelta(days=30), two_days_ago, []), 
                        (two_days_ago - timedelta(days=7), two_days_ago, []),
                        ]

        for candle in self.symbol.get_candles():
            for start_time, end_time, aggregator in time_bound_aggregator:
                if candle.end >= start_time and candle.start <= end_time:
                    aggregator.append(candle)
        return time_bound_aggregator

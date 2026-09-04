"""
Testing questrade api functionality.

"""
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from typing import TypeVar
import pytest
from zoneinfo import ZoneInfo

from horey.questrade_api.items import Candle
from horey.questrade_api.questrade_api import QuestradeAPI, QuestradeAPIConfigurationPolicy


from horey.common_utils.common_utils import CommonUtils
from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from horey.h_logger import get_logger

test_mock_values_file_tokenh = Path(__file__).parent.parent.parent.parent / "ignore" / "test_q_api.py"
test_mock_values = CommonUtils.load_module(test_mock_values_file_tokenh)



logger = get_logger()


T = TypeVar('T', bound=ConfigurationPolicy)
data_directory = Path("/tmp/data")

# pylint: disable = missing-function-docstring

class Configs(ConfigurationPolicy):
    """
    Standard tests configs.
    """

    def __init__(self):
        super().__init__()
        self._token = None
        self._account = None
        self._api_server = None
        self._user = None
        self._password = None

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def api_server(self):
        return self._api_server

    @api_server.setter
    def api_server(self, value):
        self._api_server = value

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value


@pytest.fixture(name="tests_config")
def fixture_tests_config():
    configuration = Configs()
    configuration.user = test_mock_values.user
    configuration.password= test_mock_values.password
    configuration.token = test_mock_values.token
    configuration.account = test_mock_values.account
    configuration.api_server = test_mock_values.api_server
    yield configuration


@pytest.fixture(name="questrade_api")
def fixture_questrade_api(tests_config):
    configuration = QuestradeAPIConfigurationPolicy()
    configuration.token = tests_config.token
    configuration.password = tests_config.password
    configuration.user = tests_config.user
    configuration.account = tests_config.account
    configuration.api_server = tests_config.api_server

    _questrade_api = QuestradeAPI(configuration=configuration)
    yield _questrade_api


@pytest.mark.unit
def test_connect(questrade_api):
    assert questrade_api.connect()

@pytest.mark.unit
def test_get_accounts(questrade_api):
    questrade_api.connect()
    assert questrade_api.get_accounts()


@pytest.mark.unit
def test_get_positions(questrade_api):
    questrade_api.connect()
    assert questrade_api.get_positions()

@pytest.mark.unit
def test_get_position_history(questrade_api):
    questrade_api.connect()
    assert questrade_api.get_position_history("43620897")

@pytest.mark.unit
def test_get_prefix_symbols(questrade_api):
    questrade_api.connect()
    assert questrade_api.get_prefix_symbols("B")
    assert questrade_api.get_prefix_symbols("C")
    assert questrade_api.get_prefix_symbols("D")
    assert questrade_api.get_prefix_symbols("E")
    assert questrade_api.get_prefix_symbols("F")
    assert questrade_api.get_prefix_symbols("G")
    assert questrade_api.get_prefix_symbols("H")
    assert questrade_api.get_prefix_symbols("I")
    assert questrade_api.get_prefix_symbols("J")
    assert questrade_api.get_prefix_symbols("K")
    assert questrade_api.get_prefix_symbols("L")
    assert questrade_api.get_prefix_symbols("M")
    assert questrade_api.get_prefix_symbols("N")
    assert questrade_api.get_prefix_symbols("O")
    assert questrade_api.get_prefix_symbols("P")
    assert questrade_api.get_prefix_symbols("Q")
    assert questrade_api.get_prefix_symbols("R")
    assert questrade_api.get_prefix_symbols("S")
    assert questrade_api.get_prefix_symbols("T")
    assert questrade_api.get_prefix_symbols("U")
    assert questrade_api.get_prefix_symbols("V")
    assert questrade_api.get_prefix_symbols("W")
    assert questrade_api.get_prefix_symbols("X")
    assert questrade_api.get_prefix_symbols("Y")
    assert questrade_api.get_prefix_symbols("Z")

@pytest.mark.unit
def test_get_all_symbols_from_files(questrade_api):
    assert questrade_api.get_all_symbols_from_files()

@pytest.mark.unit
def test_get_tradable_stocks(questrade_api):
    questrade_api.connect()
    assert questrade_api.get_tradable_stocks()


@pytest.mark.unit
def test_get_all_stocks_daily_history(questrade_api):
    questrade_api.connect()
    assert questrade_api.get_all_stocks_daily_history()


@pytest.mark.unit
def test_provision_db(questrade_api):
    assert questrade_api.provision_db_symbols_table()
    assert questrade_api.provision_db_candles_table()

@pytest.mark.unit
def test_sort_and_print_cheapest_by_price(questrade_api):
    response = questrade_api.sort_and_print_cheapest_by_price()
    assert response

@pytest.mark.unit
def test_check_strategy_one_persent_below_current(questrade_api):
    assert questrade_api.check_strategy_one_persent_below_current(52015918)

@pytest.mark.unit
def test_selenium_login(questrade_api):
    assert questrade_api.selenium_login()

@pytest.mark.unit
def test_cleanup_candles(questrade_api):
    assert questrade_api.cleanup_candles()

@pytest.mark.unit
def test_get_activities(questrade_api):
    assert questrade_api.get_activities()


@pytest.mark.unit
def test_update_symbol_today_candles(questrade_api):
    symbol = questrade_api.db_get_symbol(symbol_symbol="FEMY")
    questrade_api.update_symbol_today_candles(symbol)


@pytest.mark.unit
def test_debug_symbol_calculate_vwap_incline(questrade_api):
    symbol = questrade_api.db_get_symbol(symbol_symbol="FEMY")
    candles = questrade_api.db_get_today_candles(symbol)
    questrade_api.calculate_vwap_incline(candles)

@pytest.mark.unit
def test_calculate_vwap_incline(questrade_api):
    with open(Path(__file__).parent / "candles_sample.json", encoding="utf-8") as fh:
        candle_dicts = json.load(fh)
    candles = [Candle(dict_src) for dict_src in candle_dicts]
    assert questrade_api.calculate_vwap_incline(candles)

@pytest.mark.unit
def test_get_idle_positions(questrade_api):
    assert questrade_api.get_idle_positions()


@pytest.mark.unit
def test_generate_profit_review(questrade_api):
    """
    First week - buy small up to 1 dollar. Complete to 1 dollar
    Second week - complete to dollar.
    Third week - buy with slop < 0 and largest spread in vwap_change
    :param questrade_api:
    :return:
    """
    today = datetime.now(timezone.utc)
    if today.hour < 3:
        today -= timedelta(days=1)
    time_start = today.replace(hour=3, minute=0, second=0, microsecond=0) - timedelta(days=7)
    time_end = today.replace(hour=20, minute=0, second=0, microsecond=0) - timedelta(minutes=1)

    assert questrade_api.generate_profit_review(time_start, time_end)

@pytest.mark.unit
def test_fetch_symbols_by_max_price(questrade_api):
    assert questrade_api.fetch_symbols_by_price_range(0.001, 2)


@pytest.mark.unit
def test_selenium_open_symbol_page(questrade_api):
    questrade_api.selenium_login()
    assert questrade_api.selenium_open_symbol_page("MGIH")

@pytest.mark.unit
def test_selenium_sell_symbol(questrade_api):
    questrade_api.selenium_login()
    try:
        assert questrade_api.selenium_sell_symbol("MGIH", 1.63)
    finally:
        questrade_api.selenium_api.disconnect()

@pytest.mark.unit
def test_get_positions_without_sell_orders(questrade_api):
    assert questrade_api.get_positions_without_sell_orders()

@pytest.mark.unit
def test_update_cheap_candles_with_today_data(questrade_api):
    assert questrade_api.update_cheap_candles_with_today_data()

@pytest.mark.unit
def test_make_purchase_plan(questrade_api):
    assert questrade_api.make_purchase_plan()

@pytest.mark.unit
def test_get_positions_without_sell_orders_loop(questrade_api):
    for _ in range(60*2):
        assert questrade_api.get_positions_without_sell_orders()
        logger.info("Sleeping 60 seconds...")
        time.sleep(60)

@pytest.mark.unit
def test_update_interesting_symbols_in_ram(questrade_api):
    assert questrade_api.update_interesting_symbols_in_ram()
    assert questrade_api.update_interesting_symbols_in_ram()


@pytest.mark.unit
def test_update_ineresting_symbols_market_data(questrade_api):
    assert questrade_api.update_ineresting_symbols_market_data()

@pytest.mark.wip
def test_update_ineresting_symbols_market_data_symbol_name(questrade_api):
    assert questrade_api.update_ineresting_symbols_market_data(symbol_name="CAN")
    time.sleep(10)
    breakpoint()
    questrade_api.update_ineresting_symbols_market_data(symbol_name="CAN")


@pytest.mark.unit
def test_make_purchase_plan_helper(questrade_api):
    assert questrade_api.make_purchase_plan_helper()

@pytest.mark.unit
def test_get_trading_start_time_by_timedelta(questrade_api):
    utc_dt = datetime.now(timezone.utc)
    eastern_dt_now = utc_dt.astimezone(ZoneInfo("America/New_York"))
    ret = questrade_api.get_trading_start_time_by_timedelta(eastern_dt_now, timedelta(seconds=24*60*60))
    assert ret

@pytest.mark.unit
def test_run_the_main_loop(questrade_api):
    assert questrade_api.run_the_main_loop()

@pytest.mark.unit
def test_run_selenium_sell_routine(questrade_api):
    try:
        assert questrade_api.run_selenium_sell_routine()
    finally:
        questrade_api.selenium_api.disconnect()
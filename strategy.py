import logging
import pandas as pd
import numpy as np
import datetime as dt
from asset import *
from position import *
import abc

"""
Output information to log file in live trading environment 
"""
asset_mapping = {"OPT": OptionAsset, "STK": StockAsset}
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
STRATEGY_TYPE = {1: "Dollar_Cost_Avg", 2: "Fixed_Capital"}


class Strategy(metaclass=abc.ABCMeta):
    def __init__(self, initial_cash_, type_):
        # Strategy type
        self.strategy_type = STRATEGY_TYPE[type_]
        # Container
        self.positions = {}
        self.ticker_trading = []
        # Desired Information
        self.t_cost = 0
        self.cash_on_hand = initial_cash_
        self.cash_invested = initial_cash_
        self.market_value = 0
        self.unrealized_pnl = 0
        self.realized_pnl = 0
        self.div_accumulated = 0
        self.total_shares = 0
        self.port_value = self.market_value + self.cash_on_hand
        self.total_pnl = self.unrealized_pnl + self.realized_pnl
        self.winning_trades, self.winning_amt = 0, 0
        self.losing_trades, self.losing_amt = 0, 0

    @property
    def asset_trading(self):
        return list(set([x.type for x in self.ticker_trading]))

    @abc.abstractmethod
    def trading_rules(self, timestamp_, asset_obj, end_=None):
        pass

    def set_ticker(self, *args, asset_type_=None):
        target = args[0]
        if isinstance(target, list):
            for item in target:
                self.ticker_trading.append(item)

        if isinstance(target, str):
            self.ticker_trading.append(target)

    def place_trade(self, timestamp_, asset_obj_, new_shares_, trade_price_):
        if new_shares_ * trade_price_ > self.cash_on_hand:
            pass
            # logger.error("Time: {} - Insufficient buying power".format(timestamp_))
        else:
            ticker = asset_obj_.ticker
            if ticker in self.positions.keys():
                self.positions[ticker].update_trx_event(timestamp_, asset_obj_, new_shares_, trade_price_)
            else:
                pos = Position(asset_obj_)
                self.positions[ticker] = pos
                self.positions[ticker].update_trx_event(timestamp_, asset_obj_, new_shares_, trade_price_)
            # logger.info("Time: {} - Execute {} shares".format(timestamp_, new_shares_))
            self.cash_on_hand -= new_shares_ * trade_price_
            self.total_shares += new_shares_

    def _warm_up(self):
        pass

    def _re_setter(self):
        self.unrealized_pnl, self.realized_pnl, self.div_accumulated, self.market_value = 0, 0, 0, 0
        self.winning_trades, self.losing_trades, self.winning_amt, self.losing_amt = 0, 0, 0, 0

    def _pnl_helper(self, ticker_):
        self.unrealized_pnl += self.positions[ticker_].unrealized_pnl
        self.realized_pnl += self.positions[ticker_].realized_pnl
        self.total_pnl = self.unrealized_pnl + self.realized_pnl

    def _port_stats_helper(self, ticker_):
        self.div_accumulated += self.positions[ticker_].div_accumulated
        self.market_value += self.positions[ticker_].market_value
        self.cash_on_hand = self.cash_on_hand + self.positions[ticker_].cur_div
        self.port_value = self.cash_on_hand + self.market_value

    def _trade_stats_helper(self, ticker_):
        self.winning_trades += self.positions[ticker_].winning_trades
        self.winning_amt += self.positions[ticker_].winning_amt
        self.losing_trades += self.positions[ticker_].losing_trades
        self.losing_amt += self.positions[ticker_].losing_amt

    def _add_ticker(self, ticker_):
        self.ticker_trading.append(ticker_)

    def _update(self, timestamp_, asset_obj_):
        ticker = asset_obj_.ticker
        if ticker in self.positions.keys():
            self._re_setter()
            for k, v in self.positions.items():
                # Update Position Information
                if ticker == k:
                    self.positions[ticker].update_tick_event(timestamp_, asset_obj_)
                # Update Strategy Information
                # -- PnL --
                self._pnl_helper(ticker)
                # -- Portfolio --
                self._port_stats_helper(ticker)
                # -- Trades Stats --
                self._trade_stats_helper(ticker)
        else:
            pass


class BuyHoldStrategy(Strategy):
    def __init__(self, initial_cash, type_):
        super().__init__(initial_cash, type_)
        self.tracker = []

    def trading_rules(self, timestamp_, asset_obj_, end_=None):
        ticker, price, div = asset_obj_.ticker, asset_obj_.current_price, asset_obj_.div

        if (timestamp_.year, timestamp_.month) not in self.tracker:
            self.cash_on_hand += 400
            self.cash_invested += 400
            shares = 400 // price
            self.place_trade(timestamp_, asset_obj_, shares, price)
            self.tracker.append((timestamp_.year, timestamp_.month))

        self._update(timestamp_, asset_obj_)


class BuyHoldStrategyTwo(Strategy):
    def __int__(self, initial_cash):
        super().__init__(initial_cash)
        self.tracker = []

    def trading_rules(self, timestamp_, asset_obj, end_=None):
        pass


def main():
    print(40//23)


if __name__ == '__main__':
    main()

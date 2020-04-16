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


class Strategy(metaclass=abc.ABCMeta):
    def __init__(self, initial_cash):
        # Container
        self.positions = {}
        self.ticker_trading = []
        # Desired Information
        self.t_cost = 0
        self.cash_on_hand = initial_cash
        self.market_value = 0
        self.unrealized_pnl = 0
        self.realized_pnl = 0
        self.div_accumulated = 0
        self.total_shares = 0

    @property
    def port_value(self):
        return self.market_value + self.cash_on_hand

    @property
    def asset_trading(self):
        return list(set([x.type for x in self.ticker_trading]))

    @property
    def total_pnl(self):
        return self.unrealized_pnl + self.realized_pnl + self.t_cost

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

    def _add_ticker(self, ticker_):
        self.ticker_trading.append(ticker_)

    def _update(self, timestamp_, asset_obj_):
        ticker = asset_obj_.ticker
        if ticker in self.positions.keys():
            self.unrealized_pnl, self.realized_pnl, self.div_accumulated = 0, 0, 0
            self.market_value = 0
            for k, v in self.positions.items():
                if ticker == k:
                    self.positions[ticker].update_tick_event(timestamp_, asset_obj_)
                #TODO: Check if all those things are needed to be updated
                self.div_accumulated += self.positions[ticker].div_accumulated
                self.market_value += self.positions[ticker].market_value
                self.unrealized_pnl += self.positions[ticker].unrealized_pnl
                self.realized_pnl += self.positions[ticker].realized_pnl

        else:
            pass


class BuyHoldStrategy(Strategy):
    def __init__(self, initial_cash):
        super().__init__(initial_cash)
        self.tracker = []

    def trading_rules(self, timestamp_, asset_obj_, end_=None):
        ticker, price, div = asset_obj_.ticker, asset_obj_.current_price, asset_obj_.div

        if (timestamp_.year, timestamp_.month) not in self.tracker:
            self.place_trade(timestamp_, asset_obj_, 2, price)
            self.tracker.append((timestamp_.year, timestamp_.month))

        self._update(timestamp_, asset_obj_)


def main():
    tmp = BuyHoldStrategy(1000)
    tmp.set_ticker("AAPL", asset_type_="STK")
    print(tmp.ticker_trading)


if __name__ == '__main__':
    main()

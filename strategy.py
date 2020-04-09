import pandas as pd
import numpy as np
import datetime as dt
from asset import *
import abc

asset_mapping = {"OPT": OptionAsset, "STK": StockAsset}


class Strategy(metaclass=abc.ABCMeta):
    def __init__(self):
        self.positions = {}
        self.ticker_trading = []
        self.unrealized_pnl = 0
        self.t_cost = 0
        self.realized_pnl = 0

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
                # asset = asset_mapping[asset_type_](item)
                # self.ticker_trading.append(asset)
                self.ticker_trading.append(item)

        if isinstance(target, str):
            # asset = asset_mapping[asset_type_](target)
            # self.ticker_trading.append(asset)
            self.ticker_trading.append(target)

    def _warm_up(self):
        pass

    def _add_ticker(self, ticker_):
        self.ticker_trading.append(ticker_)


class BuyHoldStrategy(Strategy):
    def __init__(self):
        super().__init__()

    def trading_rules(self, timestamp_, aseet_obj):
        if timestamp_ == dt.datetime(2018, 1, 8, 0):
            self._add_ticker("SPY")


def main():
    tmp = BuyHoldStrategy()
    tmp.set_ticker("AAPL", asset_type_="STK")
    print(tmp.ticker_trading)

if __name__ == '__main__':
    main()

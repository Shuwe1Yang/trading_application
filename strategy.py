import pandas as pd
import numpy as np
import datetime as dt
from asset import *
from position import *
import abc

asset_mapping = {"OPT": OptionAsset, "STK": StockAsset}


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
                # asset = asset_mapping[asset_type_](item)
                # self.ticker_trading.append(asset)
                self.ticker_trading.append(item)

        if isinstance(target, str):
            # asset = asset_mapping[asset_type_](target)
            # self.ticker_trading.append(asset)
            self.ticker_trading.append(target)

    def place_trade(self, timestamp_, asset_obj_, new_shares_, trade_price_):
        ticker = asset_obj_.ticker
        if ticker in self.positions.keys():
            self.positions[ticker].update_trx_event(timestamp_, asset_obj_, new_shares_, trade_price_)
        else:
            pos = Position(asset_obj_)
            self.positions[ticker] = pos
            self.positions[ticker].update_trx_event(timestamp_, asset_obj_, new_shares_, trade_price_)

    def _warm_up(self):
        pass

    def _add_ticker(self, ticker_):
        self.ticker_trading.append(ticker_)

    def _update(self, timestamp_, asset_obj_):
        ticker = asset_obj_.ticker
        if ticker in self.positions.keys():
            self.positions[ticker].update_tick_event(timestamp_, asset_obj_)
            self.unrealized_pnl += self.positions[ticker].unrealized_pnl


class BuyHoldStrategy(Strategy):
    def __init__(self, initial_cash):
        super().__init__(initial_cash)
        self.i = 0

    def trading_rules(self, timestamp_, asset_obj_, end_=None):
        ticker, price = asset_obj_.ticker, asset_obj_.current_price
        if self.i % 5 == 0 and ticker == 'IVV' and len(self.positions.keys()) == 0:
            self.place_trade(timestamp_, asset_obj_, 1, price)
            self.total_shares += 10

        if ticker == 'TLT':
            self.i += 1
        self._update(timestamp_, asset_obj_)



def main():
    tmp = BuyHoldStrategy(10000)
    tmp.set_ticker("AAPL", asset_type_="STK")
    print(tmp.ticker_trading)

if __name__ == '__main__':
    main()

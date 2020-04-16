import numpy as np
import pandas as pd
from asset import *


class Position:
    def __init__(self, asset_obj_):
        self.trades_history = {}

        self.asset = asset_obj_
        self.shares = 0
        self.cost_basis = 0
        self.market_value = 0
        self.div_accumulated = 0
        self.unrealized_pnl = 0
        self.realized_pnl = 0
        self.t_cost = 0
        self.last_time_update = None

    @property
    def total_pnl(self):
        return self.unrealized_pnl + self.realized_pnl - self.t_cost

    def update_tick_event(self, timestamp_, asset_obj_):
        cur_price = asset_obj_.current_price
        self.last_time_update = timestamp_
        self.asset.last_price = self.asset.current_price
        self.asset.current_price = cur_price

        self.unrealized_pnl = (cur_price - self.cost_basis) * self.shares
        self.market_value = cur_price * self.shares
        if asset_obj_.type == 'STK':
            div = self.shares * asset_obj_.div
            self.div_accumulated += div

    def _process_trx(self, timestamp_, new_shares_, trade_price_, t_cost_=0):
        if new_shares_ + self.shares != 0:
            self.cost_basis = (self.cost_basis * self.shares + trade_price_ * new_shares_) / (new_shares_ + self.shares)
        else:
            self.cost_basis = 0
        self.shares += new_shares_
        self.market_value = self.shares * trade_price_
        self.t_cost += t_cost_
        self.last_time_update = timestamp_

    def open_position(self, timestamp_, asset_obj_, new_shares_, trade_price_, t_cost_=0):
        self.trades_history[timestamp_] = (asset_obj_.ticker, new_shares_, trade_price_, t_cost_)
        self._process_trx(timestamp_, new_shares_, trade_price_, t_cost_)

    def close_position(self, timestamp_, asset_obj_, new_shares_, trade_price_, t_cost_=0):
        self.trades_history[timestamp_] = (asset_obj_.ticker, new_shares_, trade_price_, t_cost_)
        self.realized_pnl += -new_shares_ * (trade_price_ - self.cost_basis) - t_cost_
        self._process_trx(timestamp_, new_shares_, trade_price_, t_cost_)

    def update_trx_event(self, timestamp_, asset_obj_, new_shares_, trade_price_, t_cost_=0):
        self.trades_history[timestamp_] = (asset_obj_.ticker, new_shares_, trade_price_, t_cost_)

        if self.shares == 0:
            self.open_position(timestamp_, asset_obj_, new_shares_, trade_price_, t_cost_)
        elif self.shares * new_shares_ > 0:
            # Size up
            self.open_position(timestamp_, asset_obj_, new_shares_, trade_price_, t_cost_)
        else:
            # Close position all or partial
            if self.shares + new_shares_ <= 0:
                remain_shares = self.shares + new_shares_
                self.close_position(timestamp_, asset_obj_, new_shares_, trade_price_, t_cost_)
                if remain_shares != 0:
                    self.open_position(timestamp_, asset_obj_, remain_shares, trade_price_, t_cost_)
            else:
                self.close_position(timestamp_, asset_obj_, new_shares_, trade_price_, t_cost_)


def main():
    stk = StockAsset('test')
    print(stk)


if __name__ == '__main__':
    main()

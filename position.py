import numpy as np
import pandas as pd
from asset import *


class Position:
    def __init__(self):
        self.id = 0
        self.shares = 0
        self.cost_basis = 0
        self.market_value = 0
        self.trades_history = {}
        self.unrealized_pnl = 0
        self.realized_pnl = 0
        self.commission = 0

    @property
    def total_pnl(self):
        return self.unrealized_pnl + self.realized_pnl

    def update_transaction(self, date_, asset_, new_shares_, trade_rice_, commission_=0):
        self.market_value += new_shares_ * trade_rice_
        self.shares += new_shares_
        self.cost_basis = self.market_value / self.shares
        self.commission += commission_
        self.trades_history[(date_.year, date_.month)] = asset_.symbol


def main():
    stk = StockAsset('test')
    print(stk)


if __name__ == '__main__':
    main()

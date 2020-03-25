import pandas as pd
import numpy as np
import datetime as dt
"""
1. Equity
2. Option
"""

class Asset(object):
    def __init__(self, symbol_):
        self.symbol = symbol_
        self.current_price = 0
        self.last_price = 0

    def __eq__(self, other):
        return self.symbol == other.symbol

class StockAsset(Asset):
    def __init__(self, symbol_):
        super().__init__(symbol_)


class OptionAsset(Asset):
    def __init__(self, symbol_, strike_, expiration_, rf_, multiplier_=100):
        super().__init__(symbol_)
        self.multiplier = multiplier_
        self.strike = strike_
        self.expiration = expiration_
        self.time_to_maturity = None
        self.rf_ = rf_

    @property
    def implied_vol(self):
        return 0

    def _d1(self, s0_):
        return (np.log(s0_/self.strike) + self.time_to_maturity * (self.rf_ + self.implied_vol ** 2/2)) / \
               (self.implied_vol * self.time_to_maturity ** 0.5)

    def _d2(self, s0_):
        return self._d1(s0_) - self.implied_vol * self.time_to_maturity ** 0.5

    def bs_price(self, s0_, ):
        pass


def main():
    pass


if __name__ == '__main__':
    main()

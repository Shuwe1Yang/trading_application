import pandas as pd
import numpy as np
import datetime as dt
from scipy.stats import norm
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
    def __init__(self, symbol_, strike_, expiration_, rf_, type_,multiplier_=100):
        super().__init__(symbol_)
        self.multiplier = multiplier_
        self.strike = strike_
        self.expiration = expiration_
        self.rf_ = rf_
        self.type = type_

    @property
    def time_to_exp(self, cur_time_=None):
        cur_time = dt.datetime.now() if cur_time_ is None else cur_time_
        return (self.expiration - cur_time).total_seconds() / (60*60*24*365)

    @property
    def implied_vol(self):
        return 0

    def _d1(self, s0_):
        return (np.log(s0_/self.strike) + self.time_to_exp * (self.rf_ + self.implied_vol ** 2/2)) / \
               (self.implied_vol * self.time_to_exp ** 0.5)

    def _d2(self, s0_):
        return self._d1(s0_) - self.implied_vol * self.time_to_exp ** 0.5

    def bs_price(self, s0_,):
        if self.type == 'C':
            return s0_ * norm(self._d1(s0_)) - self.strike * np.exp(-self.rf_ * self.time_to_exp) * norm(self._d2(s0_))
        elif self.type == 'P':
            return self.strike * np.exp(-self.rf_ * self.time_to_exp) * norm(-self._d2(s0_)) - s0_ * norm(-self._d1(s0_))
        else:
            raise ValueError("Option Type is not valid")


def main():
    pass


if __name__ == '__main__':
    main()

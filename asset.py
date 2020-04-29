import pandas as pd
import numpy as np
import datetime as dt
from scipy.stats import norm
"""
1. Equity
2. Option
"""


class Asset(object):
    def __init__(self, ticker_, cur_price_):
        self.ticker = ticker_
        self.current_price = cur_price_
        self.last_price = 0

    def __eq__(self, other):
        return self.ticker == other.ticker


class StockAsset(Asset):
    def __init__(self, ticker_, cur_price_, div_=0):
        super().__init__(ticker_, cur_price_)
        self.type = "STK"
        self.multiplier = 1
        self.div = div_


class OptionAsset(Asset):
    def __init__(self, ticker_, cur_price_, strike_, expiration_, rf_, side_, multiplier_=100):
        super().__init__(ticker_, cur_price_)
        self.type = "OPT"
        self.multiplier = multiplier_
        self.strike = strike_
        self.expiration = expiration_
        self.rf_ = rf_
        self.side = side_

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
        if self.side == 'C':
            return s0_ * norm(self._d1(s0_)) - self.strike * np.exp(-self.rf_ * self.time_to_exp) * norm(self._d2(s0_))
        elif self.side == 'P':
            return self.strike * np.exp(-self.rf_ * self.time_to_exp) * norm(-self._d2(s0_)) - s0_ * norm(-self._d1(s0_))
        else:
            raise ValueError("Option Type is not valid")


class FutureAsset(Asset):
    def __init__(self, ticker_, cur_price_, expiration_):
        super().__init__(ticker_, cur_price_)
        self.type = "FUT"
        self.multiplier = 100
        self.expiration = expiration_


def main():
    pass


if __name__ == '__main__':
    main()

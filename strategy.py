import pandas as pd
import numpy as np
from asset import *
import abc


class Strategy(metaclass=abc.ABCMeta):
    def __init__(self):
        self.positions = {}
        self.asset_trading = []
        self.total_pnl = 0
        self.total_t_cost = 0
        self.realized_pnl = 0

    @abc.abstractmethod
    def trading_rules(self):
        pass



def main():
    pass


if __name__ == '__main__':
    main()
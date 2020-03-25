import pandas as pd
import numpy as np


class Asset(object):
    def __init__(self, symbol_):
        self.id = 0
        self.symbol = symbol_
        self.current_price = 0
        self.last_price = 0

    def __eq__(self, other):
        if self.symbol == other.symbol and self.id == other.id:
            return True
        else:
            return False


class StockAsset(Asset):
    def __int__(self, symbol_):
        super().__init__(symbol_)


def main():
    tmp = StockAsset('IVV')
    print(tmp.symbol)


if __name__ == '__main__':
    main()

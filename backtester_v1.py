import configparser
from strategy import *
import datetime as dt
import pandas as pd
import numpy as np
import quandl
import yfinance as yf
import matplotlib.pyplot as plt

""" Quandl API
    def API_key(self, source_='Quandal'):
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config['{}'.format(source_)]['API_Key']

    def warm_up(self, ticker_):
        quandl.ApiConfig.api_key = self.API_key()
        data = quandl.get_table('WIKI/PRICES', ticker=['AAPL', 'MSFT'], qopts={'columns': ['ticker', 'date', 'adj_close']},
                                date={'gte': '2015-12-31', 'lte': '2016-12-31'}, paginate=True)
"""
#TODO: Add dividends feature, Function for generating backtest result


class Backtester(BuyHoldStrategy):
    def __init__(self, start_, end_, initial_cash_):
        super().__init__(initial_cash_)
        self.start, self.end = start_, end_
        self.state = None
        self.result = {"Date": [], "Total_Pnl": [], "Realized_Pnl": [], "Unrealized_Pnl": [],
                       "Total_shares": []}

    def set_up_df(self):
        self.state = len(self.ticker_trading)
        if isinstance(self.ticker_trading, list):
            if len(self.ticker_trading) > 1:
                df = yf.Tickers(self.ticker_trading).history(start=self.start, end=self.end)['Close']
            else:
                df = yf.Ticker(self.ticker_trading[0]).history(start=self.start, end=self.end)['Close'].to_frame()
                df.rename(columns={'Close': '{}'.format(self.ticker_trading[0])}, inplace=True)
            return df
        else:
            return None

    def _record_result(self, idx):
        self.result["Date"].append(idx)
        self.result["Total_Pnl"].append(self.total_pnl)
        self.result["Realized_Pnl"].append(self.realized_pnl)
        self.result["Unrealized_Pnl"].append(self.unrealized_pnl)
        self.result["Total_shares"].append(self.total_shares)

    def back_test(self):
        flag = 1
        while flag:
            df = self.set_up_df()
            iter = df.iterrows()
            for idx, row in iter:
                self._record_result(idx)
                asset_obj_lirst = [StockAsset(x, row['{}'.format(x)]) for x in row.index.tolist()]
                for item in asset_obj_lirst:
                    self.trading_rules(idx, item)

                # Handling case that strategy adding new ticker
                if self.state != len(self.ticker_trading):
                    self.state = len(self.ticker_trading)
                    self.start = (idx+dt.timedelta(days=1)).strftime("%Y-%m-%d") if isinstance(idx, pd.Timestamp) else idx
                    self.end = self.end.dt.datetime.strftime("%Y-%m-%d") if isinstance(self.end, pd.Timestamp) else self.end
                    break
                # If iterating to last row, turn the flag to 0 in order to jump out of while loop
                if (row == df.iloc[-1, :]).all():
                    flag = 0

    def get_backtest_result(self):
        plt.plot(self.result["Date"], self.result["Total_Pnl"])
        plt.grid()
        plt.show()


def main():
    """ 1. Specifying: 1. initial target ticker to trade and
                       2. Backtest time frame
                       3. Initial Capital"""
    ticker = ['IVV']#, 'TLT']
    start, end = '2008-01-01', '2020-01-01'
    initial_capital = 1000

    """ 2. Set up ticker"""
    strat = Backtester(start, end, initial_capital)
    strat.set_ticker(ticker, asset_type_="STK")

    """ 3. Start Backtest"""
    strat.back_test()
    strat.get_backtest_result()


if __name__ == '__main__':
    main()

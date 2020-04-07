import configparser
import datetime as dt
import pandas as pd
import numpy as np
import quandl
import yfinance as yf
import matplotlib.pyplot as plt


# Quandl API
    # def API_key(self, source_='Quandal'):
    #     config = configparser.ConfigParser()
    #     config.read('config.ini')
    #     return config['{}'.format(source_)]['API_Key']
    #
    # def warm_up(self, ticker_):
    #     quandl.ApiConfig.api_key = self.API_key()
    #     data = quandl.get_table('WIKI/PRICES', ticker=['AAPL', 'MSFT'], qopts={'columns': ['ticker', 'date', 'adj_close']},
    #                             date={'gte': '2015-12-31', 'lte': '2016-12-31'}, paginate=True)

class Backtester(object):
    def __init__(self, ticker_, start_, end_, initial_cash_):
        self.ticker = ticker_
        self.start, self.end = start_, end_
        self.initial_cash = initial_cash_
        self.market_value = 0
        self.port_value = self.initial_cash + self.market_value

    def _add_ticker(self, ticker_, start_, end_):
        self.start = start_.strftime("%Y-%m-%d") if isinstance(start_, pd.Timestamp) else start_
        self.end = end_.dt.datetime.strftime("%Y-%m-%d") if isinstance(end_, pd.Timestamp) else end_
        self.ticker.append(ticker_)

    def set_up_df(self):
        if isinstance(self.ticker, list):
            if len(self.ticker) > 1:
                df = yf.Tickers(self.ticker).history(start=self.start, end=self.end)['Close']
            else:
                df = yf.Ticker(self.ticker[0]).history(start=self.start, end=self.end)['Close'].to_frame()
                df.rename(columns={'Close': '{}'.format(self.ticker[0])}, inplace=True)
            return df
        else:
            return None

    def input_strategy(self):
        pass

    def back_test(self):
        flag = 1
        while flag:
            df = self.set_up_df()
            iter = df.iterrows()
            for idx, row in iter:
                print(idx, row)
                if idx == pd.Timestamp(2018, 1, 8, 0):
                    self._add_ticker("AAPL", idx+dt.timedelta(days=1), self.end)
                    break

                if (row == df.iloc[-1, :]).all():
                    flag = 0


def main():
    ticker = ['TLT', 'LQD']
    start, end = '2018-01-01', '2020-01-01'
    tmp = Backtester(ticker, start, end, 1000)
    tmp.back_test()


if __name__ == '__main__':
    main()

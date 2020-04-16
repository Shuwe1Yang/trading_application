import configparser
import quandl
import datetime as dt
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from strategy import *

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

INDEX_MAPPING = {"^GSPC": "SPX", "^NDX": "NDX100"}

class Backtester(BuyHoldStrategy):
    def __init__(self, start_, end_, initial_cash_):
        super().__init__(initial_cash_)
        self.start, self.end = start_, end_
        self.div_mode = False
        self.state = None
        self.result = {"Date": [], "Cash": [], "Total_Pnl": [], "Realized_Pnl": [], "Unrealized_Pnl": [],
                       "Total_shares": [], "Port_value": [], "Div_accumulated": [], "Market_Value": []}

    def _set_up_df(self):
        self.state = len(self.ticker_trading)
        if isinstance(self.ticker_trading, list):
            df, div_df, remain_ticker = self._other_data_helper()
            df = self._index_data_helper(df, remain_ticker)
            print(df)
            return df, div_df
        else:
            return None, None

    def _other_data_helper(self):
        symbol_list = [x for x in self.ticker_trading if '^' not in x]
        if len(symbol_list) > 1:
            df = yf.Tickers(symbol_list).history(start=self.start, end=self.end, auto_adjust=False)
            div_df = df['Dividends'] if self.div_mode else None
            df = df['Close']
        elif len(symbol_list) == 1:
            df = yf.Ticker(symbol_list[0]).history(start=self.start, end=self.end, auto_adjust=False)
            div_df = df['Dividends'].to_frame().rename(columns={'Dividends': '{}'.format(symbol_list[0])}) \
                if self.div_mode else None
            df = df['Close'].to_frame()
            df.rename(columns={'Close': '{}'.format(symbol_list[0])}, inplace=True)
        else:
            df, div_df = None, None
        remain_ticker = [x for x in self.ticker_trading if x not in symbol_list]
        return df, div_df, remain_ticker

    def _index_data_helper(self, df_, remain_ticker_):
        """
        Used to walk around bugs in yfinance library when quoting index data with other symbol
        :return: Index data frame
        """
        df_ = pd.DataFrame(columns=[INDEX_MAPPING[x] for x in remain_ticker_]) if df_ is None else df_
        if len(remain_ticker_) != 0:
            for ticker in remain_ticker_:
                sub_df = yf.Ticker(ticker).history(start=self.start, end=self.end, auto_adjust=False)['Close'].to_frame()
                sub_df.rename(columns={'Close': '{}'.format(INDEX_MAPPING[ticker])}, inplace=True)
                df_.loc[:, INDEX_MAPPING[ticker]] = sub_df.loc[:, INDEX_MAPPING[ticker]]
            return df_
        else:
            return df_

    def set_dividends_mode(self, mode_):
        self.div_mode = mode_

    def _record_result(self, idx):
        self.result["Date"].append(idx)
        self.result["Cash"].append(self.cash_on_hand)
        self.result["Total_Pnl"].append(self.total_pnl)
        self.result["Realized_Pnl"].append(self.realized_pnl)
        self.result["Unrealized_Pnl"].append(self.unrealized_pnl)
        self.result["Total_shares"].append(self.total_shares)
        self.result["Market_Value"].append(self.market_value)
        if self.div_mode:
            self.result["Div_accumulated"].append(self.div_accumulated)

    def _new_ticker_checker(self, idx):
        if self.state != len(self.ticker_trading):
            self.state = len(self.ticker_trading)
            self.start = (idx + dt.timedelta(days=1)).strftime("%Y-%m-%d") if isinstance(idx, pd.Timestamp) else idx
            self.end = self.end.dt.datetime.strftime("%Y-%m-%d") if isinstance(self.end, pd.Timestamp) else self.end
            return True
        return False

    def back_test(self):
        flag = 1
        while flag:
            df, div_df = self._set_up_df()
            iter = df.iterrows()

            for idx, row in iter:
                self._record_result(idx)
                if div_df is not None:
                    asset_obj_list = [StockAsset(x, row[x], div_df.loc[idx, x]) for x in div_df.columns.tolist()] + \
                                     [StockAsset(x, row[x]) for x in row.index.tolist() if x not in div_df.columns.tolist()]
                else:
                    asset_obj_list = [StockAsset(x, row[x]) for x in row.index.tolist()]

                """ Back testing block"""
                for item in asset_obj_list:
                    self.trading_rules(idx, item)
                """ Back testing block"""

                # Handling case that strategy adding new ticker and setting up new dataframe containing new ticker
                if self._new_ticker_checker(idx):
                    break
                # If iterating to last row, turn the flag to 0 in order to jump out of while loop
                if (row == df.iloc[-1, :]).all():
                    flag = 0

    def get_backtest_result(self):
        days_hold = (self.result["Date"][-1] - self.result["Date"][0]).days
        annual_rtn = (1 + self.result["Div_accumulated"][-1] / (self.positions['QYLD'].cost_basis*self.total_shares)) **\
                     (365/days_hold) - 1
        print("Annualized Return: {}%".format(round(annual_rtn*100, 2)))
        plt.plot(self.result["Date"], self.result["Div_accumulated"])
        # plt.plot(self.result["Date"], self.result["Market_Value"])
        plt.grid()
        plt.show()


def main():
    """ 1. Specifying: 1. initial target ticker to trade and
                       2. Backtest time frame
                       3. Initial Capital"""
    ticker = ['QYLD', '^NDX']
    start, end = '2014-01-01', '2020-01-01'
    initial_capital = 10000

    """ 2. Set up ticker"""
    strat = Backtester(start, end, initial_capital)
    strat.set_ticker(ticker, asset_type_="STK")
    strat.set_dividends_mode(mode_=True)
    """ 3. Start Backtest"""
    strat.back_test()
    strat.get_backtest_result()


if __name__ == '__main__':
    main()

import datetime as dt
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from strategy import *
from research_tools import *

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
RESULT_MAPPING = {"cash_on_hand": 0, "total_pnl": 1, "realized_pnl": 2, "unrealized_pnl": 3, "total_shares": 4,
                  "port_value": 5, "div_accumulated": 6, "market_value": 7, "cash_invested": 8,
                  "winning_trades": 9, "losing_trades": 10, "winning_amt": 11, "losing_amt": 12}


class Backtester(BuyHoldStrategy):
    def __init__(self, start_, end_, initial_cash_, type_):
        super().__init__(initial_cash_, type_)
        self.start, self.end = start_, end_
        self.is_div_mode = False
        self.state = None
        days = (dt.datetime.strptime(end_, '%Y-%m-%d') - dt.datetime.strptime(start_, '%Y-%m-%d')).days
        date_array = np.empty((days, 1), dtype=pd.Timestamp)
        result_array = np.empty((days, len(RESULT_MAPPING.keys())))
        self.result = np.concatenate((result_array, date_array), axis=1)

    def _set_up_df(self):
        self.state = len(self.ticker_trading)
        if isinstance(self.ticker_trading, list):
            df, div_df, remain_ticker = self._other_data_helper()
            df = self._index_data_helper(df, remain_ticker)
            return df, div_df
        else:
            return None, None

    def _other_data_helper(self):
        symbol_list = [x for x in self.ticker_trading if '^' not in x]
        if len(symbol_list) > 1:
            df = yf.Tickers(symbol_list).history(start=self.start, end=self.end, auto_adjust=False)
            div_df = df['Dividends'] if self.is_div_mode else None
            df = df['Close']
        elif len(symbol_list) == 1:
            df = yf.Ticker(symbol_list[0]).history(start=self.start, end=self.end, auto_adjust=False)
            div_df = df['Dividends'].to_frame().rename(columns={'Dividends': '{}'.format(symbol_list[0])}) \
                if self.is_div_mode else None
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
        self.is_div_mode = mode_

    def _record_result(self, i, idx):
        class_attr = self.__dict__
        for key in RESULT_MAPPING.keys():
            attr_value = class_attr.get(key, None)
            if not self.is_div_mode and key == "div_accumulated":
                continue
            self.result[i, RESULT_MAPPING.get(key)] = attr_value
        self.result[i, -1] = idx

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
            df_iter = df.iterrows()

            for i, item in enumerate(df_iter):
                idx, row = item
                if div_df is not None:
                    #TODO: Cost run-time here
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

                self._record_result(i, idx)

    def get_backtest_result(self):
        mask = (self.result != None).all(axis=1)
        self.result = self.result[mask, :]
        result_df = pd.DataFrame(self.result[:, 0:len(RESULT_MAPPING.keys())],
                                 index=self.result[:, -1],
                                 columns=RESULT_MAPPING.keys())

        annual_rtn = get_annualized_return(result_df, self.strategy_type)
        #TODO: more to add
        

def main():
    print("************ Buy Hold Strat: Add 1 share per month ************")

    for item in ['QQQ', 'IVV', 'QYLD']:
        """ 1. Specifying: 1. initial target ticker to trade and
                           2. Backtest time frame
                           3. Initial Capital"""
        ticker = [item]
        start, end = '2014-01-01', '2020-01-01'
        initial_capital = 1

        """ 2. Set up ticker"""
        strat = Backtester(start, end, initial_capital, 1)
        strat.set_ticker(ticker, asset_type_="STK")
        strat.set_dividends_mode(mode_=True)
        """ 3. Start Backtest"""
        strat.back_test()
        strat.get_backtest_result()


if __name__ == '__main__':
    main()

import datetime as dt
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt


INDEX_MAPPING = {"^GSPC": "SPX", "^NDX": "NDX100"}


class DataFrameGenerator(object):
    def __init__(self, ticker_list_, start_, end_, div_mode_):
        self.ticker_trading = ticker_list_
        self.start, self.end = start_, end_
        self.div_mode = div_mode_
        self.df, self.div_df = None, None

    def set_up_df(self):
        if isinstance(self.ticker_trading, list):
            df, div_df, remain_ticker = self._other_data_helper()
            df = self._index_data_helper(df, remain_ticker)
            self.df = df
            self.div_df = div_df

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


""" Some calculation function taking dictionary as input"""
#TODO: Finalize dividends strategy calculations


def get_annualized_return(date_series_, portfolio_value_series_):
    days_hold = (date_series_[-1] - date_series_[0]).days
    rtn = (1 + portfolio_value_series_[-1] / portfolio_value_series_[0]) ** (365 / days_hold) - 1
    return rtn


def get_sharpe_ratio(date_series_, portfolio_value_series, rf_):
    rtn_series = np.diff(portfolio_value_series) / portfolio_value_series[:-1]
    rtn = get_annualized_return(date_series_, portfolio_value_series)
    std = np.std(rtn_series) * np.sqrt(252)
    return (rtn - rf_) / std


def get_max_drawdown():
    pass


def main():
    # ticker = ['QYLD', '^NDX']
    # start, end = '2014-01-01', '2020-01-01'
    # tmp = DataFrameGenerator(ticker, start, end, div_mode_=False)
    # tmp.set_up_df()
    # df = tmp.df
    pass

if __name__ == '__main__':
    main()

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


def get_annualized_return(result_df_, type_):
    days_hold = (result_df_.index[-1] - result_df_.index[0]).days

    if type_ == "Dollar_Cost_Avg":
        rtn = (1 + result_df_["port_value"][-1] / result_df_["cash_invested"][-1]) ** (365 / days_hold) - 1
    elif type_ == "Fixed_Capital":
        rtn = (1 + result_df_["port_value"][-1] / result_df_["port_value"][0]) ** (365 / days_hold) - 1
    else:
        rtn = None

    return round(rtn * 100, 2)


def get_sharpe_ratio(result_df_, rf_, type_):
    rtn_series = result_df_["port_value"].pct_change().dropna()
    rtn = get_annualized_return(result_df_, type_)
    std = rtn_series.std() * np.sqrt(252)
    return (rtn - rf_) / std


def get_max_drawdown(result_df_, rolling_window_=None):
    rtn_series = result_df_["port_value"].pct_change().dropna()
    n = len(rtn_series)
    if rolling_window_ is None:
        rolling_window_ = n
    peak_series = rtn_series.rolling(window=rolling_window_, min_periods=1).max()
    return (rtn_series / peak_series - 1.0).min()


def get_winning_losing_trades_and_amount(result_df_):
    winning_trades = result_df_["winning_trades"][-1]
    avg_winning_amt = result_df_["winning_amt"][-1] / winning_trades
    losing_trades = result_df_["losing_trades"][-1]
    avg_losing_amt = result_df_["losing_amt"][-1] / losing_trades
    return winning_trades, avg_winning_amt, losing_trades, avg_losing_amt


def main():
    # ticker = ['QYLD', '^NDX']
    # start, end = '2014-01-01', '2020-01-01'
    # tmp = DataFrameGenerator(ticker, start, end, div_mode_=False)
    # tmp.set_up_df()
    # df = tmp.df
    pass

if __name__ == '__main__':
    main()

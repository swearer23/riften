from datasource.update_local_data import (
  kline_getter,
  klines_to_df
)
from strats.utils import upcross

def fetch_data(args):
  symbol, interval, end = args
  klines = kline_getter(symbol=symbol, interval=interval, limit=1000, end=end, silent=True)
  df = klines_to_df(klines)
  df['symbol'] = symbol
  df['interval'] = interval
  df['upcross_30'] = upcross(df, 'rsi_14', 30)
  return df
  
def get_active_trading(result):
  ret = []
  for df in [x for x in result if x is not None]:
    symbol = df['symbol'].iloc[0]
    interval = df['interval'].iloc[0]
    rsi_14 = df['rsi_14'].iloc[-1]
    if df['upcross_30'].iloc[-1]:
      price = df['close'].iloc[-1]
      ret.append((
        symbol, interval, rsi_14, price
      ))
  return ret

def get_trading_need_focus(result):
  ret = []
  for df in [x for x in result if x is not None]:
    symbol = df['symbol'].iloc[0]
    interval = df['interval'].iloc[0]
    rsi_14 = df['rsi_14'].iloc[-1]
    if df['rsi_14'].iloc[-1] < 30:
      ret.append((
        symbol, interval, rsi_14
      ))
  return ret

def filter_active_symbols(result):
  df_list = [x for x in result if x is not None]
  active_symbols = []
  interesting_symbols = []
  active_trading = get_active_trading(df_list)
  active_symbols += active_trading
  trading_need_focus = get_trading_need_focus(df_list)
  interesting_symbols += trading_need_focus
  return active_symbols
import os
from datasource.update_local_data import (
  kline_getter,
  klines_to_df
)
from strats.utils import upcross
from hunter.models.Symbol import ActiveSymbol
  
buy_rsi = os.environ.get('OPEN_TRADE_UPCROSS_RSI')

def fetch_data(args):
  symbol, interval, end = args
  klines = kline_getter(symbol=symbol, interval=interval, limit=1000, end=end, silent=True)
  df = klines_to_df(klines)
  # print(last_close_time <= end)
  df = df[df['close_time_ts'] <= end.timestamp() * 1000]
  df['symbol'] = symbol
  df['interval'] = interval
  df[f'upcross_{buy_rsi}'] = upcross(df, 'rsi_14', buy_rsi)
  return df, symbol
  
def get_active_symbols(result) -> list[ActiveSymbol]:
  ret = []
  for df, symbol in result:
    interval = df['interval'].iloc[0]
    rsi_14 = df['rsi_14'].iloc[-1]
    if df[f'upcross_{buy_rsi}'].iloc[-1]:
      price = df['close'].iloc[-1]
      ret.append(ActiveSymbol(
        raw_df=df,
        interval=interval,
        rsi_14=rsi_14,
        price=price,
        **symbol.__dict__
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

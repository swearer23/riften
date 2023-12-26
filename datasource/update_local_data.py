from datetime import datetime, timedelta
from binance.spot import Spot
import pandas as pd
import pandas_ta as ta
from time import sleep

final_end = datetime(2023, 12, 25, 0, 0, 0)

def klines_to_df(klines):
  cols = [
    'open_time',
    'open',
    'high',
    'low',
    'close',
    'volume',
    'close_time',
    'quote_asset_volume',
    'number_of_trades',
    'taker_buy_base_asset_volume',
    'taker_buy_quote_asset_volume',
    'ignore'
  ]
  df = pd.DataFrame(klines, columns=cols)
  df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
  df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
  df['rsi_14'] = ta.momentum.rsi(df['close'], window=14)
  return df

def klines_to_csv(klines, symbol, interval):
  filename = "{}_{}.csv".format(
    symbol,
    interval,
  )
  localdata_path = './localdata/'
  df = klines_to_df(klines)
  df.to_csv(localdata_path + filename, index=False)
  return df

def fetch_klines(symbol, interval, limit, end):
  client = Spot()
  end_str = int(end.timestamp() * 1000)
  klines = client.klines(
    symbol=symbol,
    interval=interval,
    endTime=end_str,
    limit=limit
  )

  klines = [list(map(float, kline)) for kline in klines]
  return klines
  
def kline_getter(symbol='BTCUSDT', interval='1d', limit=1000, end=final_end, silent=False):
  klines = []
  while len(klines) < limit:
    onetime_limit = limit if limit <= 1000 else 1000
    try:
      new_lines = fetch_klines(symbol, interval, limit=onetime_limit, end=end)
      klines += new_lines
      klines = sorted(klines, key=lambda kline: kline[0])
      if len(klines) < limit:
        end = datetime.fromtimestamp(klines[0][0]/1000)
      if not silent:
        print('now we have', len(klines), 'lines data for', interval, 'interval', 'symbol', symbol)
      if len(new_lines) < onetime_limit:
        print('not enough data, stop fetching')
        break
    except Exception as e:
      print('error when fetching klines')
      print('retry in 5 seconds')
      sleep(5)
  return klines

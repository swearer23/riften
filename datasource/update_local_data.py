from datetime import datetime, timedelta
from binance.spot import Spot
import pandas as pd
import pandas_ta as ta

final_end = datetime(2023, 11, 25, 0, 0, 0)

def klines_to_csv(klines, symbol, interval):
  filename = "{}_{}.csv".format(
    symbol,
    interval,
  )

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
  localdata_path = './localdata/'
  df = pd.DataFrame(klines, columns=cols)
  df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
  df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
  df['rsi_14'] = ta.momentum.rsi(df['close'], window=14)
  df.to_csv(localdata_path + filename, index=False)

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
  
def kline_getter(symbol='BTCUSDT', interval='1d', limit=1000):
  klines = []
  end = final_end
  while len(klines) < limit:
    onetime_limit = limit if limit <= 1000 else 1000
    klines += fetch_klines(symbol, interval, limit=onetime_limit, end=end)
    klines = sorted(klines, key=lambda kline: kline[0])
    if len(klines) < limit:
      end = datetime.fromtimestamp(klines[0][0]/1000)
    print('now we have ', len(klines), 'lines data')
  return klines

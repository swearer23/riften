from datetime import datetime, timedelta
from binance.spot import Spot
import pandas as pd
import pandas_ta as ta

def kline_to_csv(symbol, interval, start, end):
  client = Spot()
  localdata_path = './localdata/'
  start_str = int(start.timestamp() * 1000)
  end_str = int(end.timestamp() * 1000)
  klines = client.klines(
    symbol=symbol,
    interval=interval,
    startTime=start_str,
    endTime=end_str
  )

  klines = [list(map(float, kline)) for kline in klines]
  
  filename = "{}_{}_{}_{}.csv".format(
    symbol,
    interval,
    start.strftime('%Y%m%d%H%M%S'),
    end.strftime('%Y%m%d%H%M%S')
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

  df = pd.DataFrame(klines, columns=cols)
  df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
  df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
  df['rsi_14'] = ta.momentum.rsi(df['close'], window=14)
  df.to_csv(localdata_path + filename, index=False)

end = datetime(2023, 11, 25)
start = end - timedelta(days=365)
kline_to_csv('BTCUSDT', '1d', start, end)

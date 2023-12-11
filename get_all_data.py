from multiprocessing import Pool, cpu_count
import os
from time import sleep
from datasource.update_local_data import kline_getter, klines_to_csv
from common import get_all_symbols, intervals

DELTA = True

def process_symbol_interval(args):
  symbol, interval = args
  if DELTA:
    if os.path.exists(f'./localdata/{symbol}_{interval}.csv'):
      print(f'{symbol} {interval} already exists, skip')
      return
  try:
    klines = kline_getter(symbol=symbol, interval=interval, limit=5000)
    klines_to_csv(klines, symbol, interval)
  except Exception as e:
    print(f'error when processing {symbol} {interval}')
    print(e)
    sleep(5)
    process_symbol_interval(args)

symbols = get_all_symbols()

with Pool(cpu_count()) as p:
  p.map(
    process_symbol_interval,
    [
      (symbol, interval)
      for symbol in symbols[:20]
      for interval in intervals
    ]
  )
import os
from multiprocessing import Pool, cpu_count
from datetime import datetime
from datasource.update_local_data import kline_getter, klines_to_csv
from common import get_all_symbols
from utils import load_config

train_final_end = datetime(2023, 12, 1, 0, 0, 0)
test_final_end = datetime(2024, 1, 1, 0, 0, 0)
load_config()

def process_symbol_interval(args):
  symbol, interval, suffix = args

  if suffix == 'train':
    endtime = train_final_end
  elif suffix == 'test':
    endtime = test_final_end
  if os.path.exists(f'./localdata/{symbol}_{interval}_{suffix}.csv'):
    print(f'{symbol} {interval} already exists, skip')
    return
  klines = kline_getter(
    symbol=symbol,
    interval=interval,
    limit=5000,
    end=endtime
  )
  klines_to_csv(klines, symbol, interval, suffix=suffix)

if __name__ == '__main__':
  symbols = get_all_symbols()

  with Pool(cpu_count()) as p:
    p.map(
      process_symbol_interval,
      [
        (symbol, interval, suffix)
        for symbol in symbols
        for interval in ['5m']
        for suffix in ['train', 'test']
      ]
    )
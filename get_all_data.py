from datasource.update_local_data import kline_getter, klines_to_csv
from cli.param_setter import intervals

for interval in intervals:
  klines = kline_getter(interval=interval, limit=5000)
  klines_to_csv(klines, 'BTCUSDT', interval)
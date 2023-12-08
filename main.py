import pandas as pd
from cli.param_setter import (
  cli_set_interval,
  cli_set_mode,
  MODE
)
from datasource.update_local_data import kline_getter, klines_to_csv
from trading.trade import Trade
from trading.holdings import Holdings

def update_mode():
  interval = cli_set_interval(standalone_mode=False)
  klines = kline_getter(interval=interval, limit=2000)
  klines_to_csv(klines, 'BTCUSDT', interval)

def test_mode():
  interval = cli_set_interval(standalone_mode=False)
  path = f'./localdata/BTCUSDT_{interval}.csv'

  df = pd.read_csv(path)
  df.index = pd.to_datetime(df['open_time'])

  upcross = df[(df['rsi_14'] < 30) & (df['rsi_14'].shift(-1) > 30)]
  upcross_dt = upcross['open_time'].tolist()
  holdings = Holdings()

  previous_row = None

  for index, row in df.iterrows():
    last_order = holdings.last()
    if row['open_time'] in upcross_dt:
      if holdings.is_empty():
        holdings.append(Trade(row['open'], row['open_time']))
      
      # if last_order and last_order.is_active():
      #   last_order.close(row['open'], row['open_time'])
    if row['rsi_14'] < 30 and previous_row['rsi_14'] > 30:
      if last_order and last_order.is_active():
        last_order.close(row['open'], row['open_time'])

    if row['rsi_14'] < 70 and previous_row['rsi_14'] > 70:
      if last_order and last_order.is_active():
        last_order.close(row['open'], row['open_time'])

    if last_order and row['open'] < last_order.buy_price * 0.98:
      last_order.close(row['open'], row['open_time'])

    previous_row = row

  result_df = pd.DataFrame([x.to_dict() for x in holdings])
  print(result_df)
  print('sum profit is ', result_df['profit'].sum())

def main():
  # cli_set_interval(intervals)
  mode = cli_set_mode(standalone_mode=False)
  if mode == MODE.UPDATE.value:
    update_mode()
  elif mode == MODE.TEST.value:
    test_mode()

if __name__ == '__main__':
  main()

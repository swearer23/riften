from cli.param_setter import (
  cli_set_interval,
  cli_set_mode,
  MODE
)
from datasource.update_local_data import kline_getter, klines_to_csv
from strats.rsi import rsi_pair

def update_mode():
  interval = cli_set_interval(standalone_mode=False)
  klines = kline_getter(interval=interval, limit=2000)
  df = klines_to_csv(klines, 'UNIDOWNUSDT', interval)
  return df

def test_mode():
  interval = cli_set_interval(standalone_mode=False)
  path = f'./localdata/BTCUSDT_{interval}.csv'

  result_df = rsi_pair(path, 20, 70)
  wins = len(result_df[result_df['profit'] > 0])
  loses = len(result_df[result_df['profit'] < 0])
  print(result_df)
  print('sum profit is ', result_df['profit'].sum())
  print('win time', wins)
  print('lose time', loses)
  print('win rate', wins / len(result_df))

def main():
  # cli_set_interval(intervals)
  mode = cli_set_mode(standalone_mode=False)
  if mode == MODE.UPDATE.value:
    df = update_mode()
    print(df)
  elif mode == MODE.TEST.value:
    test_mode()

if __name__ == '__main__':
  main()

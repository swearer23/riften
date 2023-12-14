from multiprocessing import Pool, cpu_count
from datetime import datetime, timedelta
from strats.rsi import rsi_pair
import pandas as pd
from common import get_all_symbols, intervals

def test_symbol_interval(args):
  symbol, interval, close_rsi = args
  path = f'./localdata/{symbol}_{interval}.csv'

  result_df = rsi_pair(path, 30, close_rsi)
  if len(result_df) == 0:
    return {
      'symbol': symbol,
      'interval': interval,
      'sum_profit': 0,
      'wins': 0,
      'loses': 0,
      'win_rate': 0,
      'total_time_duration': 0,
      'efficiency': 0,
      'trades_per_day': 0,
      'close_rsi': 0
    }
  result_df['buy_dt'] = pd.to_datetime(result_df['buy_dt'])
  result_df['sell_dt'] = pd.to_datetime(result_df['sell_dt'])
  total_time_duration = (
    result_df['sell_dt'] - result_df['buy_dt']
  ).sum().total_seconds() / 86400 
  wins = len(result_df[result_df['profit'] > 0])
  loses = len(result_df[result_df['profit'] < 0])
  return {
    'symbol': symbol,
    'interval': interval,
    'sum_profit': result_df['profit'].sum(),
    'wins': wins,
    'loses': loses,
    'win_rate': wins / len(result_df),
    'total_time_duration': total_time_duration,
    'efficiency': result_df['profit'].sum() / total_time_duration,
    'trades_per_day': len(result_df) / total_time_duration,
    'close_rsi': close_rsi
  }

symbols = get_all_symbols()

with Pool(cpu_count()) as p:
  result = p.map(
    test_symbol_interval,
    [
      (symbol, interval, close_rsi)
      for symbol in symbols[:20]
      for interval in intervals
      for close_rsi in range(40, 90, 5)
    ]
  )

df = pd.DataFrame(result)
print('total profit', df['sum_profit'].sum())
print('win rate', df['wins'].sum() / (df['loses'].sum() + df['wins'].sum()))
print('trades', df['wins'].sum() + df['loses'].sum())
print('profit per trade', df['sum_profit'].sum() / (df['wins'].sum() + df['loses'].sum()))
df.to_csv('./results/result.csv', index=False)
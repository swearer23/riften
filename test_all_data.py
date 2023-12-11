from multiprocessing import Pool, cpu_count
from datetime import datetime, timedelta
from strats.rsi import rsi_pair
import pandas as pd
from common import get_all_symbols, intervals

def test_symbol_interval(args):
  symbol, interval = args
  path = f'./localdata/{symbol}_{interval}.csv'

  result_df = rsi_pair(path, 30, 70)
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
    'trades_per_day': len(result_df) / total_time_duration
  }

symbols = get_all_symbols()

with Pool(cpu_count()) as p:
  result = p.map(
    test_symbol_interval,
    [
      (symbol, interval)
      for symbol in symbols[:20]
      for interval in intervals
    ]
  )

df = pd.DataFrame(result)
print(df)
df.to_csv('./results/result.csv', index=False)
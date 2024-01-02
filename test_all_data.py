from utils import load_config
load_config()

import os
from multiprocessing import Pool, cpu_count
from strats.rsi import rsi_pair
import pandas as pd
from common import get_all_symbols

def test_symbol_interval(args):
  symbol, interval, close_rsi = args
  path = f'./localdata/{symbol}_{interval}_test.csv'
  buy_rsi = int(os.environ['OPEN_TRADE_UPCROSS_RSI'])
  stoploss_rsi = int(os.environ['STOP_LOSS_DOWNCROSS_RSI'])

  if not os.path.exists(path):
    return None, None
  result_df = rsi_pair(path, buy_rsi, stoploss_rsi=stoploss_rsi, takeprofit_rsi=close_rsi)
  if len(result_df) == 0:
    return None, None
  result_df['buy_dt'] = pd.to_datetime(result_df['buy_dt'])
  result_df['sell_dt'] = pd.to_datetime(result_df['sell_dt'])
  try:
    total_time_duration = (
      result_df['sell_dt'] - result_df['buy_dt']
    ).sum().total_seconds() / 86400
  except Exception as e:
    total_time_duration = 0
  wins = len(result_df[result_df['profit'] > 0])
  loses = len(result_df[result_df['profit'] < 0])
  result_df['symbol'] = symbol
  result_df['interval'] = interval
  result_df['close_rsi'] = close_rsi
  return {
    'symbol': symbol,
    'interval': interval,
    'sum_profit': result_df['profit'].sum(),
    'wins': wins,
    'loses': loses,
    'win_rate': wins / len(result_df),
    'total_time_duration': total_time_duration,
    'efficiency': result_df['profit'].sum() / total_time_duration if total_time_duration > 0 else 0,
    'trades_per_day': len(result_df) / total_time_duration if total_time_duration > 0 else 0,
    'profit_per_trade': result_df['profit'].sum() / len(result_df),
    'close_rsi': close_rsi
  }, result_df

symbols = get_all_symbols()

with Pool(cpu_count()) as p:
  result = p.map(
    test_symbol_interval,
    [
      (symbol, interval, close_rsi)
      for symbol in symbols
      for interval in ['5m'] #intervals
      for close_rsi in [65] #range(40, 90, 5)
    ]
  )

result = [x for x in result if x[0] is not None]
df = pd.DataFrame([x[0] for x in result])
print('total profit', df['sum_profit'].sum())
print('win rate', df['wins'].sum() / (df['loses'].sum() + df['wins'].sum()))
print('trades', df['wins'].sum() + df['loses'].sum())
print('profit per trade', df['sum_profit'].sum() / (df['wins'].sum() + df['loses'].sum()))
df.to_csv('./results/result.csv', index=False)
pd.concat([x[1] for x in result]).to_csv('./results/result_detail.csv', index=False)
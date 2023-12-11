import pandas as pd
from trading.trade import Trade
from trading.holdings import Holdings
from strats.utils import upcross, downcross

def rsi_pair(path, buy_rsi, sell_rsi):
  df = pd.read_csv(path)
  df.index = pd.to_datetime(df['open_time'])

  df[f'upcross_{buy_rsi}'] = upcross(df, 'rsi_14', buy_rsi)
  df[f'downcross_{buy_rsi}'] = downcross(df, 'rsi_14', buy_rsi)
  df[f'downcross_{sell_rsi}'] = downcross(df, 'rsi_14', sell_rsi)

  holdings = Holdings()

  for index, row in df.iterrows():
    last_order = holdings.last()
    if row[f'upcross_{buy_rsi}']:
      if holdings.is_empty():
        holdings.append(Trade(row['open'], row['open_time']))
      
    if row[f'downcross_{buy_rsi}']:
      if last_order and last_order.is_active():
        last_order.close(row['open'], row['open_time'])

    if row[f'downcross_{sell_rsi}']:
      if last_order and last_order.is_active():
        last_order.close(row['open'], row['open_time'])

    if last_order and row['open'] < last_order.buy_price * 0.98:
      last_order.close(row['open'], row['open_time'])

  result_df = pd.DataFrame([x.to_dict() for x in holdings])
  return result_df
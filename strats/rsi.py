import pandas as pd
from trading.trade import Trade
from trading.holdings import Holdings
from strats.utils import upcross, downcross

def trace_back(df, index):
  upbars = []
  downbars = []
  while True:
    if index < 0:
      break
    row = df.iloc[index]
    if row['close'] > row['open']:
      upbars.append(row)
    else:
      downbars.append(row)
    if len(upbars) > 0 and len(downbars) > 0 and len(upbars) == len(downbars):
      break
    index -= 1
  if len(upbars) == 0 or len(downbars) == 0:
    return 0
  up_rally_volume = sum([x['volume'] for x in upbars])
  down_rally_volume = sum([x['volume'] for x in downbars])
  up_rally_price_diff = sum([x['close'] - x['open'] for x in upbars])
  down_rally_price_diff = sum([x['open'] - x['close'] for x in downbars])
  up_rally_amount = up_rally_volume * up_rally_price_diff
  down_rally_amount = down_rally_volume * down_rally_price_diff
  surge_factor = up_rally_amount / down_rally_amount if down_rally_amount > 0 else 0
  return surge_factor

def rsi_pair(path, buy_rsi, sell_rsi):
  df = pd.read_csv(path)
  df['open_time'] = pd.to_datetime(df['open_time']) + pd.to_timedelta(8, unit='h')
  # df.index = df['open_time']
  df = df.drop_duplicates(subset=['open_time'], keep='last')

  df[f'upcross_{buy_rsi}'] = upcross(df, 'rsi_14', buy_rsi)
  df[f'downcross_{buy_rsi}'] = downcross(df, 'rsi_14', buy_rsi)
  df[f'downcross_{sell_rsi}'] = downcross(df, 'rsi_14', sell_rsi)
  df = df.sort_values(by='open_time')
  df = df.reset_index()

  holdings = Holdings()
  for index, row in df.iterrows():
    last_order = holdings.last()
    if row[f'upcross_{buy_rsi}']:
      if holdings.is_empty():
        surge_factor = trace_back(df, index)
        taker_buy_perc = row['taker_buy_base_asset_volume'] / row['volume']
        if 2 < surge_factor < 10:
          holdings.append(Trade(
            row['open'],
            row['close'],
            row['open_time'],
            taker_buy_perc,
            surge_factor=surge_factor,
            buy_rsi=row['rsi_14'],
            raw_df=df
          ))

    # if row[f'downcross_{buy_rsi}']:
    #   if last_order and last_order.is_active():
    #     last_order.close(row['close'], row['open_time'], 'downcross_buy_rsi')
    if row[f'downcross_{sell_rsi}']:
      if last_order and last_order.is_active():
        last_order.close(row['close'], row['open_time'], 'downcross_sell_rsi')

    # if (
    #   last_order
    #   and last_order.is_active()
    #   and row['close'] > last_order.buy_price * 1.01
    # ):
    #   last_order.close(row['close'], row['open_time'], 'take_profit')

    # if (
    #   last_order
    #   and last_order.is_active()
    #   and row['close'] < last_order.buy_price * 0.99
    # ):
    #   last_order.close(row['close'], row['open_time'], 'stop_loss')

  result_df = pd.DataFrame([x.to_dict() for x in holdings])
  return result_df

if __name__ == '__main__':
  rsi_pair('./localdata/BTCUSDT_5m.csv', 30, 70)
import pandas as pd
from trading.trade import Trade
from trading.holdings import Holdings
from hunter.prepare_data import process_df

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

def last_rsi_below(df, buy_rsi, row):
  sub_df = df[df[f'upcross_{buy_rsi}'] == True]
  sub_df = sub_df[sub_df['open_time'] < row['open_time']]
  return (
    row['open_time'] - sub_df['open_time'].iloc[-1]
  ).total_seconds() / 60 if len(sub_df) > 0 else None

def rsi_pair(path, buy_rsi, stoploss_rsi, takeprofit_rsi):
  df = pd.read_csv(path)
  df['open_time'] = pd.to_datetime(df['open_time']) + pd.to_timedelta(8, unit='h')
  df = df.drop_duplicates(subset=['open_time'], keep='last')
  df = process_df(df)

  df = df.sort_values(by='open_time')
  df = df.reset_index()

  holdings = Holdings()
  for index, row in df.iterrows():
    last_order = holdings.last()
    if row[f'upcross_{buy_rsi}']:
      if holdings.is_empty():
        surge_factor = trace_back(df, index)
        last_rsi_below_at = last_rsi_below(df, buy_rsi, row)
        taker_buy_perc = row['taker_buy_base_asset_volume'] / row['volume']
        # if surge_factor < 2 or surge_factor > 10:
        #   continue
        # if last_rsi_below_at and last_rsi_below_at <= 30:
        #   continue
        holdings.append(Trade(
          row['open'],
          row['close'],
          row['open_time'],
          taker_buy_perc,
          surge_factor=surge_factor,
          buy_rsi=row['rsi_14'],
          raw_df=df,
          row=row,
          assigned_buy_rsi=buy_rsi
        ))
    
    # if last_order and last_order.is_active() and last_order.trade_lasting(row) > 60:
    #   last_order.close(row['close'], row['open_time'], 'trade_lasting')

    if row[f'downcross_{stoploss_rsi}']:
      if last_order and last_order.is_active():
        last_order.close(row['close'], row['open_time'], 'stoploss_rsi')
    if row[f'downcross_{takeprofit_rsi}']:
      if last_order and last_order.is_active():
        last_order.close(row['close'], row['open_time'], 'takeprofit_rsi')

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
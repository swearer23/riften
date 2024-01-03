import os
from multiprocessing import Pool, cpu_count
import pandas as pd
import numpy as np
from strats.utils import upcross, downcross
from utils.constants import (
  buy_rsi,
  stoploss_rsi,
  takeprofit_rsi
)

def label(df: pd.DataFrame):
  ret = []
  for index, row in df.iterrows():
    if row[f'upcross_{buy_rsi}']:
      cur = index
      label = 0
      while cur < len(df):
        if df.iloc[cur][f'downcross_{takeprofit_rsi}']:
          label = 1
          break
        elif df.iloc[cur][f'downcross_{stoploss_rsi}']:
          label = 0
          break
        cur += 1
      ret.append(label)
    else:
      ret.append(-1)
  return ret

def modify_df(df: pd.DataFrame):
  df[f'upcross_{buy_rsi}'] = upcross(df, 'rsi_14', buy_rsi)
  df[f'downcross_{stoploss_rsi}'] = downcross(df, 'rsi_14', stoploss_rsi)
  df[f'downcross_{takeprofit_rsi}'] = downcross(df, 'rsi_14', takeprofit_rsi)
  df['label'] = label(df)
  df['weekday'] = pd.to_datetime(df['open_time']).dt.weekday
  df['hour'] = pd.to_datetime(df['open_time']).dt.hour
  df['minute'] = pd.to_datetime(df['open_time']).dt.minute
  df['change'] = (df['close'] - df['open']) / df['open']
  df['true_change'] = (df['high'] - df['low']) / df['open']
  df['rsi_change'] = (df['rsi_14'] - df['rsi_14'].shift(1)) / df['rsi_14'].shift(1)
  df['volume_change'] = (df['volume'] - df['volume'].shift(1)) / df['volume'].shift(1)
  df['volume_change'] = df['volume_change'].replace([np.inf, -np.inf], 0)
  df['taker_percents'] = df['taker_buy_base_asset_volume'] / df['volume']
  return df

def make_dataset(f):
  df = pd.read_csv('./localdata/' + f)
  df['symbol'] = f.split('_')[0]
  df = modify_df(df)
  return df

def init_dataset():
  files = os.listdir('./localdata')
  files = [f for f in files if f.endswith('train.csv')]

  dfs = Pool(cpu_count()).map(make_dataset, files)

  df = pd.concat(dfs)
  df.to_csv('./ml/datasets/dataset.csv', index=False)

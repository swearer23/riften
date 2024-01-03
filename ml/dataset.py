import os
from multiprocessing import Pool, cpu_count
import pandas as pd
from strats.utils import upcross, downcross

def label(df: pd.DataFrame):
  ret = []
  for index, row in df.iterrows():
    if row['upcross_open_rsi']:
      cur = index
      label = 0
      while cur < len(df):
        if df.iloc[cur]['downcross_takeprofit_rsi']:
          label = 1
          break
        elif df.iloc[cur]['downcross_open_rsi']:
          label = 0
          break
        cur += 1
      ret.append(label)
    else:
      ret.append(-1)
  return ret

def make_dataset(f):
  df = pd.read_csv('./localdata/' + f)
  df['symbol'] = f.split('_')[0]
  df['upcross_open_rsi'] = upcross(df, 'rsi_14', 30)
  df['downcross_open_rsi'] = downcross(df, 'rsi_14', 30)
  df['downcross_takeprofit_rsi'] = downcross(df, 'rsi_14', 70)
  df['label'] = label(df)
  df['weekday'] = pd.to_datetime(df['open_time']).dt.weekday
  df['hour'] = pd.to_datetime(df['open_time']).dt.hour
  df['minute'] = pd.to_datetime(df['open_time']).dt.minute
  df['change'] = (df['close'] - df['open']) / df['open']
  df['rsi_change'] = (df['rsi_14'] - df['rsi_14'].shift(1)) / df['rsi_14'].shift(1)
  return df

def init_dataset():
  files = os.listdir('./localdata')
  files = [f for f in files if f.endswith('train.csv')]

  dfs = Pool(cpu_count()).map(make_dataset, files)

  df = pd.concat(dfs)
  df.to_csv('./ml/datasets/dataset.csv', index=False)

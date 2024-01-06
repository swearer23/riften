import sys, os, time
import json
from multiprocessing import Process, Queue
from datetime import datetime
import pandas as pd
from ml.dataset import init_dataset
from ml.train import train
from ml.lgb import train as lgb_train
from ml.constants import HyperParams
from test_all_data import run

optimize_file_apth = './results/optimization.csv'
break_point_file_path = './.breakpoint'

def run_test(model, epoch, loss):
  result = run(model)
  result['epoch'] = epoch
  result['loss'] = loss
  result['model'] = model
  result = {
    **result,
    **HyperParams.json()
  }
  df = pd.DataFrame([result])
  print(df)
  if os.path.exists(optimize_file_apth):
    df.to_csv(optimize_file_apth, mode='a', header=False, index=False)
  else:
    df.to_csv(optimize_file_apth, index=False)

def optimize(interval, breakpoint=None):
  if breakpoint is None and os.path.exists(optimize_file_apth):
    os.remove(optimize_file_apth)
  HyperParams.init()
  combinations = [
    (lookback, num_lstm_layers, hidden_size)
    for lookback in [12, 30, 60]
    for num_lstm_layers in [2, 4, 6]
    for hidden_size in [64, 128, 256]
  ]
  epoch = 0
  model_path = None
  if breakpoint is not None:
    combinations = combinations[combinations.index((
      breakpoint['lookback'],
      breakpoint['num_lstm_layers'],
      breakpoint['hidden_size']
    )):]
    epoch = breakpoint['epoch']
    model_path = breakpoint['path']
  for lookback, num_lstm_layers, hidden_size in combinations:
    HyperParams.set('lookback', lookback)
    HyperParams.set('num_lstm_layers', num_lstm_layers)
    HyperParams.set('hidden_size', hidden_size)
    is_checkpoint = True
    while is_checkpoint:
      q = Queue()
      p = Process(target=train, args=(q, model_path))
      p.start()
      p.join()
      is_checkpoint, model_path, loss = q.get()
      p = Process(target=run_test, args=(model_path, epoch, loss))
      p.start()
      p.join()
      epoch += HyperParams.load('epoch_step')
      if interval is not None:
        print('===============sleep================')
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        time.sleep(interval)
        write_break_point({
          'lookback': lookback,
          'num_lstm_layers': num_lstm_layers,
          'hidden_size': hidden_size,
          'epoch': epoch,
          'path': model_path
        })
    epoch = 0
    model_path = None
  print('===============done================')
  print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def write_break_point(breakpoint):
  with open(break_point_file_path, 'w') as f:
    f.write(json.dumps(breakpoint, indent=2, ensure_ascii=False))

def get_break_point():
  if not os.path.exists(break_point_file_path):
    return None
  else:
    with open(break_point_file_path, 'r') as f:
      try:
        breakpoint = json.loads(f.read())
        return breakpoint
      except:
        return None

if __name__ == '__main__':
  argv = sys.argv
  task = argv[1]
  if task == 'ds':
    init_dataset()
  elif task == 'train':
    train()
  elif task == 'lgb':
    lgb_train()
  elif task == 'optimize':
    breakpoint = get_break_point()
    if breakpoint:
      print('===============breakpoint================')
      print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
      print(breakpoint)
      lookback = breakpoint['lookback']
      num_lstm_layers = breakpoint['num_lstm_layers']
      hidden_size = breakpoint['hidden_size']
      HyperParams.set('lookback', lookback)
      HyperParams.set('num_lstm_layers', num_lstm_layers)
      HyperParams.set('hidden_size', hidden_size)
    interval = int(argv[2])
    optimize(interval, breakpoint)
import sys, os
from multiprocessing import Process, Queue
import pandas as pd
from ml.dataset import init_dataset
from ml.train import train
from ml.lgb import train as lgb_train
from ml.constants import HyperParams
from test_all_data import run

def run_test(model, epoch, loss):
  filepath = './results/optimization.csv'
  result = run(model)
  result['epoch'] = epoch
  result['loss'] = loss
  result = {
    **result,
    **HyperParams.json()
  }
  df = pd.DataFrame([result])
  if os.path.exists(filepath):
    df.to_csv(filepath, mode='a', header=False, index=False)
  else:
    df.to_csv(filepath, index=False)

def optimize():
  combinations = [
    (lookback, num_lstm_layers, hidden_size)
    for lookback in [12, 30, 60]
    for num_lstm_layers in [2, 4, 6]
    for hidden_size in [64, 128, 256]
  ]
  for lookback, num_lstm_layers, hidden_size in combinations:
    HyperParams.set('lookback', lookback)
    HyperParams.set('num_lstm_layers', num_lstm_layers)
    HyperParams.set('hidden_size', hidden_size)
    epoch = 0
    is_checkpoint = True
    model_path = None
    while is_checkpoint:
      print(pd.DataFrame([{
        'epoch': epoch,
        **HyperParams.json(),
      }]))
      q = Queue()
      p = Process(target=train, args=(q, model_path))
      p.start()
      p.join()
      is_checkpoint, model_path, loss = q.get()
      p = Process(target=run_test, args=(model_path, epoch, loss))
      p.start()
      p.join()
      epoch += HyperParams.load('epoch_step')

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
    optimize()
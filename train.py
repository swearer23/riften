import sys
from ml.dataset import init_dataset
from ml.train import train
from ml.lgb import train as lgb_train

if __name__ == '__main__':
  argv = sys.argv
  task = argv[1]
  if task == 'ds':
    init_dataset()
  elif task == 'train':
    train()
  elif task == 'lgb':
    lgb_train()
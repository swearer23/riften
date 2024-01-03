import sys
from ml.dataset import init_dataset
from ml.train import train

if __name__ == '__main__':
  argv = sys.argv
  task = argv[1]
  if task == 'ds':
    init_dataset()
  elif task == 'train':
    train()
import json

batch_size = 1024
learning_rate = 1e-4
num_classes = 2
num_lstm_layers = 4
num_epochs = 10
lookback = 12
cols = [
  'rsi_14', 'change', 'rsi_change',
  'open', 'high', 'low', 'close',
  'volume_change', 'volume',
  'number_of_trades', 'taker_percents',
  'weekday', 'hour', 'minute',
  'label'
]
hidden_size = 128
epoch_step = 1000
min_loss_limit = 1e-7

class HyperParams:
  filepath = './.hyperparams.json'

  @staticmethod
  def init():
    with open(HyperParams.filepath, 'w') as f:
      json.dump(HyperParams.default(), f)

  @staticmethod
  def load(key):
    with open(HyperParams.filepath, 'r') as f:
      data = json.load(f)
      return data.get(key, HyperParams.default()[key])
    
  @staticmethod
  def set(key, value):
    with open(HyperParams.filepath, 'r') as f:
      data = json.load(f)
      data[key] = value
    with open(HyperParams.filepath, 'w') as f:
      json.dump(data, f)

  @staticmethod
  def default():
    return {
      'learning_rate': learning_rate,
      'num_lstm_layers': num_lstm_layers,
      'lookback': lookback,
      'hidden_size': hidden_size,
      'epoch_step': epoch_step,
    }
  
  @staticmethod
  def json():
    with open(HyperParams.filepath, 'r') as f:
      return {
        **HyperParams.default(),
        **json.load(f)
      }
batch_size = 2048
learning_rate = 1e-4
num_classes = 2
num_epochs = 1000
lookback = 30
cols = [
  'rsi_14', 'change', 'rsi_change',
  # 'volume_change', 'volume',
  # 'weekday', 'hour', 'minute',
  'label'
]
hidden_size = 128 # 假设隐藏层大小为10
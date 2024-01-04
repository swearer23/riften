import torch
from torch import nn
from ml.constants import num_lstm_layers

class LSTMClassifier(nn.Module):
  def __init__(self, input_size, hidden_size, num_classes):
    super(LSTMClassifier, self).__init__()
    self.hidden_size = hidden_size
    self.num_layers = num_lstm_layers
    self.lstm = nn.LSTM(input_size, hidden_size, num_lstm_layers, batch_first=True)
    self.fc = nn.Linear(hidden_size, num_classes)
  
  def forward(self, x):
    h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
    c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
    
    out, _ = self.lstm(x, (h0, c0))
    out = self.fc(out[:, -1, :])  # 取序列最后一个时间步的输出作为分类器的输入
    return out
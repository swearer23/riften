import torch
from torch import nn

class MultiDimLinearClassifier(nn.Module):
  def __init__(self, input_size, hidden_size):
    super(MultiDimLinearClassifier, self).__init__()
    self.fc1 = nn.Linear(input_size, hidden_size)  # 输入特征维度为 input_size，输出特征维度为 hidden_size
    self.fc2 = nn.Linear(hidden_size, 1)  # 输入特征维度为 input_size，输出为1（二分类）

  def forward(self, x):
    x = torch.sigmoid(self.fc1(x))
    return torch.sigmoid(self.fc2(x))  # 使用 sigmoid 激活函数进行二分类
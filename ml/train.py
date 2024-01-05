import os
from multiprocessing import Pool, cpu_count
from functools import lru_cache
import pandas as pd
import torch
from torch import nn, Tensor
import numpy as np
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from ml.LSTMModel import LSTMClassifier
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from ml.constants import HyperParams, cols, batch_size, num_classes, min_loss_limit

class MultivariateTimeSeriesDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

def trace_back_set(df: pd.DataFrame, idx):
  lookback = HyperParams.load('lookback')
  if idx >= lookback:
    section = df.iloc[idx - lookback:idx]
    if len(section) != len(section.dropna()):
      return None
    return section
  else:
    return None
  
def standardize(df: pd.DataFrame):
  scaler = StandardScaler()
  # scaler = MinMaxScaler()
  for col in df.columns:
    df[col] = scaler.fit_transform(df[col].values.reshape(-1, 1)).reshape(-1)
  
  return df

def split_symbol(group):
  X = []
  Y = []
  group = group.sort_values(by=['open_time'])
  group = group[cols]
  group = group.reset_index(drop=True)
  for idx, row in group.iterrows():
    if row['label'] != -1:
      traceback = trace_back_set(group, idx)
      if traceback is None:
        continue
      Y.append(row['label'])
      traceback = traceback.dropna()
      traceback = traceback.drop(columns=['label'])
      traceback = standardize(traceback)
      X.append(traceback.values)
  return X, Y

@lru_cache(maxsize=1)
def split():
  data = pd.read_csv('./ml/datasets/dataset.csv')
  # print(data.columns)
  # exit()
  X = []
  Y = []
  with Pool(cpu_count()) as p:
    result = p.map(split_symbol, [x for _, x in data.groupby('symbol')])
    p.close()
    p.join()
  for x, y in result:
    X = X + x
    Y = Y + y
  return np.array(X), np.array(Y)

def test_model(model, test_loader, device):
  # 评估模型
  model.eval()
  with torch.no_grad():
    correct = 0
    total = 0
    for batch in test_loader:
      inputs, labels = batch
      inputs, labels = inputs.to(device), labels.to(device)
      outputs = model(inputs)
      predicted = outputs.argmax(dim=1)
      total += labels.size(0)
      correct += (predicted == labels).sum().item()

  accuracy = correct / total
  print(f"Test Accuracy: {accuracy}")

def run_epoch(model, train_loader, test_loader) -> Tensor:
  criterion = nn.CrossEntropyLoss()
  optimizer = torch.optim.Adam(model.parameters(), lr=HyperParams.load('learning_rate'))
  device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
  model.to(device)
  epoch_step = HyperParams.load('epoch_step')
  for epoch in range(epoch_step):
    model.train()
    for batch in train_loader:
      inputs, labels = batch
      inputs, labels = inputs.to(device), labels.to(device)
      optimizer.zero_grad()
      outputs = model(inputs)
      loss = criterion(outputs, labels)
      loss.backward()
      optimizer.step()
    if (epoch + 1) % 100 == 0:
      print(f"Epoch {epoch + 1} Loss: {loss}")
      test_model(model, test_loader, device)
    if loss < min_loss_limit:
      break
  return loss

def define_model(input_size):
  hidden_size = HyperParams.load('hidden_size')
  # model = MultiDimLinearClassifier(input_size, hidden_size)
  model = LSTMClassifier(input_size, hidden_size, num_classes)
  return model

def load_checkpoint(num_features, checkpoint_path=None):
  path = './ml/models/checkpoint.pth' if checkpoint_path is None else checkpoint_path
  if not os.path.exists(path):
    return None
  model = define_model(num_features)
  model.load_state_dict(torch.load(path))
  return model

def train(queue=None, checkpoint_path=None):
  x, y = split()
  X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
  # 将数据转换为PyTorch张量
  X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
  X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
  y_train_tensor = torch.tensor(y_train, dtype=torch.long)
  y_test_tensor = torch.tensor(y_test, dtype=torch.long)
  train_dataset = MultivariateTimeSeriesDataset(X_train_tensor, y_train_tensor)
  test_dataset = MultivariateTimeSeriesDataset(X_test_tensor, y_test_tensor)
  train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
  test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
  checkpoint = load_checkpoint(X_train.shape[2], checkpoint_path)
  if checkpoint is not None:
    model = checkpoint
  else:
    model = define_model(X_train.shape[2])
  # 训练模型
  loss = run_epoch(model, train_loader, test_loader)
  loss = loss.item()

  ts = pd.Timestamp.now().timestamp()
  path = f'./ml/models/checkpoint_{ts}.pth'
  if loss > min_loss_limit:
    torch.save(model.state_dict(), path)
    torch.cuda.empty_cache()
    if queue is not None:
      queue.put((True, path, loss))
    return True, path, loss
  else:
    # 保存模型
    torch.save(model.state_dict(), path)
    torch.cuda.empty_cache()
    if queue is not None:
      queue.put((False, path, loss))
    return False, None, loss
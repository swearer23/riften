import lightgbm as lgb
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from ml.train import split
from ml.constants import cols, HyperParams

def reshape_row(df, index):
  lookback = HyperParams.load('lookback')
  columns = [col for col in cols if col != 'label']
  input = df[columns].iloc[index - lookback:index]
  input = input.dropna()
  if len(input) < lookback:
    return None
  input = input.values.reshape(-1)
  return input

def train():
  X, Y = split()
  X = X.reshape(X.shape[0], -1)
  X_train, X_valid, y_train, y_valid = train_test_split(X, Y, test_size=0.2, random_state=42)

  train_data = lgb.Dataset(X_train, label=y_train)
  valid_data = lgb.Dataset(X_valid, label=y_valid, reference=train_data)
  # train_data = lgb.Dataset(X, label=Y)

  # 训练模型
  model = LGBMClassifier(
    boosting_type='gbdt',
    objective='binary',
    metric='binary_error',
    num_leaves=100,
    n_estimators=500,
    learning_rate=0.001,
    feature_fraction=0.8,
    bagging_fraction=0.8,
    bagging_freq=5,
    verbose=0,
  )
  model = lgb.train(
    model.get_params(),
    train_data,
    num_boost_round=10000,
    valid_sets=[valid_data],
  )

  model.save_model('./ml/models/lgb.model')
  # Getting evaluation results
  evals_result = model.best_score
  print("Validation binary_error:", evals_result['valid_0']['binary_error'])
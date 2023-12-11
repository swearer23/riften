def upcross(df, column, value):
  df = df.copy()
  # if n > value and n-1 <= value set new column to 1, else 0
  df[f'upcross_{value}'] = (df[column] > value) & (df[column].shift(1) <= value)
  return df[f'upcross_{value}'].values.tolist()

def downcross(df, column, value):
  df = df.copy()
  # if n < value and n-1 >= value set new column to 1, else 0
  df[f'downcross_{value}'] = (df[column] < value) & (df[column].shift(1) >= value)
  return df[f'downcross_{value}'].values

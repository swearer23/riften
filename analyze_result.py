import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
path = './results/result.csv'
df = pd.read_csv(path)

most_profit_param = []
most_winrate_param = []

group_by_interval = df.groupby('interval')
for interval, group in group_by_interval:
  group_by_symbol = group.groupby('symbol')
  for symbol, sub_group in group_by_symbol:
    most_profit_param.append({
      'symbol': symbol,
      'interval': interval,
      'close_rsi': sub_group['close_rsi'].iloc[sub_group['sum_profit'].argmax()],
    })
    most_winrate_param.append({
      'symbol': symbol,
      'interval': interval,
      'close_rsi': sub_group['close_rsi'].iloc[sub_group['win_rate'].argmax()],
    })

most_profit_param_df = pd.DataFrame(most_profit_param)
most_winrate_param_df = pd.DataFrame(most_winrate_param)

print('most profit params')
print(most_profit_param_df[['symbol', 'interval', 'close_rsi']])

count_data = most_winrate_param_df.groupby(['interval', 'close_rsi']).size().reset_index(name='count')

sns.scatterplot(data=count_data, x='interval', y='close_rsi', size='count', sizes=(20, 200))

plt.title('most win rate params')
plt.xlabel('close_rsi')
plt.ylabel('interval')

plt.show()
# print('most winrate params')
# print(most_winrate_param_df[['symbol', 'interval', 'close_rsi']])
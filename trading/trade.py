from datetime import datetime

class Trade:
  def __init__(self, stoploss_price, price, dt, taker_buy_perc, trade_cash=10000, **kwargs) -> None:
    self.stoploss_price = stoploss_price
    self.buy_price = price
    self.buy_dt = dt
    self.sell_price = 0
    self.sell_dt = None
    self.closed = False
    self.profit = 0
    self.price_diff = 0
    self.trade_cash = trade_cash
    self.close_type = None
    self.surge_factor = kwargs.get('surge_factor')
    self.taker_buy_perc = taker_buy_perc
    self.buy_rsi = kwargs.get('buy_rsi')
    self.df = kwargs.get('raw_df')
    self.assigned_buy_rsi = kwargs.get('assigned_buy_rsi')
    self.trade_row = kwargs.get('row')

  def close(self, price, dt, close_type):
    self.sell_price = price
    self.sell_dt = dt
    self.closed = True
    position = self.trade_cash / self.buy_price
    self.profit = (self.sell_price - self.buy_price) * position
    self.price_diff = self.sell_price - self.buy_price
    self.close_type = close_type

  def is_active(self):
    return self.closed == False
  
  def trade_lasting(self, curr):
    return (curr['open_time'] - self.buy_dt).total_seconds() / 60
  
  def last_rsi_below(self):
    sub_df = self.df[self.df[f'upcross_{self.assigned_buy_rsi}'] == True]
    sub_df = sub_df[sub_df['open_time'] < self.trade_row['open_time']]
    return (
      self.buy_dt - sub_df['open_time'].iloc[-1]
    ).total_seconds() / 60 if len(sub_df) > 0 else None
  
  def __repr__(self) -> str:
    return self.to_dict().__repr__()
  
  def to_dict(self):
    # duration in minutes
    duration = (self.sell_dt - self.buy_dt).total_seconds() / 60 if self.sell_dt else None
    holding_df = self.df[(
      self.df['open_time'] >= self.buy_dt
    ) & (
      self.df['open_time'] <= self.sell_dt if self.sell_dt else True
    )]
    holding_df = holding_df.reset_index()
    holding_length = len(holding_df)
    holding_above = len(holding_df[holding_df['close'] > self.buy_price])
    holding_below = len(holding_df[holding_df['close'] < self.buy_price])
    holding_above_perc = holding_above / holding_length if holding_length > 0 else None
    holding_below_perc = holding_below / holding_length if holding_length > 0 else None
    highest_profit = (holding_df['close'].max() - self.buy_price) / self.buy_price * 100
    highest_profit_index = holding_df['close'].idxmax()
    if holding_below > 0:
      first_below_optime = holding_df[holding_df['close'] < self.buy_price]['open_time'].iloc[0]
      first_below_index = (first_below_optime - self.buy_dt).total_seconds() / 300
    else:
      first_below_index = -1
    return {
      'buy_price': self.buy_price,
      'buy_dt': self.buy_dt,
      'sell_price': self.sell_price,
      'sell_dt': self.sell_dt,
      'profit': self.profit,
      'price_diff': self.price_diff,
      'close_type': self.close_type,
      'surge_factor': self.surge_factor,
      'taker_buy_per_trade': self.taker_buy_perc,
      'buy_rsi': self.buy_rsi,
      'duration': duration,
      'holding_length': holding_length,
      'holding_above_perc': holding_above_perc,
      'holding_below_perc': holding_below_perc,
      'highest_profit': highest_profit,
      'first_below_index': first_below_index,
      'highest_profit_index': highest_profit_index,
      'last_rsi_below': self.last_rsi_below()
    }

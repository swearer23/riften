class Trade:
  def __init__(self, price, dt, trade_cash=10000) -> None:
    self.buy_price = price
    self.buy_dt = dt
    self.sell_price = 0
    self.sell_dt = None
    self.closed = False
    self.profit = 0
    self.price_diff = 0
    self.trade_cash = trade_cash
    self.close_type = None

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
  
  def __repr__(self) -> str:
    return self.to_dict().__repr__()
  
  def to_dict(self):
    return {
      'buy_price': self.buy_price,
      'buy_dt': self.buy_dt,
      'sell_price': self.sell_price,
      'sell_dt': self.sell_dt,
      'profit': self.profit,
      'price_diff': self.price_diff,
      'close_type': self.close_type,
    }
